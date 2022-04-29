import napari
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from qtpy.QtWidgets import QVBoxLayout, QWidget

__all__ = ["HistogramWidget"]


class NapariMPLWidget(QWidget):
    """
    Attributes
    ----------
    viewer : napari.viewer.Viewer
        Main napari viewer.
    figure : matplotlib.figure.Figure
        Matplotlib figure.
    canvas : matplotlib.backends.backend_qt5agg.FigureCanvas
        Matplotlib canvas.
    axes : matplotlib.axes.Axes
        Matplotlib axes.
    """

    def __init__(self, napari_viewer: napari.viewer.Viewer):
        super().__init__()

        self.viewer = napari_viewer
        self.figure = Figure(figsize=(5, 3), tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.axes = self.canvas.figure.subplots()

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.canvas)


class HistogramWidget(NapariMPLWidget):
    """
    Widget to display a histogram of the currently selected layer.

    Attributes
    ----------
    layer : napari.layers.Layer
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
        z = self.viewer.dims.current_step[0]
        bins = np.linspace(np.min(layer.data), np.max(layer.data), 100)
        data = layer.data[z]
        self.axes.hist(data.ravel(), bins=bins)
        self.axes.set_title(f"{layer.name}, z={z}")
        self.canvas.draw()
