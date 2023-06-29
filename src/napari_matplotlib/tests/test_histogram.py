from copy import deepcopy

import pytest

from napari_matplotlib import HistogramWidget
from napari_matplotlib.tests.helpers import (
    assert_figures_equal,
    assert_figures_not_equal,
)


@pytest.mark.mpl_image_compare
def test_histogram_2D(make_napari_viewer, astronaut_data):
    viewer = make_napari_viewer()
    viewer.add_image(astronaut_data[0], **astronaut_data[1])
    fig = HistogramWidget(viewer).figure
    # Need to return a copy, as original figure is too eagerley garbage
    # collected by the widget
    return deepcopy(fig)


@pytest.mark.mpl_image_compare
def test_histogram_3D(make_napari_viewer, brain_data):
    viewer = make_napari_viewer()
    viewer.add_image(brain_data[0], **brain_data[1])
    fig = HistogramWidget(viewer).figure
    # Need to return a copy, as original figure is too eagerley garbage
    # collected by the widget
    return deepcopy(fig)


def test_change_layer(make_napari_viewer, brain_data, astronaut_data):
    viewer = make_napari_viewer()
    widget = HistogramWidget(viewer)

    viewer.add_image(brain_data[0], **brain_data[1])
    viewer.add_image(astronaut_data[0], **astronaut_data[1])

    # Select first layer
    viewer.layers.selection.clear()
    viewer.layers.selection.add(viewer.layers[0])
    fig1 = deepcopy(widget.figure)

    # Re-selecting first layer should produce identical plot
    viewer.layers.selection.clear()
    viewer.layers.selection.add(viewer.layers[0])
    assert_figures_equal(widget.figure, fig1)

    # Plotting the second layer should produce a different plot
    viewer.layers.selection.clear()
    viewer.layers.selection.add(viewer.layers[1])
    assert_figures_not_equal(widget.figure, fig1)
