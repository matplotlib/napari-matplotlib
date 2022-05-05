import numpy as np

from .base import NapariMPLWidget

__all__ = ["HistogramWidget"]

import napari

_COLORS = {"r": "tab:red", "g": "tab:green", "b": "tab:blue"}


class HistogramWidget(NapariMPLWidget):
    """
    Display a histogram of the currently selected layer.
    """

    n_layers_input = 1

    def __init__(self, napari_viewer: napari.viewer.Viewer):
        super().__init__(napari_viewer)
        self.axes = self.canvas.figure.subplots()
        self.update_layers(None)

    def clear(self) -> None:
        self.axes.clear()

    def draw(self) -> None:
        """
        Clear the axes and histogram the currently selected layer/slice.
        """
        layer = self.layers[0]
        bins = np.linspace(np.min(layer.data), np.max(layer.data), 100)

        if layer.data.ndim - layer.rgb == 3:
            # 3D data, can be single channel or RGB
            data = layer.data[self.current_z]
            self.axes.set_title(f"z={self.current_z}")
        else:
            data = layer.data

        if layer.rgb:
            # Histogram RGB channels independently
            for i, c in enumerate("rgb"):
                self.axes.hist(
                    data[..., i].ravel(),
                    bins=bins,
                    label=c,
                    histtype="step",
                    color=_COLORS[c],
                )
        else:
            self.axes.hist(data.ravel(), bins=bins, label=layer.name)

        self.axes.legend()
