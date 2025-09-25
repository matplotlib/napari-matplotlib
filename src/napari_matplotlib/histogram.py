from typing import Any, cast

import napari
import numpy as np
import numpy.typing as npt
from matplotlib.container import BarContainer
from napari.layers import Image
from napari.layers._multiscale_data import MultiScaleData
from qtpy.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .base import SingleAxesWidget
from .features import FEATURES_LAYER_TYPES
from .util import Interval

__all__ = ["HistogramWidget", "FeaturesHistogramWidget"]

_COLORS = {"r": "tab:red", "g": "tab:green", "b": "tab:blue"}


def _get_bins(
    data: npt.NDArray[Any],
    num_bins: int = 100,
) -> npt.NDArray[np.floating]:
    """Create evenly spaced bins with a given interval.

    Parameters
    ----------
    data : napari.layers.Layer.data
        Napari layer data.
    num_bins : integer, optional
        Number of evenly-spaced bins to create. Defaults to 100.

    Returns
    -------
    bin_edges : numpy.ndarray
        Array of evenly spaced bin edges.
    """
    if data.dtype.kind in {"i", "u"}:
        # Make sure integer data types have integer sized bins
        step = np.ceil(np.ptp(data) / num_bins)
        return np.arange(np.min(data), np.max(data) + step, step)
    else:
        # For other data types we can use exactly `num_bins` bins
        # (and `num_bins` + 1 bin edges)
        return np.linspace(np.min(data), np.max(data), num_bins + 1)


class HistogramWidget(SingleAxesWidget):
    """
    Display a histogram of the currently selected layer.
    """

    n_layers_input = Interval(1, 1)
    input_layer_types = (napari.layers.Image,)

    def __init__(
        self,
        napari_viewer: napari.viewer.Viewer,
        parent: QWidget | None = None,
    ):
        super().__init__(napari_viewer, parent=parent)

        num_bins_widget = QSpinBox()
        num_bins_widget.setRange(1, 100_000)
        num_bins_widget.setValue(101)
        num_bins_widget.setWrapping(False)
        num_bins_widget.setKeyboardTracking(False)

        # Set bins widget layout
        bins_selection_layout = QFormLayout()
        bins_selection_layout.addRow("num bins", num_bins_widget)

        # Group the widgets and add to main layout
        params_widget_group = QGroupBox("Params")
        params_widget_group_layout = QVBoxLayout()
        params_widget_group_layout.addLayout(bins_selection_layout)
        params_widget_group.setLayout(params_widget_group_layout)
        self.layout().addWidget(params_widget_group)

        # Add callbacks
        num_bins_widget.valueChanged.connect(self._draw)

        # Store widgets for later usage
        self.num_bins_widget = num_bins_widget

        self._update_layers(None)
        self.viewer.events.theme.connect(self._on_napari_theme_changed)

    def on_update_layers(self) -> None:
        """
        Called when the selected layers are updated.
        """
        super().on_update_layers()
        if self._valid_layer_selection:
            self.layers[0].events.contrast_limits.connect(
                self._update_contrast_lims
            )

        if not self.layers:
            return

        # Reset the num bins based on new layer data
        layer_data = self._get_layer_data(self.layers[0])
        self._set_widget_nums_bins(data=layer_data)

    def _update_contrast_lims(self) -> None:
        for lim, line in zip(
            self.layers[0].contrast_limits, self._contrast_lines, strict=False
        ):
            line.set_xdata([lim])

        self.figure.canvas.draw()

    def _set_widget_nums_bins(self, data: npt.NDArray[Any]) -> None:
        """Update num_bins widget with bins determined from the image data"""
        bins = _get_bins(data)
        self.num_bins_widget.setValue(bins.size - 1)

    def _get_layer_data(self, layer: napari.layers.Layer) -> npt.NDArray[Any]:
        """Get the data associated with a given layer"""
        data = layer.data

        if isinstance(layer.data, MultiScaleData):
            data = data[layer.data_level]

        if layer.ndim - layer.rgb == 3:
            # 3D data, can be single channel or RGB
            # Slice in z dimension
            data = data[self.current_z]
            self.axes.set_title(f"z={self.current_z}")

        # Read data into memory if it's a dask array
        data = np.asarray(data)

        return data

    def draw(self) -> None:
        """
        Clear the axes and histogram the currently selected layer/slice.
        """
        layer: Image = self.layers[0]
        data = self._get_layer_data(layer)

        # Important to calculate bins after slicing 3D data, to avoid reading
        # whole cube into memory.
        bins = _get_bins(
            data,
            num_bins=self.num_bins_widget.value(),
        )

        if layer.rgb:
            # Histogram RGB channels independently
            for i, c in enumerate("rgb"):
                self.axes.hist(
                    data[..., i].ravel(),
                    bins=bins.tolist(),
                    label=c,
                    histtype="step",
                    color=_COLORS[c],
                )
        else:
            self.axes.hist(data.ravel(), bins=bins.tolist(), label=layer.name)

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
        parent: QWidget | None = None,
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
    def x_axis_key(self) -> str | None:
        """Key to access x axis data from the FeaturesTable"""
        return self._x_axis_key

    @x_axis_key.setter
    def x_axis_key(self, key: str | None) -> None:
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

    def _get_data(self) -> tuple[npt.NDArray[Any] | None, str]:
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
            if self.x_axis_key:
                self.layers[0].face_color = self.x_axis_key
        elif isinstance(self.layers[0], napari.layers.Vectors):
            colormap = self.layers[0].edge_colormap
            if self.x_axis_key:
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

        bins = _get_bins(data)

        _, bins, patches = self.axes.hist(data, bins=bins.tolist())
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
