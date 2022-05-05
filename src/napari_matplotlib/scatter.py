import matplotlib.colors as mcolor
import napari

from .base import NapariMPLWidget

__all__ = ["ScatterWidget"]


class ScatterWidget(NapariMPLWidget):
    """
    Widget to display scatter plot of two similarly shaped layers.

    If there are more than 500 data points, a 2D histogram is displayed instead
    of a scatter plot, to avoid too many scatter points.

    Attributes
    ----------
    layers : list[`napari.layers.Layer`]
        Current two layers being scattered.
    """

    def __init__(self, napari_viewer: napari.viewer.Viewer):
        super().__init__(napari_viewer)
        self.axes = self.canvas.figure.subplots()
        self.layers = self.viewer.layers[-2:]

        self.viewer.dims.events.current_step.connect(
            self.scatter_current_layers
        )
        self.viewer.layers.selection.events.changed.connect(self.update_layers)

        self.scatter_current_layers()

    def update_layers(self, event: napari.utils.events.Event) -> None:
        """
        Update the currently selected layers.
        """
        # Update current layer when selection changed in viewer
        layers = self.viewer.layers.selection
        if len(layers) == 2:
            self.layers = list(layers)
            self.scatter_current_layers()

    def scatter_current_layers(self) -> None:
        """
        Clear the axes and scatter the currently selected layers.
        """
        self.axes.clear()
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
        self.canvas.draw()
