from typing import Dict, Tuple

import napari
import numpy as np
from qtpy.QtWidgets import QComboBox, QHBoxLayout, QSpinBox

from napari_matplotlib.base import NapariMPLWidget

__all__ = ["SliceWidget"]

_dims = ["x", "y", "z"]


class SliceWidget(NapariMPLWidget):
    """
    Plot a 1D slice along a given dimension.
    """

    n_layers_input = 1

    def __init__(self, napari_viewer: napari.viewer.Viewer):
        super().__init__(napari_viewer)
        self.axes = self.canvas.figure.subplots()

        button_layout = QHBoxLayout()
        self.layout().addLayout(button_layout)

        self.dim_selector = QComboBox()
        button_layout.addWidget(self.dim_selector)
        self.dim_selector.addItems(_dims)

        self.slice_selectors = {}
        for d in _dims:
            self.slice_selectors[d] = QSpinBox()
            button_layout.addWidget(self.slice_selectors[d])

        self.update_layers(None)

    @property
    def layer(self):
        return self.layers[0]

    @property
    def current_dim(self) -> str:
        """
        Currently selected slice dimension.
        """
        return self.dim_selector.currentText()

    @property
    def current_dim_index(self) -> int:
        """
        Currently selected slice dimension index.
        """
        # Note the reversed list because in napari the z-axis is the first
        # numpy axis
        return _dims[::-1].index(self.current_dim)

    @property
    def selector_values(self) -> Dict[str, int]:
        return {d: self.slice_selectors[d].value() for d in _dims}

    def update_slice_selectors(self) -> None:
        """
        Update range and enabled status of the slice selectors, and the value
        of the z slice selector.
        """
        # Update min/max
        for i, dim in enumerate(_dims):
            self.slice_selectors[dim].setRange(0, self.layer.data.shape[i])

        # The z dimension is always set by current z in the viewer
        self.slice_selectors["z"].setValue(self.current_z)
        self.slice_selectors[self.current_dim].setEnabled(False)

    def get_xy(self) -> Tuple[np.ndarray, np.ndarray]:
        x = np.arange(self.layer.data.shape[self.current_dim_index])

        slices = []
        for d in _dims:
            if d == self.current_dim:
                # Select all data along this axis
                slices.append(slice(None))
            else:
                # Select specific index
                val = self.selector_values[d]
                slices.append(slice(val, val + 1))

        # Reverse since z is the first axis in napari
        slices = slices[::-1]
        y = self.layer.data[tuple(slices)].ravel()

        return x, y

    def clear(self) -> None:
        self.axes.cla()

    def draw(self) -> None:
        """
        Clear axes and draw a 1D plot.
        """
        self.update_slice_selectors()
        x, y = self.get_xy()

        self.axes.plot(x, y)
        self.axes.set_xlabel(self.current_dim)
        self.axes.set_title(self.layer.name)
