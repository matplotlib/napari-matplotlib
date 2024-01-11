from typing import Any, Optional, cast

import napari
import numpy as np
import numpy.typing as npt
from matplotlib.container import BarContainer
from qtpy.QtWidgets import (
    QComboBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from .base import SingleAxesWidget
from .features import FEATURES_LAYER_TYPES
from .util import Interval

__all__ = ["HistogramWidget", "FeaturesHistogramWidget"]

_COLORS = {"r": "tab:red", "g": "tab:green", "b": "tab:blue"}


class HistogramWidget(SingleAxesWidget):
    """
    Display a histogram of the currently selected layer.
    """

    n_layers_input = Interval(1, 1)
    input_layer_types = (napari.layers.Image,)

    def __init__(
        self,
        napari_viewer: napari.viewer.Viewer,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(napari_viewer, parent=parent)
        self._update_layers(None)
        self.viewer.events.theme.connect(self._on_napari_theme_changed)

    def on_update_layers(self) -> None:
        """
        Called when the selected layers are updated.
        """
        super().on_update_layers()
        for layer in self.viewer.layers:
            layer.events.contrast_limits.connect(self._update_contrast_lims)

    def _update_contrast_lims(self) -> None:
        for lim, line in zip(
            self.layers[0].contrast_limits, self._contrast_lines
        ):
            line.set_xdata(lim)

        self.figure.canvas.draw()

    def draw(self) -> None:
        """
        Clear the axes and histogram the currently selected layer/slice.
        """
        layer = self.layers[0]

        if layer.data.ndim - layer.rgb == 3:
            # 3D data, can be single channel or RGB
            data = layer.data[self.current_z]
            self.axes.set_title(f"z={self.current_z}")
        else:
            data = layer.data
        # Read data into memory if it's a dask array
        data = np.asarray(data)

        # Important to calculate bins after slicing 3D data, to avoid reading
        # whole cube into memory.
        if data.dtype.kind == "i":
            # Make sure integer data types have integer sized bins
            step = (np.max(data) - np.min(data)) // 100
            bins = np.arange(np.min(data), np.max(data) + step, step)
        else:
            bins = np.linspace(np.min(data), np.max(data), 100)

        if layer.rgb:
            # Histogram RGB channels independently
            for i, c in enumerate("rgb"):
                self.axes.hist(
                    data[..., i].ravel(),
                    bins=bins,
                    label=c,
                    histtype="step",
                    color=_COLORS[c],
                )
        else:
            self.axes.hist(data.ravel(), bins=bins, label=layer.name)

        self._contrast_lines = [
            self.axes.axvline(lim, color="white")
            for lim in layer.contrast_limits
        ]
        self.axes.legend()


class FeaturesHistogramWidget(SingleAxesWidget):
    """
    Display a histogram of selected feature attached to selected layer.
    """

    n_layers_input = Interval(1, 1)
    # All layers that have a .features attributes
    input_layer_types = FEATURES_LAYER_TYPES

    def __init__(
        self,
        napari_viewer: napari.viewer.Viewer,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(napari_viewer, parent=parent)

        self.layout().addLayout(QVBoxLayout())
        self._key_selection_widget = QComboBox()
        self.layout().addWidget(QLabel("Key:"))
        self.layout().addWidget(self._key_selection_widget)

        self._key_selection_widget.currentTextChanged.connect(
            self._set_axis_keys
        )

        self._update_layers(None)

    @property
    def x_axis_key(self) -> Optional[str]:
        """Key to access x axis data from the FeaturesTable"""
        return self._x_axis_key

    @x_axis_key.setter
    def x_axis_key(self, key: Optional[str]) -> None:
        self._x_axis_key = key
        self._draw()

    def _set_axis_keys(self, x_axis_key: str) -> None:
        """Set both axis keys and then redraw the plot"""
        self._x_axis_key = x_axis_key
        self._draw()

    def _get_valid_axis_keys(self) -> list[str]:
        """
        Get the valid axis keys from the layer FeatureTable.

        Returns
        -------
        axis_keys : List[str]
            The valid axis keys in the FeatureTable. If the table is empty
            or there isn't a table, returns an empty list.
        """
        if len(self.layers) == 0 or not (hasattr(self.layers[0], "features")):
            return []
        else:
            return self.layers[0].features.keys()

    def _get_data(self) -> tuple[Optional[npt.NDArray[Any]], str]:
        """Get the plot data.

        Returns
        -------
        data : List[np.ndarray]
            List contains X and Y columns from the FeatureTable. Returns
            an empty array if nothing to plot.
        x_axis_name : str
            The title to display on the x axis. Returns
            an empty string if nothing to plot.
        """
        if not hasattr(self.layers[0], "features"):
            # if the selected layer doesn't have a featuretable,
            # skip draw
            return None, ""

        feature_table = self.layers[0].features

        if (len(feature_table) == 0) or (self.x_axis_key is None):
            return None, ""

        data = feature_table[self.x_axis_key]
        x_axis_name = self.x_axis_key.replace("_", " ")

        return data, x_axis_name

    def on_update_layers(self) -> None:
        """
        Called when the layer selection changes by ``self.update_layers()``.
        """
        # reset the axis keys
        self._x_axis_key = None

        # Clear combobox
        self._key_selection_widget.clear()
        self._key_selection_widget.addItems(self._get_valid_axis_keys())

    def draw(self) -> None:
        """Clear the axes and histogram the currently selected layer/slice."""
        # get the colormap from the layer depending on its type
        if isinstance(self.layers[0], napari.layers.Points):
            colormap = self.layers[0].face_colormap
            self.layers[0].face_color = self.x_axis_key
        elif isinstance(self.layers[0], napari.layers.Vectors):
            colormap = self.layers[0].edge_colormap
            self.layers[0].edge_color = self.x_axis_key
        else:
            colormap = None

        # apply new colors to the layer
        self.viewer.layers[self.layers[0].name].refresh_colors(True)
        self.viewer.layers[self.layers[0].name].refresh()

        # Draw the histogram
        data, x_axis_name = self._get_data()

        if data is None:
            return

        _, bins, patches = self.axes.hist(
            data, bins=50, edgecolor="white", linewidth=0.3
        )
        patches = cast(BarContainer, patches)

        # recolor the histogram plot
        if colormap is not None:
            self.bins_norm = (bins - bins.min()) / (bins.max() - bins.min())
            colors = colormap.map(self.bins_norm)

            # Set histogram style:
            for idx, patch in enumerate(patches):
                patch.set_facecolor(colors[idx])

        # set ax labels
        self.axes.set_xlabel(x_axis_name)
        self.axes.set_ylabel("Counts [#]")
