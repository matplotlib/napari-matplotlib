from typing import List, Optional, Tuple

import matplotlib.colors as mcolor
import napari
import numpy as np
import pandas as pd
from magicgui import magicgui
from magicgui.widgets import ComboBox

from .base import NapariMPLWidget
from .util import Interval

__all__ = ["Line2DBaseWidget", "MetadataLine2DWidget"]


class Line2DBaseWidget(NapariMPLWidget):
    # opacity value for the lines
    _line_alpha = 0.5
    _lines = []

    def __init__(self, napari_viewer: napari.viewer.Viewer):
        super().__init__(napari_viewer)

        self.axes = self.canvas.figure.subplots()
        self.update_layers(None)

    def clear(self) -> None:
        """
        Clear the axes.
        """
        self.axes.clear()

    def draw(self) -> None:
        """
        Plot the currently selected layers.
        """
        data, x_axis_name, y_axis_name = self._get_data()
        

        if len(data) == 0:
            # don't plot if there isn't data
            return
        self._lines = []
        x_data = data[0]
        y_data = data[1]

        if len(y_data) < len(x_data):
            print("x_data bigger than y_data, plotting only first y_data")
        for i, y in enumerate(y_data):
            if len(x_data) == 1:
                line = self.axes.plot(x_data[0], y, alpha=self._line_alpha)
            else:
                line = self.axes.plot(x_data[i], y, alpha=self._line_alpha)
            self._lines += line

        self.axes.set_xlabel(x_axis_name)
        self.axes.set_ylabel(y_axis_name)

    def _get_data(self) -> Tuple[List[np.ndarray], str, str]:
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

class MetadataLine2DWidget(Line2DBaseWidget):
    n_layers_input = Interval(1, 1)

    def __init__(self, napari_viewer: napari.viewer.Viewer):
        super().__init__(napari_viewer)
        self.setMinimumSize(200, 200)
        self._plugin_name_widget = magicgui(
            self._set_plugin_name,
            plugin_name={"choices": self._get_plugin_metadata_key},
            auto_call = True,
        )
        self._key_selection_widget = magicgui(
            self._set_axis_keys,
            x_axis_key={"choices": self._get_valid_axis_keys},
            y_axis_key={"choices": self._get_valid_axis_keys},
            call_button="plot",
        )
        
        self.ray_index = 0
        self.dot_index = 0
        self.layout().insertWidget(0, self._plugin_name_widget.native)
        self.layout().addWidget(self._key_selection_widget.native)

    @property
    def x_axis_key(self) -> Optional[str]:
        """Key to access x axis data from the Metadata"""
        return self._x_axis_key

    @x_axis_key.setter
    def x_axis_key(self, key: Optional[str]) -> None:
        self._x_axis_key = key
        self._draw()

    @property
    def y_axis_key(self) -> Optional[str]:
        """Key to access y axis data from the Metadata"""
        return self._y_axis_key

    @y_axis_key.setter
    def y_axis_key(self, key: Optional[str]) -> None:
        self._y_axis_key = key
        self._draw()

    def _set_axis_keys(self, x_axis_key: str, y_axis_key: str) -> None:
        """Set both axis keys and then redraw the plot"""
        self._x_axis_key = x_axis_key
        self._y_axis_key = y_axis_key
        self._draw()
        
    @property
    def plugin_name_key(self) -> Optional[str]:
        """Key to plugin dictionary in the Metadata"""
        return self._plugin_name_key

    @plugin_name_key.setter
    def plugin_name_key(self, key: Optional[str]) -> None:
        self._plugin_name_key = key
        
    def _set_plugin_name(self, plugin_name: str) -> None:
        """Set plugin name from layer metadata"""
        self._plugin_name_key = plugin_name
    
    def _get_plugin_metadata_key(
            self, combo_widget: Optional[ComboBox] = None
        ) -> List[str]:
        """Get plugin key from layer metadata"""
        if len(self.layers) == 0:
            return []
        else:
            return self._get_valid_metadata_keys() 

    def _get_valid_metadata_keys(
            self) -> List[str]:
        """Get metadata keys if nested dictionaries"""
        if len(self.layers) == 0:
            return []
        else:
            metadata = self.layers[0].metadata
            keys_with_nested_dicts = []
            for key, value in metadata.items():
                if isinstance(value, dict):
                    keys_with_nested_dicts.append(key)
            return keys_with_nested_dicts

    def _get_valid_axis_keys(
        self, combo_widget: Optional[ComboBox] = None
    ) -> List[str]:
        """
        Get the valid axis keys from the layer Metadata.
        Returns
        -------
        axis_keys : List[str]
            The valid axis keys in the Metadata. If the table is empty
            or there isn't a table, returns an empty list.
        """
        
        if len(self.layers) == 0:
            return []
        else:
            valid_metadata = self._get_valid_metadata_keys()
            if not valid_metadata:
                return []
            else:
                if not hasattr(self, "plugin_name_key"):
                    self.plugin_name_key = self._get_valid_metadata_keys()[0]
                return self.layers[0].metadata[self.plugin_name_key].keys()

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
        valid_metadata = self._get_valid_metadata_keys()
        
        if (
            (not valid_metadata)
            or (self.x_axis_key is None)
            or (self.y_axis_key is None)
        ):
            return [], "", ""
        
        if not hasattr(self, "plugin_name_key"):
            self.plugin_name_key = valid_metadata[0]

        plugin_metadata_dict = self.layers[0].metadata[self.plugin_name_key]

        data_x = warp_to_list(plugin_metadata_dict[self.x_axis_key])
        data_y = warp_to_list(plugin_metadata_dict[self.y_axis_key])
        data = [data_x, data_y]

        x_axis_name = self.x_axis_key.replace("_", " ")
        y_axis_name = self.y_axis_key.replace("_", " ")

        return data, x_axis_name, y_axis_name

    def _on_update_layers(self) -> None:
        """
        This is called when the layer selection changes by
        ``self.update_layers()``.
        """
        # if hasattr(self, "_key_selection_widget"):
        #     self._plugin_name_widget.reset_choices()
        #     self._key_selection_widget.reset_choices()
        
        # reset the axis keys
        self._x_axis_key = None
        self._y_axis_key = None
        
def warp_to_list(data):
    if isinstance(data, list):
        return data
    # If numpy array, make a list from axis=0
    if isinstance(data, np.ndarray):
        if len(data.shape) == 1:
            data = data[np.newaxis,:]
        data = data.tolist()
    # If pandas dataframe, make a list from columns
    if isinstance(data, pd.DataFrame):
        data = data.T.values.tolist()
    return data

    