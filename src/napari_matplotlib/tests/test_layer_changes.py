from copy import deepcopy
from typing import Any, Dict, Tuple, Type

import numpy as np
import numpy.typing as npt
import pytest
from napari.viewer import Viewer

from napari_matplotlib import HistogramWidget, SliceWidget
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
