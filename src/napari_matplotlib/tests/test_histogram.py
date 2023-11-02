from copy import deepcopy

import numpy as np
import pytest

from napari_matplotlib import FeaturesHistogramWidget, HistogramWidget
from napari_matplotlib.tests.helpers import (
    assert_figures_equal,
    assert_figures_not_equal,
)


@pytest.mark.mpl_image_compare
def test_histogram_2D(make_napari_viewer, astronaut_data):
    viewer = make_napari_viewer()
    viewer.theme = "light"
    viewer.add_image(astronaut_data[0], **astronaut_data[1])
    fig = HistogramWidget(viewer).figure
    # Need to return a copy, as original figure is too eagerley garbage
    # collected by the widget
    return deepcopy(fig)


@pytest.mark.mpl_image_compare
def test_histogram_3D(make_napari_viewer, brain_data):
    viewer = make_napari_viewer()
    viewer.theme = "light"
    viewer.add_image(brain_data[0], **brain_data[1])
    axis = viewer.dims.last_used
    slice_no = brain_data[0].shape[0] - 1
    viewer.dims.set_current_step(axis, slice_no)
    fig = HistogramWidget(viewer).figure
    # Need to return a copy, as original figure is too eagerley garbage
    # collected by the widget
    return deepcopy(fig)


def test_feature_histogram(make_napari_viewer):
    n_points = 1000
    random_points = np.random.random((n_points, 3)) * 10
    random_directions = np.random.random((n_points, 3)) * 10
    random_vectors = np.stack([random_points, random_directions], axis=1)
    feature1 = np.random.random(n_points)
    feature2 = np.random.normal(size=n_points)

    viewer = make_napari_viewer()
    viewer.add_points(
        random_points,
        properties={"feature1": feature1, "feature2": feature2},
        name="points1",
    )
    viewer.add_vectors(
        random_vectors,
        properties={"feature1": feature1, "feature2": feature2},
        name="vectors1",
    )

    widget = FeaturesHistogramWidget(viewer)
    viewer.window.add_dock_widget(widget)

    # Check whether changing the selected key changes the plot
    widget._set_axis_keys("feature1")
    fig1 = deepcopy(widget.figure)

    widget._set_axis_keys("feature2")
    assert_figures_not_equal(widget.figure, fig1)

    # check whether selecting a different layer produces the same plot
    viewer.layers.selection.clear()
    viewer.layers.selection.add(viewer.layers[1])
    assert_figures_equal(widget.figure, fig1)


@pytest.mark.mpl_image_compare
def test_feature_histogram_vectors(make_napari_viewer):
    n_points = 1000
    np.random.seed(42)
    random_points = np.random.random((n_points, 3)) * 10
    random_directions = np.random.random((n_points, 3)) * 10
    random_vectors = np.stack([random_points, random_directions], axis=1)
    feature1 = np.random.random(n_points)

    viewer = make_napari_viewer()
    viewer.add_vectors(
        random_vectors,
        properties={"feature1": feature1},
        name="vectors1",
    )

    widget = FeaturesHistogramWidget(viewer)
    viewer.window.add_dock_widget(widget)
    widget._set_axis_keys("feature1")

    fig = FeaturesHistogramWidget(viewer).figure
    return deepcopy(fig)


@pytest.mark.mpl_image_compare
def test_feature_histogram_points(make_napari_viewer):
    np.random.seed(0)
    n_points = 1000
    random_points = np.random.random((n_points, 3)) * 10
    feature1 = np.random.random(n_points)

    viewer = make_napari_viewer()
    viewer.add_points(
        random_points,
        properties={"feature1": feature1},
        name="points1",
    )

    widget = FeaturesHistogramWidget(viewer)
    viewer.window.add_dock_widget(widget)
    widget._set_axis_keys("feature1")

    fig = FeaturesHistogramWidget(viewer).figure
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
