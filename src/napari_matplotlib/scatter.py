from typing import Any, Optional, Tuple

import napari
import numpy.typing as npt
from qtpy.QtWidgets import QWidget

from .base import SingleAxesWidget
from .features import FeaturesMixin
from .util import Interval

__all__ = ["ScatterBaseWidget", "ScatterWidget", "FeaturesScatterWidget"]


class ScatterBaseWidget(SingleAxesWidget):
    """
    Base class for widgets that scatter two datasets against each other.
    """

    # if the number of points is greater than this value,
    # the scatter is plotted as a 2D histogram
    _threshold_to_switch_to_histogram = 500

    def draw(self) -> None:
        """
        Scatter the currently selected layers.
        """
        x, y, x_axis_name, y_axis_name = self._get_data()

        if x.size > self._threshold_to_switch_to_histogram:
            self.axes.hist2d(
                x.ravel(),
                y.ravel(),
                bins=100,
            )
        else:
            self.axes.scatter(x, y, alpha=0.5)

        self.axes.set_xlabel(x_axis_name)
        self.axes.set_ylabel(y_axis_name)

    def _get_data(self) -> Tuple[npt.NDArray[Any], npt.NDArray[Any], str, str]:
        """
        Get the plot data.

        This must be implemented on the subclass.

        Returns
        -------
        x, y : np.ndarray
            x and y values of plot data.
        x_axis_name, y_axis_name : str
            Label to display on the x/y axis
        """
        raise NotImplementedError


class ScatterWidget(ScatterBaseWidget):
    """
    Scatter data in two similarly shaped layers.

    If there are more than 500 data points, a 2D histogram is displayed instead
    of a scatter plot, to avoid too many scatter points.
    """

    n_layers_input = Interval(2, 2)
    input_layer_types = (napari.layers.Image,)

    def _get_data(self) -> Tuple[npt.NDArray[Any], npt.NDArray[Any], str, str]:
        """
        Get the plot data.

        Returns
        -------
        data : List[np.ndarray]
            List contains the in view slice of X and Y axis images.
        x_axis_name : str
            The title to display on the x axis
        y_axis_name: str
            The title to display on the y axis
        """
        x = self.layers[0].data[self.current_z]
        y = self.layers[1].data[self.current_z]
        x_axis_name = self.layers[0].name
        y_axis_name = self.layers[1].name

        return x, y, x_axis_name, y_axis_name


class FeaturesScatterWidget(ScatterBaseWidget, FeaturesMixin):
    """
    Widget to scatter data stored in two layer feature attributes.
    """

    def __init__(
        self,
        napari_viewer: napari.viewer.Viewer,
        parent: Optional[QWidget] = None,
    ):
        ScatterBaseWidget.__init__(self, napari_viewer, parent=parent)
        FeaturesMixin.__init__(self, ndim=2)
        self._update_layers(None)

    def draw(self) -> None:
        """
        Scatter two features from the currently selected layer.
        """
        if self._ready_to_plot():
            super().draw()

    def _get_data(self) -> Tuple[npt.NDArray[Any], npt.NDArray[Any], str, str]:
        """
        Get the plot data from the ``features`` attribute of the first
        selected layer.

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
        feature_table = self.layers[0].features

        x = feature_table[self.get_key("x")]
        y = feature_table[self.get_key("y")]

        x_axis_name = str(self.get_key("x"))
        y_axis_name = str(self.get_key("y"))

        return x, y, x_axis_name, y_axis_name
