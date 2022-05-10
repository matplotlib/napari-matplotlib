from typing import Tuple

import napari
import numpy as np
from magicgui import magicgui

from napari_matplotlib.base import NapariMPLWidget

__all__ = ["SliceWidget"]

_dims_sel = ["x", "y"]
_dims = ["x", "y", "z"]


class SliceWidget(NapariMPLWidget):
    """
    Plot a 1D slice along a given dimension.
    """

    n_layers_input = 1

    def __init__(self, napari_viewer: napari.viewer.Viewer):
        # Setup figure/axes
        super().__init__(napari_viewer)
        self.axes = self.canvas.figure.subplots()

        self._selection_widget = magicgui(
            self._set_selector_values,
            dim={"choices": ["x", "y", "z"]},
            x_val={"min": 0, "max": 1},
            y_val={"min": 0, "max": 1},
            call_button=False,
            auto_call=True,
            layout="horizontal",
        )

        # Set initial default values
        self._vals = {"x": 0, "y": 0}
        self.current_dim = "x"
        self.layout().addWidget(self._selection_widget.native)
        self.update_layers(None)

    @property
    def layer(self):
        return self.layers[0]

    def _on_update_layers(self) -> None:
        """
        Change the range widget maxima when layer selection changed.
        """
        if len(self.layers) == 1:
            self._selection_widget.x_val.max = self.layer.data.shape[2]
            self._selection_widget.y_val.max = self.layer.data.shape[1]

    def _set_selector_values(self, dim: str, x_val: int, y_val: int):
        """
        Set dimension and slice values, and re-draw the plot.
        """
        self.current_dim = dim
        self._vals["x"] = x_val
        self._vals["y"] = y_val
        self._draw()

    def get_xy(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get data for plotting.
        """
        dim_index = _dims[::-1].index(self.current_dim)
        x = np.arange(self.layer.data.shape[dim_index])

        vals = self._vals
        vals.update({"z": self.current_z})

        slices = []
        for d in _dims:
            if d == self.current_dim:
                # Select all data along this axis
                slices.append(slice(None))
            else:
                # Select specific index
                val = vals[d]
                slices.append(slice(val, val + 1))

        # Reverse since z is the first axis in napari
        slices = slices[::-1]
        y = self.layer.data[tuple(slices)].ravel()

        return x, y

    def clear(self) -> None:
        self.axes.cla()

    def draw(self) -> None:
        x, y = self.get_xy()

        self.axes.plot(x, y)
        self.axes.set_xlabel(self.current_dim)
        self.axes.set_title(self.layer.name)
