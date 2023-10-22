from copy import deepcopy
from typing import Any

import numpy as np
import numpy.typing as npt
import pytest
from napari.viewer import Viewer

from napari_matplotlib import (
    FeaturesScatterWidget,
    HistogramWidget,
    ScatterWidget,
    SliceWidget,
)
from napari_matplotlib.base import NapariMPLWidget
from napari_matplotlib.tests.helpers import (
    assert_figures_equal,
    assert_figures_not_equal,
)


@pytest.mark.parametrize(
    "widget_cls, n_layers",
    [(HistogramWidget, 1), (SliceWidget, 1), (ScatterWidget, 2)],
)
def test_change_one_layer(
    make_napari_viewer,
    brain_data,
    astronaut_data,
    widget_cls,
    n_layers,
):
    """
    Test all widgets that take one layer as input to make sure the plot changes
    when the napari layer selection changes.
    """
    viewer = make_napari_viewer()

    widget = widget_cls(viewer)
    # Add n copies of two different datasets
    for _ in range(n_layers):
        viewer.add_image(brain_data[0], **brain_data[1])
    for _ in range(n_layers):
        viewer.add_image(astronaut_data[0], **astronaut_data[1])

    assert len(viewer.layers) == 2 * n_layers
    assert_plot_changes(viewer, widget, n_layers=n_layers)


@pytest.mark.parametrize("widget_cls", [FeaturesScatterWidget])
def test_change_features_layer(
    make_napari_viewer, points_with_features_data, widget_cls
):
    """
    Test all widgets that take one layer with features as input to make sure the
    plot changes when the napari layer selection changes.
    """
    viewer = make_napari_viewer()
    assert_features_plot_changes(viewer, widget_cls, points_with_features_data)


def assert_features_plot_changes(
    viewer: Viewer,
    widget_cls: type[NapariMPLWidget],
    data: tuple[npt.NDArray[np.generic], dict[str, Any]],
) -> None:
    """
    When the selected layer is changed, make sure the plot generated
    by `widget_cls` also changes.
    """
    widget = widget_cls(viewer)
    viewer.add_points(data[0], **data[1])
    # Change the features data for the second layer
    data[1]["features"] = {
        name: data + 1 for name, data in data[1]["features"].items()
    }
    viewer.add_points(data[0], **data[1])
    assert_plot_changes(viewer, widget, n_layers=1)


def assert_plot_changes(
    viewer: Viewer, widget: NapariMPLWidget, *, n_layers: int
) -> None:
    """
    Assert that a widget plot changes when the layer selection
    is changed. The passed viewer must already have (2 * n_layers) layers
    loaded.
    """
    # Select first layer(s)
    viewer.layers.selection.clear()

    for i in range(n_layers):
        viewer.layers.selection.add(viewer.layers[i])
    assert len(viewer.layers.selection) == n_layers
    fig1 = deepcopy(widget.figure)

    # Re-selecting first layer(s) should produce identical plot
    viewer.layers.selection.clear()
    for i in range(n_layers):
        viewer.layers.selection.add(viewer.layers[i])
    assert len(viewer.layers.selection) == n_layers
    assert_figures_equal(widget.figure, fig1)

    # Plotting the second layer(s) should produce a different plot
    viewer.layers.selection.clear()
    for i in range(n_layers):
        viewer.layers.selection.add(viewer.layers[n_layers + i])
    assert len(viewer.layers.selection) == n_layers
    assert_figures_not_equal(widget.figure, fig1)
