import os
from pathlib import Path
from typing import List, Tuple

import napari
from matplotlib.axes import Axes
from matplotlib.backends.backend_qtagg import (
    FigureCanvas,
    NavigationToolbar2QT,
)
from matplotlib.figure import Figure
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QVBoxLayout, QWidget

from .util import Interval, from_napari_css_get_size_of

# Icons modified from
# https://github.com/matplotlib/matplotlib/tree/main/lib/matplotlib/mpl-data/images
ICON_ROOT = Path(__file__).parent / "icons"
__all__ = ["NapariMPLWidget"]


class NapariMPLWidget(QWidget):
    """
    Base Matplotlib canvas. Widget that can be embedded as a napari widget.

    This creates a single FigureCanvas, which contains a single Figure.
    It is not responsible for creating any Axes, because different widgets
    may want to implement different subplot layouts.

    This class also handles callbacks to automatically update figures when
    the layer selection or z-step is changed in the napari viewer. To take
    advantage of this sub-classes should implement the ``clear()`` and
    ``draw()`` methods.

    Attributes
    ----------
    viewer : `napari.Viewer`
        Main napari viewer.
    canvas : matplotlib.backends.backend_qt5agg.FigureCanvas
        Matplotlib canvas.
    layers : `list`
        List of currently selected napari layers.
    """

    def __init__(self, napari_viewer: napari.viewer.Viewer):
        super().__init__()

        self.viewer = napari_viewer
        self.canvas = FigureCanvas()
        self.canvas.widget = self

        self.canvas.figure.patch.set_facecolor("none")
        self.canvas.figure.set_layout_engine("constrained")
        self.toolbar = NapariNavigationToolbar(
            self.canvas, self
        )  # type: ignore[no-untyped-call]
        self._replace_toolbar_icons()

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.canvas)

        self.setup_callbacks()
        self.layers: List[napari.layers.Layer] = []

    # Accept any number of input layers by default
    n_layers_input = Interval(None, None)
    # Accept any type of input layer by default
    input_layer_types: Tuple[napari.layers.Layer, ...] = (napari.layers.Layer,)

    @property
    def figure(self) -> Figure:
        """Matplotlib figure."""
        return self.canvas.figure

    @property
    def n_selected_layers(self) -> int:
        """
        Number of currently selected layers.
        """
        return len(self.layers)

    @property
    def current_z(self) -> int:
        """
        Current z-step of the viewer.
        """
        return self.viewer.dims.current_step[0]

    def setup_callbacks(self) -> None:
        """
        Sets up callbacks.

        Sets up callbacks for:
        - Layer selection changing
        - z-step changing
        """
        # z-step changed in viewer
        self.viewer.dims.events.current_step.connect(self._draw)
        # Layer selection changed in viewer
        self.viewer.layers.selection.events.changed.connect(self.update_layers)

    def update_layers(self, event: napari.utils.events.Event) -> None:
        """
        Update the layers attribute with currently selected layers and re-draw.
        """
        self.layers = list(self.viewer.layers.selection)
        self._on_update_layers()
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

    def add_single_axes(self) -> None:
        """
        Add a single Axes to the figure.

        The Axes is saved on the ``.axes`` attribute for later access.
        """
        self.axes = self.figure.subplots()
        self.apply_napari_colorscheme(self.axes)

    @staticmethod
    def apply_napari_colorscheme(ax: Axes) -> None:
        """Apply napari-compatible colorscheme to an axes object."""
        # changing color of axes background to transparent
        ax.set_facecolor("none")

        # changing colors of all axes
        for spine in ax.spines:
            ax.spines[spine].set_color("white")

        ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")

        # changing colors of axes labels
        ax.tick_params(axis="x", colors="white")
        ax.tick_params(axis="y", colors="white")

    def _on_update_layers(self) -> None:
        """
        Function is called when self.layers is updated via
        ``self.update_layers()``.

        This is a no-op, and is intended for derived classes to override.
        """

    def _replace_toolbar_icons(self) -> None:
        # Modify toolbar icons and some tooltips
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
                icon_path = os.path.join(ICON_ROOT, text + ".png")
                action.setIcon(QIcon(icon_path))


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
        # changes pan/zoom icons depending on state (checked or not)
        if "pan" in self._actions:
            if self._actions["pan"].isChecked():
                self._actions["pan"].setIcon(
                    QIcon(os.path.join(ICON_ROOT, "Pan_checked.png"))
                )
            else:
                self._actions["pan"].setIcon(
                    QIcon(os.path.join(ICON_ROOT, "Pan.png"))
                )
        if "zoom" in self._actions:
            if self._actions["zoom"].isChecked():
                self._actions["zoom"].setIcon(
                    QIcon(os.path.join(ICON_ROOT, "Zoom_checked.png"))
                )
            else:
                self._actions["zoom"].setIcon(
                    QIcon(os.path.join(ICON_ROOT, "Zoom.png"))
                )
