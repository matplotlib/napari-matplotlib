import matplotlib.colors as mcolor
import napari

from .base import NapariMPLWidget

__all__ = ["ScatterWidget"]


class ScatterWidget(NapariMPLWidget):
    """
    Widget to display scatter plot of two similarly shaped layers.

    If there are more than 500 data points, a 2D histogram is displayed instead
    of a scatter plot, to avoid too many scatter points.
    """

    n_layers_input = 2

    def __init__(self, napari_viewer: napari.viewer.Viewer):
        super().__init__(napari_viewer)
        self.axes = self.canvas.figure.subplots()
        self.update_layers(None)

    def draw(self) -> None:
        """
        Clear the axes and scatter the currently selected layers.
        """
        data = [layer.data[self.current_z] for layer in self.layers]
        if data[0].size < 500:
            self.axes.scatter(data[0], data[1], alpha=0.5)
        else:
            self.axes.hist2d(
                data[0].ravel(),
                data[1].ravel(),
                bins=100,
                norm=mcolor.LogNorm(),
            )
        self.axes.set_xlabel(self.layers[0].name)
        self.axes.set_ylabel(self.layers[1].name)
