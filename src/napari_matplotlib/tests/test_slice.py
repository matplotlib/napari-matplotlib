from copy import deepcopy

import pytest

from napari_matplotlib import SliceWidget


@pytest.mark.mpl_image_compare
def test_slice_3D(make_napari_viewer, brain_data):
    viewer = make_napari_viewer()
    viewer.theme = "light"

    data = brain_data[0]
    assert data.ndim == 3, data.shape
    viewer.add_image(data, **brain_data[1])

    axis = viewer.dims.last_used
    slice_no = data.shape[0] - 1
    viewer.dims.set_current_step(axis, slice_no)
    fig = SliceWidget(viewer).figure
    # Need to return a copy, as original figure is too eagerley garbage
    # collected by the widget
    return deepcopy(fig)


@pytest.mark.mpl_image_compare
def test_slice_2D(make_napari_viewer, astronaut_data):
    viewer = make_napari_viewer()
    viewer.theme = "light"

    # Take first RGB channel
    data = astronaut_data[0][:, :, 0]
    assert data.ndim == 2, data.shape
    viewer.add_image(data)

    fig = SliceWidget(viewer).figure
    # Need to return a copy, as original figure is too eagerley garbage
    # collected by the widget
    return deepcopy(fig)
