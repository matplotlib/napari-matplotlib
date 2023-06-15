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
