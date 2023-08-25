from typing import Any, Dict, List, Optional, Tuple, Union

import napari
import numpy.typing as npt
from qtpy.QtWidgets import QComboBox, QLabel, QVBoxLayout, QWidget

from .base import SingleAxesWidget
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
        if len(self.layers) == 0:
            return
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


class FeaturesScatterWidget(ScatterBaseWidget):
    """
    Widget to scatter data stored in two layer feature attributes.
    """

    n_layers_input = Interval(1, 1)
    # All layers that have a .features attributes
    input_layer_types = (
        napari.layers.Labels,
        napari.layers.Points,
        napari.layers.Shapes,
        napari.layers.Tracks,
        napari.layers.Vectors,
    )

    def __init__(
        self,
        napari_viewer: napari.viewer.Viewer,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(napari_viewer, parent=parent)

        self.layout().addLayout(QVBoxLayout())

        self._selectors: Dict[str, QComboBox] = {}
        for dim in ["x", "y"]:
            self._selectors[dim] = QComboBox()
            # Re-draw when combo boxes are updated
            self._selectors[dim].currentTextChanged.connect(self._draw)

            self.layout().addWidget(QLabel(f"{dim}-axis:"))
            self.layout().addWidget(self._selectors[dim])

        self._update_layers(None)

    @property
    def x_axis_key(self) -> Union[str, None]:
        """
        Key for the x-axis data.
        """
        if self._selectors["x"].count() == 0:
            return None
        else:
            return self._selectors["x"].currentText()

    @x_axis_key.setter
    def x_axis_key(self, key: str) -> None:
        self._selectors["x"].setCurrentText(key)
        self._draw()

    @property
    def y_axis_key(self) -> Union[str, None]:
        """
        Key for the y-axis data.
        """
        if self._selectors["y"].count() == 0:
            return None
        else:
            return self._selectors["y"].currentText()

    @y_axis_key.setter
    def y_axis_key(self, key: str) -> None:
        self._selectors["y"].setCurrentText(key)
        self._draw()

    def _get_valid_axis_keys(self) -> List[str]:
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

    def _ready_to_scatter(self) -> bool:
        """
        Return True if selected layer has a feature table we can scatter with,
        and the two columns to be scatterd have been selected.
        """
        if not hasattr(self.layers[0], "features"):
            return False

        feature_table = self.layers[0].features
        valid_keys = self._get_valid_axis_keys()
        return (
            feature_table is not None
            and len(feature_table) > 0
            and self.x_axis_key in valid_keys
            and self.y_axis_key in valid_keys
        )

    def draw(self) -> None:
        """
        Scatter two features from the currently selected layer.
        """
        if self._ready_to_scatter():
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

        x = feature_table[self.x_axis_key]
        y = feature_table[self.y_axis_key]

        x_axis_name = str(self.x_axis_key)
        y_axis_name = str(self.y_axis_key)

        return x, y, x_axis_name, y_axis_name

    def on_update_layers(self) -> None:
        """
        Called when the layer selection changes by ``self.update_layers()``.
        """
        # Clear combobox
        for dim in ["x", "y"]:
            while self._selectors[dim].count() > 0:
                self._selectors[dim].removeItem(0)
            # Add keys for newly selected layer
            self._selectors[dim].addItems(self._get_valid_axis_keys())
