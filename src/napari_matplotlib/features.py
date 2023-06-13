import napari.layers

from napari_matplotlib.base import NapariMPLWidget
from napari_matplotlib.util import Interval


class FeaturesMixin(NapariMPLWidget):
    """
    Mixin to help with widgets that plot data from a features table stored
    on a single layer.
    """

    n_layers_input = Interval(1, 1)
    # All layers that have a .features attributes
    input_layer_types = (
        napari.layers.Labels,
        napari.layers.Points,
        napari.layers.Shapes,
        napari.layers.Tracks,
        napari.layers.Vectors,
    )
