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


def test_slice_axes(make_napari_viewer, astronaut_data):
    viewer = make_napari_viewer()
    viewer.theme = "light"

    # Take first RGB channel
    data = astronaut_data[0][:256, :, 0]
    # Shape:
    # x: 0 > 512
    # y: 0 > 256
    assert data.ndim == 2, data.shape
    # Make sure data isn't square for later tests
    assert data.shape[0] != data.shape[1]
    viewer.add_image(data)

    widget = SliceWidget(viewer)
    assert widget._dim_names == ["y", "x"]
    assert widget.current_dim_name == "x"
    assert widget.slice_selector.value() == 0
    assert widget.slice_selector.minimum() == 0
    assert widget.slice_selector.maximum() == data.shape[0]
    # x/y are flipped in napari
    assert widget._slice_width == data.shape[1]
