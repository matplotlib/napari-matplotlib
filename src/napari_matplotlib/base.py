import napari
from matplotlib.backends.backend_qt5agg import FigureCanvas, NavigationToolbar2QT
from matplotlib.figure import Figure
from qtpy.QtWidgets import QVBoxLayout, QWidget

__all__ = ["NapariMPLWidget"]


class NapariMPLWidget(QWidget):
    """
    Base widget that can be embedded as a napari widget and contains a
    Matplotlib canvas.

    This creates a single Axes, and sub-classes should implement logic for
    drawing on that Axes.

    Attributes
    ----------
    viewer : `napari.Viewer`
        Main napari viewer.
    figure : `matplotlib.figure.Figure`
        Matplotlib figure.
    canvas : matplotlib.backends.backend_qt5agg.FigureCanvas
        Matplotlib canvas.
    axes : `matplotlib.axes.Axes`
        Matplotlib axes.
    """

    def __init__(self, napari_viewer: napari.viewer.Viewer):
        super().__init__()

        self.viewer = napari_viewer
        self.figure = Figure(figsize=(5, 3), tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        self.axes = self.canvas.figure.subplots()

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.canvas)

    @property
    def current_z(self) -> int:
        """
        Current z-step of the viewer.
        """
        return self.viewer.dims.current_step[0]
