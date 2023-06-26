from typing import Optional, List, Tuple

import napari
import numpy as np
from qtpy.QtWidgets import QWidget
from magicgui import magicgui, ComboBox

from .base import SingleAxesWidget
from .util import Interval
from .features import FEATURES_LAYER_TYPES

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

    def draw(self) -> None:
        """
        Clear the axes and histogram the currently selected layer/slice.
        """
        layer = self.layers[0]
        bins = np.linspace(np.min(layer.data), np.max(layer.data), 100)

        if layer.data.ndim - layer.rgb == 3:
            # 3D data, can be single channel or RGB
            data = layer.data[self.current_z]
            self.axes.set_title(f"z={self.current_z}")
        else:
            data = layer.data

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

        self.axes.legend()


class FeaturesHistogramWidget(NapariMPLWidget):
    n_layers_input = Interval(1, 1)
    # All layers that have a .features attributes
    input_layer_types = FEATURES_LAYER_TYPES

    def __init__(self, napari_viewer: napari.viewer.Viewer):
        super().__init__(napari_viewer)
        self.axes = self.canvas.figure.subplots()

        self._key_selection_widget = magicgui(
            self._set_axis_keys,
            x_axis_key={"choices": self._get_valid_axis_keys},
            call_button="plot",
        )
        self.layout().addWidget(self._key_selection_widget.native)

        self.update_layers(None)

    def clear(self) -> None:
        """
        Clear the axes.
        """
        self.axes.clear()

        self.layout().addWidget(self._key_selection_widget.native)

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

    def _get_valid_axis_keys(
        self, combo_widget: Optional[ComboBox] = None
    ) -> List[str]:
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

    def _get_data(self) -> Tuple[np.ndarray, str]:
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
            return [], ""

        feature_table = self.layers[0].features

        if (
            (len(feature_table) == 0)
            or (self.x_axis_key is None)
        ):
            return [], ""

        data = feature_table[self.x_axis_key]
        x_axis_name = self.x_axis_key.replace("_", " ")

        return data, x_axis_name

    def _on_update_layers(self) -> None:
        """
        This is called when the layer selection changes by
        ``self.update_layers()``.
        """
        if hasattr(self, "_key_selection_widget"):
            self._key_selection_widget.reset_choices()

        # reset the axis keys
        self._x_axis_key = None

    def draw(self) -> None:
        """Clear the axes and histogram the currently selected layer/slice."""

        data, x_axis_name = self._get_data()

        if len(data) == 0:
            return

        self.axes.hist(data, bins=50, edgecolor='white',
                                 linewidth=0.3)

        # set ax labels
        self.axes.set_xlabel(x_axis_name)
        self.axes.set_ylabel('Counts [#]')