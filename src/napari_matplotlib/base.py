import matplotlib as mpl
import napari
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas,
    NavigationToolbar2QT,
)
from matplotlib.figure import Figure
from qtpy.QtWidgets import QVBoxLayout, QWidget

mpl.rc("axes", edgecolor="white")
mpl.rc("axes", facecolor="#262930")
mpl.rc("axes", labelcolor="white")
mpl.rc("savefig", facecolor="#262930")
mpl.rc("text", color="white")

mpl.rc("xtick", color="white")
mpl.rc("ytick", color="white")
__all__ = ["NapariMPLWidget"]


class NapariMPLWidget(QWidget):
    """
    Base widget that can be embedded as a napari widget and contains a
    Matplotlib canvas.

    This creates a single Figure, and sub-classes should implement logic for
    drawing on that Figure.

    Attributes
    ----------
    viewer : `napari.Viewer`
        Main napari viewer.
    figure : `matplotlib.figure.Figure`
        Matplotlib figure.
    canvas : matplotlib.backends.backend_qt5agg.FigureCanvas
        Matplotlib canvas.
    """

    def __init__(self, napari_viewer: napari.viewer.Viewer):
        super().__init__()

        self.viewer = napari_viewer
        self.figure = Figure(figsize=(5, 3), tight_layout=True)
        self.canvas = FigureCanvas()
        self.canvas.figure.patch.set_facecolor("#262930")
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.canvas)

    @property
    def current_z(self) -> int:
        """
        Current z-step of the viewer.
        """
        return self.viewer.dims.current_step[0]
