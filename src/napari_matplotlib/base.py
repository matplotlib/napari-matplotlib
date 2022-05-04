import napari
from matplotlib.backends.backend_qt5agg import FigureCanvas, NavigationToolbar2QT
from matplotlib.figure import Figure
from qtpy.QtWidgets import QVBoxLayout, QWidget

__all__ = ["NapariMPLWidget"]

class MplCanvas(FigureCanvas):
    """
    Defines the canvas of the matplotlib window
    From https://github.com/haesleinhuepf/napari-workflow-inspector/blob/main/src/napari_workflow_inspector/_dock_widget.py
    """
    def __init__(self):
        self.fig = Figure()                         # create figure
        self.axes = self.fig.add_subplot(111)       # create subplot

        self.axes.spines['bottom'].set_color('white')
        self.axes.spines['top'].set_color('white')
        self.axes.spines['left'].set_color('white')
        self.axes.spines['right'].set_color('white')
        self.fig.patch.set_facecolor('#262930')
        self.axes.set_facecolor('#262930')
        self.axes.grid(which='major', linestyle='--', color='white', alpha=0.6)
        self.axes.tick_params(axis='both', colors='white')

        FigureCanvas.__init__(self, self.fig)       # initialize canvas
        FigureCanvas.updateGeometry(self)


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
        self.canvas = MplCanvas()
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        self.axes = self.canvas.axes

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.canvas)

    @property
    def current_z(self) -> int:
        """
        Current z-step of the viewer.
        """
        return self.viewer.dims.current_step[0]
