from typing import Any, Dict, List, Optional, Tuple

import matplotlib.ticker as mticker
import napari
import numpy as np
import numpy.typing as npt
from qtpy.QtWidgets import QComboBox, QHBoxLayout, QLabel, QSpinBox, QWidget

from .base import SingleAxesWidget
from .util import Interval

__all__ = ["SliceWidget"]

_dims_sel = ["x", "y"]


class SliceWidget(SingleAxesWidget):
    """
    Plot a 1D slice along a given dimension.
    """

    n_layers_input = Interval(1, 1)
    input_layer_types = (napari.layers.Image,)

    def __init__(
        self,
        napari_viewer: napari.viewer.Viewer,
        parent: Optional[QWidget] = None,
    ):
        # Setup figure/axes
        super().__init__(napari_viewer, parent=parent)

        button_layout = QHBoxLayout()
        self.layout().addLayout(button_layout)

        self.dim_selector = QComboBox()
        button_layout.addWidget(QLabel("Slice axis:"))
        button_layout.addWidget(self.dim_selector)
        self.dim_selector.addItems(["x", "y", "z"])

        self.slice_selectors = {}
        for d in _dims_sel:
            self.slice_selectors[d] = QSpinBox()
            button_layout.addWidget(QLabel(f"{d}:"))
            button_layout.addWidget(self.slice_selectors[d])

        # Setup callbacks
        # Re-draw when any of the combon/spin boxes are updated
        self.dim_selector.currentTextChanged.connect(self._draw)
        for d in _dims_sel:
            self.slice_selectors[d].textChanged.connect(self._draw)

        self._update_layers(None)

    @property
    def _layer(self) -> napari.layers.Layer:
        """
        Layer being plotted.
        """
        return self.layers[0]

    @property
    def current_dim_name(self) -> str:
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
        return self._dim_names[::-1].index(self.current_dim_name)

    @property
    def _dim_names(self) -> List[str]:
        """
        List of dimension names. This is a property as it varies depending on the
        dimensionality of the currently selected data.
        """
        if self._layer.data.ndim == 2:
            return ["x", "y"]
        elif self._layer.data.ndim == 3:
            return ["x", "y", "z"]
        else:
            raise RuntimeError("Don't know how to handle ndim != 2 or 3")

    @property
    def _selector_values(self) -> Dict[str, int]:
        """
        Values of the slice selectors.

        Mapping from dimension name to value.
        """
        return {d: self.slice_selectors[d].value() for d in _dims_sel}

    def _get_xy(self) -> Tuple[npt.NDArray[Any], npt.NDArray[Any]]:
        """
        Get data for plotting.
        """
        dim_index = self.current_dim_index
        if self._layer.data.ndim == 2:
            dim_index -= 1
        x = np.arange(self._layer.data.shape[dim_index])

        vals = self._selector_values
        vals.update({"z": self.current_z})

        slices = []
        for dim_name in self._dim_names:
            if dim_name == self.current_dim_name:
                # Select all data along this axis
                slices.append(slice(None))
            else:
                # Select specific index
                val = vals[dim_name]
                slices.append(slice(val, val + 1))

        # Reverse since z is the first axis in napari
        slices = slices[::-1]
        y = self._layer.data[tuple(slices)].ravel()

        return x, y

    def draw(self) -> None:
        """
        Clear axes and draw a 1D plot.
        """
        x, y = self._get_xy()

        self.axes.plot(x, y)
        self.axes.set_xlabel(self.current_dim_name)
        self.axes.set_title(self._layer.name)
        # Make sure all ticks lie on integer values
        self.axes.xaxis.set_major_locator(
            mticker.MaxNLocator(steps=[1, 2, 5, 10], integer=True)
        )
