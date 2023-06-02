from copy import deepcopy

import pytest
from numpy import array

from napari_matplotlib import ScatterWidget


@pytest.mark.mpl_image_compare
def test_scatter_2D(make_napari_viewer, astronaut_data):
    viewer = make_napari_viewer()
    widget = ScatterWidget(viewer)
    fig = widget.figure

    viewer.add_image(astronaut_data[0], **astronaut_data[1], name="astronaut")

    viewer.add_image(
        astronaut_data[0] * -1, **astronaut_data[1], name="astronaut_reversed"
    )
    # De-select existing selection
    viewer.layers.selection.clear()

    # Select images
    viewer.layers.selection.add(viewer.layers[0])
    viewer.layers.selection.add(viewer.layers[1])
    return deepcopy(fig)


@pytest.mark.mpl_image_compare
def test_scatter_3D(make_napari_viewer, brain_data):
    viewer = make_napari_viewer()
    widget = ScatterWidget(viewer)
    fig = widget.figure

    viewer.add_image(brain_data[0], **brain_data[1], name="brain")

    viewer.add_image(
        brain_data[0] * -1, **brain_data[1], name="brain_reversed"
    )
    # De-select existing selection
    viewer.layers.selection.clear()
    axis = viewer.dims.last_used
    slice_no = array(brain_data[0]).shape[0] - 1
    viewer.dims.set_current_step(axis, slice_no)
    # Select images
    viewer.layers.selection.add(viewer.layers[0])
    viewer.layers.selection.add(viewer.layers[1])

    return deepcopy(fig)
