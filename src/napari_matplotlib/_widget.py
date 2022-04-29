import napari
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from qtpy.QtWidgets import QComboBox, QVBoxLayout, QWidget


class ExampleQWidget(QWidget):
    def __init__(self, napari_viewer: napari.viewer.Viewer):
        super().__init__()
        self.viewer = napari_viewer

        self.setLayout(QVBoxLayout())

        static_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.axes = static_canvas.figure.subplots()

        self.layer_box = QComboBox()
        self.layout().addWidget(self.layer_box)
        self.layout().addWidget(static_canvas)

        self.update_layers()

    def update_layers(self):
        self.layer_box.clear()
        names = [layer.name for layer in self.viewer.layers]
        self.layer_box.insertItems(0, names)
