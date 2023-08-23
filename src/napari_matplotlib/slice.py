from typing import Any, List, Optional, Tuple

import matplotlib.ticker as mticker
import napari
import numpy as np
import numpy.typing as npt
from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QComboBox,
    QLabel,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from .base import SingleAxesWidget
from .util import Interval

__all__ = ["SliceWidget"]


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

        self.dim_selector = QComboBox()
        self.dim_selector.addItems(["x", "y"])

        self.slice_selector = QSlider(orientation=Qt.Orientation.Horizontal)

        # Create widget layout
        button_layout = QVBoxLayout()
        button_layout.addWidget(QLabel("Slice axis:"))
        button_layout.addWidget(self.dim_selector)
        button_layout.addWidget(self.slice_selector)
        self.layout().addLayout(button_layout)

        # Setup callbacks
        # Re-draw when any of the combo/slider is updated
        self.dim_selector.currentTextChanged.connect(self._draw)
        self.slice_selector.valueChanged.connect(self._draw)

        self._update_layers(None)

    def on_update_layers(self) -> None:
        """
        Called when layer selection is updated.
        """
        if self.current_dim_name == "x":
            max = self._layer.data.shape[-2]
        elif self.current_dim_name == "y":
            max = self._layer.data.shape[-1]
        else:
            raise RuntimeError("dim name must be x or y")
        self.slice_selector.setRange(0, max)

    @property
    def _slice_width(self) -> int:
        """
        Width of the slice being plotted.
        """
        return self._layer.data.shape[self.current_dim_index] - 1

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
        return self._dim_names.index(self.current_dim_name)

    @property
    def _dim_names(self) -> List[str]:
        """
        List of dimension names. This is a property as it varies depending on the
        dimensionality of the currently selected data.
        """
        if self._layer.data.ndim == 2:
            return ["y", "x"]
        elif self._layer.data.ndim == 3:
            return ["z", "y", "x"]
        else:
            raise RuntimeError("Don't know how to handle ndim != 2 or 3")

    def _get_xy(self) -> Tuple[npt.NDArray[Any], npt.NDArray[Any]]:
        """
        Get data for plotting.
        """
        val = self.slice_selector.value()

        slices = []
        for dim_name in self._dim_names:
            if dim_name == self.current_dim_name:
                # Select all data along this axis
                slices.append(slice(None))
            elif dim_name == "z":
                # Only select the currently viewed z-index
                slices.append(slice(self.current_z, self.current_z + 1))
            else:
                # Select specific index
                slices.append(slice(val, val + 1))

        x = np.arange(self._slice_width)
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
