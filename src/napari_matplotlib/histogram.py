from typing import Any, Optional, cast

import napari
import numpy as np
import numpy.typing as npt
from matplotlib.container import BarContainer
from qtpy.QtWidgets import QComboBox, QLabel, QVBoxLayout, QWidget, QGroupBox, QFormLayout, QDoubleSpinBox, QSpinBox, QAbstractSpinBox

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

        # Create widgets for setting bin parameters
        bins_start = QDoubleSpinBox()
        bins_start.setObjectName("bins start")
        bins_start.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        bins_start.setRange(-1e10, 1e10)
        bins_start.setValue(0)
        bins_start.setWrapping(True)
        bins_start.setKeyboardTracking(False)
        bins_start.setDecimals(2)

        bins_stop = QDoubleSpinBox()
        bins_stop.setObjectName("bins stop")
        bins_stop.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        bins_stop.setRange(-1e10, 1e10)
        bins_stop.setValue(100)
        bins_stop.setKeyboardTracking(False)
        bins_stop.setDecimals(2)

        bins_num = QSpinBox()
        bins_num.setObjectName("bins num")
        bins_num.setRange(1, 100_000)
        bins_num.setValue(101)
        bins_num.setWrapping(False)
        bins_num.setKeyboardTracking(False)

        # Set bins widget layout
        bins_selection_layout = QFormLayout()
        bins_selection_layout.addRow("start", bins_start)
        bins_selection_layout.addRow("stop", bins_stop)
        bins_selection_layout.addRow("num", bins_num)

        # Group the widgets and add to main layout
        bins_widget_group = QGroupBox("Bins")
        bins_widget_group_layout = QVBoxLayout()
        bins_widget_group_layout.addLayout(bins_selection_layout)
        bins_widget_group.setLayout(bins_widget_group_layout)
        self.layout().addWidget(bins_widget_group)

        # Add callbacks
        bins_start.valueChanged.connect(self._draw)
        bins_stop.valueChanged.connect(self._draw)
        bins_num.valueChanged.connect(self._draw)

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

    @property
    def bins_start(self) -> float:
        """Minimum bin edge"""
        return self.findChild(QDoubleSpinBox, name="bins start").value()

    @bins_start.setter
    def bins_start(self, start: int | float) -> None:
        """Set the minimum bin edge"""
        self.findChild(QDoubleSpinBox, name="bins start").setValue(start)

    @property
    def bins_stop(self) -> float:
        """Maximum bin edge"""
        return self.findChild(QDoubleSpinBox, name="bins stop").value()

    @bins_stop.setter
    def bins_stop(self, stop: int | float) -> None:
        """Set the maximum bin edge"""
        self.findChild(QDoubleSpinBox, name="bins stop").setValue(stop)

    @property
    def bins_num(self) -> int:
        """Number of bins to use"""
        return self.findChild(QSpinBox, name="bins num").value()

    @bins_num.setter
    def bins_num(self, num: int) -> None:
        """Set the number of bins to use"""
        self.findChild(QSpinBox, name="bins num").setValue(num)

    def autoset_widget_bins(self, data: npt.ArrayLike) -> None:
        """Update widgets with bins determined from the image data"""

        bins = np.linspace(np.min(data), np.max(data), 100, dtype=data.dtype)
        self.bins_start = bins[0]
        self.bins_stop = bins[-1]
        self.bins_num = bins.size


    def _get_layer_data(self, layer) -> np.ndarray:
        """Get the data associated with a given layer"""

        if layer.data.ndim - layer.rgb == 3:
            # 3D data, can be single channel or RGB
            data = layer.data[self.current_z]
            self.axes.set_title(f"z={self.current_z}")
        else:
            data = layer.data

        # Read data into memory if it's a dask array
        data = np.asarray(data)

        return data

    def on_update_layers(self) -> None:
        """
        Called when the layer selection changes by ``self._update_layers()``.
        """

        if not self.layers:
            return

        # Reset to bin start, stop and step
        layer_data = self._get_layer_data(self.layers[0])
        self.autoset_widget_bins(data=layer_data)

        # Only allow integer bins for integer data
        n_decimals = 0 if np.issubdtype(layer_data.dtype, np.integer) else 2
        self.findChild(QDoubleSpinBox, name="bins start").setDecimals(n_decimals)
        self.findChild(QDoubleSpinBox, name="bins stop").setDecimals(n_decimals)

    def draw(self) -> None:
        """
        Clear the axes and histogram the currently selected layer/slice.
        """
        layer = self.layers[0]
        data = self._get_layer_data(layer)

        # Important to calculate bins after slicing 3D data, to avoid reading
        # whole cube into memory.
        if data.dtype.kind in {"i", "u"}:
            # Make sure integer data types have integer sized bins
            step = (self.bins_start - self.bins_stop) // self.bins_num
            step = max(1, step)
            bins = np.arange(self.bins_start, self.bins_stop + step, step)
        else:
            bins = np.linspace(self.bins_start, self.bins_stop, self.bins_num)

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
