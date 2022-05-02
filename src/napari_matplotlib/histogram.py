import napari
import numpy as np

from .base import NapariMPLWidget

__all__ = ["HistogramWidget"]


_COLORS = {"r": "tab:red", "g": "tab:green", "b": "tab:blue"}


class HistogramWidget(NapariMPLWidget):
    """
    Widget to display a histogram of the currently selected layer.

    Attributes
    ----------
    layer : `napari.layers.Layer`
        Current layer being histogrammed.
    """

    def __init__(self, napari_viewer: napari.viewer.Viewer):
        super().__init__(napari_viewer)
        self.layer = self.viewer.layers[-1]

        self.viewer.dims.events.current_step.connect(self.hist_current_layer)
        self.viewer.layers.selection.events.active.connect(self.update_layer)

        self.hist_current_layer()

    def update_layer(self, event: napari.utils.events.Event) -> None:
        """
        Update the currently selected layer.
        """
        # Update current layer when selection changed in viewer
        if event.value:
            self.layer = event.value
            self.hist_current_layer()

    def hist_current_layer(self) -> None:
        """
        Clear the axes and histogram the currently selected layer/slice.
        """
        self.axes.clear()
        layer = self.layer
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
        self.canvas.draw()
