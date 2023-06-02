from copy import deepcopy

import pytest

from napari_matplotlib import SliceWidget


@pytest.mark.mpl_image_compare
def test_slice_3D(make_napari_viewer, brain_data):
    viewer = make_napari_viewer()
    viewer.add_image(brain_data[0], **brain_data[1])
    axis = viewer.dims.last_used
    slice_no = 9
    viewer.dims.set_current_step(axis, slice_no)
    fig = SliceWidget(viewer).figure
    # Need to return a copy, as original figure is too eagerley garbage
    # collected by the widget
    return deepcopy(fig)


@pytest.mark.mpl_image_compare
def test_slice_2D(make_napari_viewer, astronaut_data):
    viewer = make_napari_viewer()
    viewer.add_image(astronaut_data[0], **astronaut_data[1])
    fig = SliceWidget(viewer).figure
    # Need to return a copy, as original figure is too eagerley garbage
    # collected by the widget
    return deepcopy(fig)
