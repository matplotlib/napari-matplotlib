from typing import Dict, List, Optional

import napari
import napari.layers
from qtpy.QtWidgets import QComboBox, QLabel, QVBoxLayout

from napari_matplotlib.base import NapariMPLWidget
from napari_matplotlib.util import Interval


class FeaturesMixin(NapariMPLWidget):
    """
    Mixin to help with widgets that plot data from a features table stored
    on a single layer.
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

    def __init__(self, *, ndim: int) -> None:
        assert ndim in [1, 2]
        self.dims = ["x", "y"][:ndim]
        # Set up selection boxes
        self.layout().addLayout(QVBoxLayout())

        self._selectors: Dict[str, QComboBox] = {}
        for dim in self.dims:
            self._selectors[dim] = QComboBox()
            # Re-draw when combo boxes are updated
            self._selectors[dim].currentTextChanged.connect(self._draw)

            self.layout().addWidget(QLabel(f"{dim}-axis:"))
            self.layout().addWidget(self._selectors[dim])

    def get_key(self, dim: str) -> Optional[str]:
        """
        Get key for a given dimension.
        """
        if self._selectors[dim].count() == 0:
            return None
        else:
            return self._selectors[dim].currentText()

    def set_key(self, dim: str, value: str) -> None:
        """
        Set key for a given dimension.
        """
        self._selectors[dim].setCurrentText(value)
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

    def _ready_to_plot(self) -> bool:
        """
        Return True if selected layer has a feature table we can plot with,
        and the columns to plot have been selected.
        """
        if not hasattr(self.layers[0], "features"):
            return False

        feature_table = self.layers[0].features
        valid_keys = self._get_valid_axis_keys()
        return (
            feature_table is not None
            and len(feature_table) > 0
            and all([self.get_key(dim) in valid_keys for dim in self.dims])
        )

    def on_update_layers(self) -> None:
        """
        Called when the layer selection changes by ``self.update_layers()``.
        """
        # Clear combobox
        for dim in self.dims:
            while self._selectors[dim].count() > 0:
                self._selectors[dim].removeItem(0)
            # Add keys for newly selected layer
            self._selectors[dim].addItems(self._get_valid_axis_keys())
