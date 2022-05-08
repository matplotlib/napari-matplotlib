from typing import List, Tuple, Union

import matplotlib.colors as mcolor
import napari
import numpy as np
from magicgui import magicgui

from .base import NapariMPLWidget

__all__ = ["ScatterWidget", "FeaturesScatterWidget"]


class ScatterBaseWidget(NapariMPLWidget):
    # opacity value for the markers
    _marker_alpha = 0.5

    # flag set to True if histogram should be used
    # for plotting large points
    _histogram_for_large_data = True

    # if the number of points is greater than this value,
    # the scatter is plotted as a 2dhist
    _threshold_to_switch_to_histogram = 500

    def __init__(
        self,
        napari_viewer: napari.viewer.Viewer,
    ):
        super().__init__(napari_viewer)

        self.axes = self.canvas.figure.subplots()
        self.update_layers(None)

    def clear(self) -> None:
        self.axes.clear()

    def draw(self) -> None:
        """
        Clear the axes and scatter the currently selected layers.
        """
        data, x_axis_name, y_axis_name = self._get_data()

        if len(data) == 0:
            # don't plot if there isn't data
            return

        if self._histogram_for_large_data and (data[0].size > 500):
            self.axes.hist2d(
                data[0].ravel(),
                data[1].ravel(),
                bins=100,
                norm=mcolor.LogNorm(),
            )
        else:
            self.axes.scatter(data[0], data[1], alpha=self._marker_alpha)

        self.axes.set_xlabel(x_axis_name)
        self.axes.set_ylabel(y_axis_name)

    def _get_data(self) -> Tuple[List[np.ndarray], str, str]:
        """Get the plot data.

        This must be implemented on the subclass.

        Returns
        -------
        data : np.ndarray
            The list containing the scatter plot data.
        x_axis_name : str
            The label to display on the x axis
        y_axis_name: str
            The label to display on the y axis
        """
        raise NotImplementedError


class ScatterWidget(ScatterBaseWidget):
    """
    Widget to display scatter plot of two similarly shaped image layers.

    If there are more than 500 data points, a 2D histogram is displayed instead
    of a scatter plot, to avoid too many scatter points.
    """

    n_layers_input = 2

    def __init__(
        self,
        napari_viewer: napari.viewer.Viewer,
    ):
        super().__init__(
            napari_viewer,
        )

    def _get_data(self) -> Tuple[List[np.ndarray], str, str]:
        """Get the plot data.

        Returns
        -------
        data : List[np.ndarray]
            List contains the in view slice of X and Y axis images.
        x_axis_name : str
            The title to display on the x axis
        y_axis_name: str
            The title to display on the y axis
        """
        data = [layer.data[self.current_z] for layer in self.layers]
        x_axis_name = self.layers[0].name
        y_axis_name = self.layers[1].name

        return data, x_axis_name, y_axis_name


class FeaturesScatterWidget(ScatterBaseWidget):
    n_layers_input = 1

    def __init__(
        self,
        napari_viewer: napari.viewer.Viewer,
        key_selection_gui: bool = True,
    ):
        self._key_selection_widget = None
        super().__init__(
            napari_viewer,
        )

        if key_selection_gui is True:
            self._key_selection_widget = magicgui(
                self._set_axis_keys,
                x_axis_key={"choices": self._get_valid_axis_keys},
                y_axis_key={"choices": self._get_valid_axis_keys},
                call_button="plot",
            )
            self.layout().addWidget(self._key_selection_widget.native)

    @property
    def x_axis_key(self) -> Union[None, str]:
        """Key to access x axis data from the FeaturesTable"""
        return self._x_axis_key

    @x_axis_key.setter
    def x_axis_key(self, key: Union[None, str]):
        self._x_axis_key = key
        self._draw()

    @property
    def y_axis_key(self) -> Union[None, str]:
        """Key to access y axis data from the FeaturesTable"""
        return self._y_axis_key

    @y_axis_key.setter
    def y_axis_key(self, key: Union[None, str]):
        self._y_axis_key = key
        self._draw()

    def _set_axis_keys(self, x_axis_key: str, y_axis_key: str):
        """Set both axis keys and then redraw the plot"""
        self._x_axis_key = x_axis_key
        self._y_axis_key = y_axis_key
        self._draw()

    def _get_valid_axis_keys(self, combo_widget=None) -> List[str]:
        """Get the valid axis keys from the layer FeatureTable.

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

    def _get_data(self) -> Tuple[List[np.ndarray], str, str]:
        """Get the plot data.

        Returns
        -------
        data : List[np.ndarray]
            List contains X and Y columns from the FeatureTable. Returns
            an empty array if nothing to plot.
        x_axis_name : str
            The title to display on the x axis. Returns
            an empty string if nothing to plot.
        y_axis_name: str
            The title to display on the y axis. Returns
            an empty string if nothing to plot.
        """
        if not hasattr(self.layers[0], "features"):
            # if the selected layer doesn't have a featuretable,
            # skip draw
            return np.array([]), "", ""

        feature_table = self.layers[0].features

        if (
            (len(feature_table) == 0)
            or (self.x_axis_key is None)
            or (self.y_axis_key is None)
        ):
            return np.array([]), "", ""

        data_x = feature_table[self.x_axis_key]
        data_y = feature_table[self.y_axis_key]
        data = [data_x, data_y]

        x_axis_name = self.x_axis_key.replace("_", " ")
        y_axis_name = self.y_axis_key.replace("_", " ")

        return data, x_axis_name, y_axis_name

    def _on_update_layers(self) -> None:
        """This is called when the layer selection changes
        by self.update_layers().
        """
        if self._key_selection_widget is not None:
            self._key_selection_widget.reset_choices()

        # reset the axis keys
        self._x_axis_key = None
        self._y_axis_key = None
