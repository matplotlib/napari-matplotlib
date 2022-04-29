import napari
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from qtpy.QtWidgets import QHBoxLayout, QWidget


class ExampleQWidget(QWidget):
    def __init__(self, napari_viewer: napari.viewer.Viewer):
        super().__init__()
        self.viewer = napari_viewer

        self.setLayout(QHBoxLayout())

        static_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        axes = static_canvas.figure.subplots()

        self.layout().addWidget(static_canvas)
