from typing import Any, Dict, List, Optional, Tuple, Union
import matplotlib.colors as mcolor
from cycler import cycler
import napari
import numpy as np
import pandas as pd
import numpy.typing as npt
from qtpy.QtWidgets import QComboBox, QLabel, QVBoxLayout, QWidget

from .base import NapariMPLWidget
from .util import Interval

__all__ = ["LineBaseWidget", "MetadataLineWidget", "FeaturesLineWidget"]


class LineBaseWidget(NapariMPLWidget):
    """
    Base class for widgets that do line plots of two datasets against each other.
    """

    def __init__(self, napari_viewer: napari.viewer.Viewer, parent: Optional[QWidget] = None,
                 ):
        super().__init__(napari_viewer, parent=parent)
        self.add_single_axes()

    def clear(self) -> None:
        """
        Clear the axes.
        """
        self.axes.clear()

    def draw(self) -> None:
        """
        Plot lines for the currently selected layers.
        """
        x, y, x_axis_name, y_axis_name = self._get_data()
        self.axes.plot(x, y)
        self.axes.set_xlabel(x_axis_name)
        self.axes.set_ylabel(y_axis_name)

    def _get_data(self) -> Tuple[npt.NDArray[Any], npt.NDArray[Any], str, str]:
        """Get the plot data.

        This must be implemented on the subclass.

        Returns
        -------
        data : np.ndarray
            The list containing the line plot data.
        x_axis_name : str
            The label to display on the x axis
        y_axis_name: str
            The label to display on the y axis
        """
        raise NotImplementedError


class LineWidget(LineBaseWidget):
    """
    Plot pixel values of an Image layer underneath a line from a Shapes layer.
    """

    n_layers_input = Interval(2, 2)
    input_layer_types = (napari.layers.Image,
                         napari.layers.Shapes,)

    def _get_data(self) -> Tuple[npt.NDArray[Any], npt.NDArray[Any], str, str]:
        """
        Get the plot data.

        Returns
        -------
        x, y : np.ndarray
            x and y values of plot data.
        x_axis_name : str
            The title to display on the x axis
        y_axis_name: str
            The title to display on the y axis
        """
        line_data = self._get_line_data()
        if line_data is None:
            return [], [], "", ""
        image_layers = [layer for layer in self.layers if isinstance(layer, napari.layers.Image)]
        if len(image_layers) == 0:
            return [], [], "", ""
        line_pixel_coords = self._get_line_pixel_coordinates(
            line_data[0], line_data[1], weight=1, shape=image_layers[0].data.shape)

        x = self._get_pixel_distances(line_pixel_coords, line_data[0])
        y = image_layers[0].data[self.current_z][line_pixel_coords[0], line_pixel_coords[1]]
        x_axis_name = 'pixel distance'
        y_axis_name = image_layers[0].name

        return x, y, x_axis_name, y_axis_name

    def _get_line_data(self):
        """
        Get the line data from the Shapes layer.
        """
        for layer in self.layers:
            # There must be a Shapes layer
            if isinstance(layer, napari.layers.Shapes):
                # There must be a line
                if 'line' in layer.shape_type:
                    line_data = layer.data[layer.shape_type.index('line')]
                    return line_data
        return None

    def _get_line_pixel_coordinates(self, start, end, weight=1, shape=None):
        """
        Get the pixel coordinates of a line from start to end using a bezier curve.
        """
        import numpy as np
        from skimage.draw import bezier_curve
        middle = (start + end) / 2
        start = np.round(start).astype(int)
        middle = np.round(middle).astype(int)
        end = np.round(end).astype(int)
        rr, cc = bezier_curve(start[0], start[1], middle[0], middle[1], end[0], end[1], weight=weight, shape=shape)
        return np.array([rr, cc])

    def _get_pixel_distances(self, line_coordinates, start):
        """
        Get the pixel distances from the start of the line.
        """
        distances = np.linalg.norm(line_coordinates - start[:, np.newaxis], axis=0)
        return distances


class FeaturesLineWidget(LineBaseWidget):
    """
    Widget to do line plots of two features from a layer, grouped by label.
    """

    n_layers_input = Interval(1, 1)
    # Currently working with Labels layer
    input_layer_types = (
        napari.layers.Labels,
    )

    def __init__(
        self,
        napari_viewer: napari.viewer.Viewer,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(napari_viewer, parent=parent)

        self.layout().addLayout(QVBoxLayout())

        self._selectors: Dict[str, QComboBox] = {}
        # Add split-by selector
        self._selectors["label"] = QComboBox()
        self._selectors["label"].currentTextChanged.connect(self._draw)
        self.layout().addWidget(QLabel(f"label:"))
        self.layout().addWidget(self._selectors["label"])

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

    @property
    def label_axis_key(self) -> Union[str, None]:
        """
        Key for the label factor.
        """
        if self._selectors["label"].count() == 0:
            return None
        else:
            return self._selectors["label"].currentText()

    @label_axis_key.setter
    def label_axis_key(self, key: str) -> None:
        self._selectors["label"].setCurrentText(key)
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

    def _check_valid_labels_data_and_set_color_cycle(self):
        feature_table = self.layers[0].features
        # Get sorted unique labels
        labels_from_table = np.unique(feature_table[self.label_axis_key].values).astype(int)
        labels_from_layer = np.unique(self.layers[0].data)[1:]  # exclude zero
        if np.array_equal(labels_from_table, labels_from_layer):
            # Set color cycle
            self._set_color_cycle(labels_from_table.tolist())
            return True
        return False

    def _ready_to_plot(self) -> bool:
        """
        Return True if selected layer has a feature table we can plot with,
        the two columns to be plotted have been selected, and object
        identifier ('labels') in the table.
        """
        if not hasattr(self.layers[0], "features"):
            return False

        feature_table = self.layers[0].features
        valid_keys = self._get_valid_axis_keys()
        valid_labels_data = self._check_valid_labels_data_and_set_color_cycle()

        return (
            feature_table is not None
            and len(feature_table) > 0
            and self.x_axis_key in valid_keys
            and self.y_axis_key in valid_keys
            and self.label_axis_key in valid_keys
            and valid_labels_data
        )

    def draw(self) -> None:
        """
        Plot lines for two features from the currently selected layer, grouped by labels.
        """
        if self._ready_to_plot():
            # draw calls _get_data and then plots the data
            super().draw()

    def _set_color_cycle(self, labels):
        """
        Set the color cycle for the plot from the colors in the Labels layer.
        """
        colors = [self.layers[0].get_color(label) for label in labels]
        napari_labels_cycler = (cycler(color=colors))
        self.axes.set_prop_cycle(napari_labels_cycler)

    def _get_data(self) -> Tuple[npt.NDArray[Any], npt.NDArray[Any], str, str]:
        """
        Get the plot data from the ``features`` attribute of the first
        selected layer grouped by labels.

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

        # Sort features by 'label' and x_axis_key
        feature_table = feature_table.sort_values(by=[self.label_axis_key, self.x_axis_key])
        # Get data for each label
        grouped = feature_table.groupby(self.label_axis_key)
        x = np.array([sub_df[self.x_axis_key].values for label, sub_df in grouped]).T.squeeze()
        y = np.array([sub_df[self.y_axis_key].values for label, sub_df in grouped]).T.squeeze()

        x_axis_name = str(self.x_axis_key)
        y_axis_name = str(self.y_axis_key)

        return x, y, x_axis_name, y_axis_name

    def on_update_layers(self) -> None:
        """
        Called when the layer selection changes by ``self.update_layers()``.
        """
        # Clear combobox
        for dim in ["label", "x", "y"]:
            while self._selectors[dim].count() > 0:
                self._selectors[dim].removeItem(0)
            # Add keys for newly selected layer
            self._selectors[dim].addItems(self._get_valid_axis_keys())
