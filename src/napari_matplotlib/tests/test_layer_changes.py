from copy import deepcopy
from typing import Any, Dict, Tuple, Type

import numpy as np
import numpy.typing as npt
import pytest
from napari.viewer import Viewer

from napari_matplotlib import (
    FeaturesScatterWidget,
    HistogramWidget,
    SliceWidget,
)
from napari_matplotlib.base import NapariMPLWidget
from napari_matplotlib.tests.helpers import (
    assert_figures_equal,
    assert_figures_not_equal,
)


@pytest.mark.parametrize("widget_cls", [HistogramWidget, SliceWidget])
def test_change_one_layer(
    make_napari_viewer, brain_data, astronaut_data, widget_cls
):
    """
    Test all widgets that take one layer as input to make sure the plot changes
    when the napari layer selection changes.
    """
    viewer = make_napari_viewer()
    assert_one_layer_plot_changes(
        viewer, widget_cls, brain_data, astronaut_data
    )


def assert_one_layer_plot_changes(
    viewer: Viewer,
    widget_cls: Type[NapariMPLWidget],
    data1: Tuple[npt.NDArray[np.generic], Dict[str, Any]],
    data2: Tuple[npt.NDArray[np.generic], Dict[str, Any]],
) -> None:
    """
    When the selected layer is changed, make sure the plot generated
    by `widget_cls` also changes.
    """
    widget = widget_cls(viewer)
    viewer.add_image(data1[0], **data1[1])
    viewer.add_image(data2[0], **data2[1])
    assert_plot_changes(viewer, widget)


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
    widget_cls: Type[NapariMPLWidget],
    data: Tuple[npt.NDArray[np.generic], Dict[str, Any]],
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
    assert_plot_changes(viewer, widget)


def assert_plot_changes(viewer: Viewer, widget: NapariMPLWidget) -> None:
    """
    Assert that a widget plot changes when the layer selection
    is changed. The passed viewer must already have two layers
    loaded.
    """
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
