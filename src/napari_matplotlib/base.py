import os
from pathlib import Path
from typing import List, Optional, Tuple

import napari
from matplotlib.axes import Axes
from matplotlib.backends.backend_qtagg import (
    FigureCanvas,
    NavigationToolbar2QT,
)
from matplotlib.figure import Figure
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QLabel, QVBoxLayout, QWidget

from .util import Interval, from_napari_css_get_size_of

__all__ = ["BaseNapariMPLWidget", "NapariMPLWidget"]


class BaseNapariMPLWidget(QWidget):
    """
    Widget containing Matplotlib canvas and toolbar themed to match napari.

    This creates a single FigureCanvas, which contains a single
    `~matplotlib.figure.Figure`, and an associated toolbar. Both of these
    are customised to match the visual style of the main napari window.
    It is not responsible for creating any Axes, because different
    widgets may want to implement different subplot layouts.

    See Also
    --------
    NapariMPLWidget : A child class that also contains helpful attributes and
        methods for working with napari layers.
    """

    def __init__(
        self,
        napari_viewer: napari.Viewer,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent=parent)
        self.viewer = napari_viewer

        self.canvas = FigureCanvas()

        self.canvas.figure.patch.set_facecolor("none")
        self.canvas.figure.set_layout_engine("constrained")
        self.toolbar = NapariNavigationToolbar(
            self.canvas, parent=self
        )  # type: ignore[no-untyped-call]
        self._replace_toolbar_icons()
        # callback to update when napari theme changed
        # TODO: this isn't working completely (see issue #140)
        # most of our styling respects the theme change but not all
        self.viewer.events.theme.connect(self._on_theme_change)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.canvas)

    @property
    def figure(self) -> Figure:
        """Matplotlib figure."""
        return self.canvas.figure

    def add_single_axes(self) -> None:
        """
        Add a single Axes to the figure.

        The Axes is saved on the ``.axes`` attribute for later access.
        """
        self.axes = self.figure.subplots()
        self.apply_napari_colorscheme(self.axes)

    def apply_napari_colorscheme(self, ax: Axes) -> None:
        """Apply napari-compatible colorscheme to an Axes."""
        # get the foreground colours from current theme
        theme = napari.utils.theme.get_theme(self.viewer.theme, as_dict=False)
        fg_colour = theme.foreground.as_hex()  # fg is a muted contrast to bg
        text_colour = theme.text.as_hex()  # text is high contrast to bg

        # changing color of axes background to transparent
        ax.set_facecolor("none")

        # changing colors of all axes
        for spine in ax.spines:
            ax.spines[spine].set_color(fg_colour)

        ax.xaxis.label.set_color(text_colour)
        ax.yaxis.label.set_color(text_colour)
        # ax.set_xlabel(ax.get_xlabel, color=text_colour)

        # changing colors of axes labels
        ax.tick_params(axis="x", colors=text_colour)
        ax.tick_params(axis="y", colors=text_colour)

    def _on_theme_change(self) -> None:
        """Update MPL toolbar and axis styling when `napari.Viewer.theme` is changed.

        Note:
            At the moment we only handle the default 'light' and 'dark' napari themes.
        """
        self._replace_toolbar_icons()
        if self.figure.gca():
            self.apply_napari_colorscheme(self.figure.gca())

    def _theme_has_light_bg(self) -> bool:
        """
        Does this theme have a light background?

        Returns
        -------
        bool
            True if theme's background colour has hsl lighter than 50%, False if darker.
        """
        theme = napari.utils.theme.get_theme(self.viewer.theme, as_dict=False)
        _, _, bg_lightness = theme.background.as_hsl_tuple()
        return bg_lightness > 0.5

    def _get_path_to_icon(self) -> Path:
        """
        Get the icons directory (which is theme-dependent).

        Icons modified from
        https://github.com/matplotlib/matplotlib/tree/main/lib/matplotlib/mpl-data/images
        """
        icon_root = Path(__file__).parent / "icons"
        if self._theme_has_light_bg():
            return icon_root / "black"
        else:
            return icon_root / "white"

    def _replace_toolbar_icons(self) -> None:
        """
        Modifies toolbar icons to match the napari theme, and add some tooltips.
        """
        icon_dir = self._get_path_to_icon()
        for action in self.toolbar.actions():
            text = action.text()
            if text == "Pan":
                action.setToolTip(
                    "Pan/Zoom: Left button pans; Right button zooms; "
                    "Click once to activate; Click again to deactivate"
                )
            if text == "Zoom":
                action.setToolTip(
                    "Zoom to rectangle; Click once to activate; "
                    "Click again to deactivate"
                )
            if len(text) > 0:  # i.e. not a separator item
                icon_path = os.path.join(icon_dir, text + ".png")
                action.setIcon(QIcon(icon_path))


class NapariMPLWidget(BaseNapariMPLWidget):
    """
    Widget containing a Matplotlib canvas and toolbar.

    In addition to ``BaseNapariMPLWidget``, this class handles callbacks
    to automatically update figures when the layer selection or z-step
    is changed in the napari viewer. To take advantage of this sub-classes
    should implement the ``clear()`` and ``draw()`` methods.

    When both the z-step and layer selection is changed, ``clear()`` is called
    and if the number a type of selected layers are valid for the widget
    ``draw()`` is then called. When layer selection is changed ``on_update_layers()``
    is also called, which can be useful e.g. for updating a layer list in a
    selection widget.

    Attributes
    ----------
    viewer : `napari.Viewer`
        Main napari viewer.
    layers : `list`
        List of currently selected napari layers.

    See Also
    --------
    BaseNapariMPLWidget : The parent class of this widget. Contains helpful methods
        for creating and working with the Matplotlib figure and any axes.
    """

    #: Number of layers taken as input
    n_layers_input = Interval(None, None)
    #: Type of layer taken as input
    input_layer_types: Tuple[napari.layers.Layer, ...] = (napari.layers.Layer,)

    def __init__(
        self,
        napari_viewer: napari.viewer.Viewer,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(napari_viewer=napari_viewer, parent=parent)
        self._setup_callbacks()
        self.layers: List[napari.layers.Layer] = []

        helper_text = self.n_layers_input._helper_text
        if helper_text is not None:
            self.layout().insertWidget(0, QLabel(helper_text))

    @property
    def n_selected_layers(self) -> int:
        """
        Number of currently selected layers.
        """
        return len(self.layers)

    @property
    def current_z(self) -> int:
        """
        Current z-step of the napari viewer.
        """
        return self.viewer.dims.current_step[0]

    def _setup_callbacks(self) -> None:
        """
        Sets up callbacks.

        Sets up callbacks for when:
        - Layer selection is changed
        - z-step is changed
        """
        # z-step changed in viewer
        self.viewer.dims.events.current_step.connect(self._draw)
        # Layer selection changed in viewer
        self.viewer.layers.selection.events.changed.connect(
            self._update_layers
        )

    def _update_layers(self, event: napari.utils.events.Event) -> None:
        """
        Update the ``layers`` attribute with currently selected layers and re-draw.
        """
        self.layers = list(self.viewer.layers.selection)
        self.layers = sorted(self.layers, key=lambda layer: layer.name)
        self.on_update_layers()
        self._draw()

    def _draw(self) -> None:
        """
        Clear current figure, check selected layers are correct, and draw new
        figure if so.
        """
        self.clear()
        if self.n_selected_layers in self.n_layers_input and all(
            isinstance(layer, self.input_layer_types) for layer in self.layers
        ):
            self.draw()
        self.canvas.draw()

    def clear(self) -> None:
        """
        Clear any previously drawn figures.

        This is a no-op, and is intended for derived classes to override.
        """

    def draw(self) -> None:
        """
        Re-draw any figures.

        This is a no-op, and is intended for derived classes to override.
        """

    def on_update_layers(self) -> None:
        """
        Called when the selected layers are updated.

        This is a no-op, and is intended for derived classes to override.
        """


class NapariNavigationToolbar(NavigationToolbar2QT):
    """Custom Toolbar style for Napari."""

    def __init__(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        self.setIconSize(
            from_napari_css_get_size_of(
                "QtViewerPushButton", fallback=(28, 28)
            )
        )

    def _update_buttons_checked(self) -> None:
        """Update toggle tool icons when selected/unselected."""
        super()._update_buttons_checked()
        icon_dir = self.parentWidget()._get_path_to_icon()

        # changes pan/zoom icons depending on state (checked or not)
        if "pan" in self._actions:
            if self._actions["pan"].isChecked():
                self._actions["pan"].setIcon(
                    QIcon(os.path.join(icon_dir, "Pan_checked.png"))
                )
            else:
                self._actions["pan"].setIcon(
                    QIcon(os.path.join(icon_dir, "Pan.png"))
                )
        if "zoom" in self._actions:
            if self._actions["zoom"].isChecked():
                self._actions["zoom"].setIcon(
                    QIcon(os.path.join(icon_dir, "Zoom_checked.png"))
                )
            else:
                self._actions["zoom"].setIcon(
                    QIcon(os.path.join(icon_dir, "Zoom.png"))
                )
