import napari
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from qtpy.QtWidgets import QComboBox, QVBoxLayout, QWidget
import numpy as np


class ExampleQWidget(QWidget):
    def __init__(self, napari_viewer: napari.viewer.Viewer):
        super().__init__()
        self.viewer = napari_viewer
        self.layer = self.viewer.layers[0]

        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.axes = self.canvas.figure.subplots()

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.canvas)

        self.viewer.dims.events.current_step.connect(self.hist_current_layer)
        self.viewer.layers.selection.events.active.connect(self.update_layer)

        self.hist_current_layer()

    def update_layer(self, event):
        # Update current layer when selection changed in viewer
        if event.value:
            self.layer = event.value
            self.hist_current_layer()

    def hist_current_layer(self):
        self.axes.clear()
        layer = self.layer
        z = self.viewer.dims.current_step[0]
        bins = np.linspace(np.min(layer.data), np.max(layer.data), 100)
        data = layer.data[z]
        self.axes.hist(data.ravel(), bins=bins)
        self.axes.set_title(f"{layer.name}, z={z}")
        self.canvas.draw()
