from copy import deepcopy

import pytest

from napari_matplotlib import ScatterBaseWidget, ScatterWidget


@pytest.mark.mpl_image_compare
def test_scatter_2D(make_napari_viewer, astronaut_data):
    viewer = make_napari_viewer()
    viewer.theme = "light"
    widget = ScatterWidget(viewer)
    fig = widget.figure

    viewer.add_image(astronaut_data[0], **astronaut_data[1], name="astronaut")

    viewer.add_image(
        255 - astronaut_data[0], **astronaut_data[1], name="astronaut_reversed"
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
    viewer.theme = "light"
    widget = ScatterWidget(viewer)
    fig = widget.figure

    viewer.add_image(brain_data[0], **brain_data[1], name="brain")

    viewer.add_image(
        255 -brain_data[0], **brain_data[1], name="brain_reversed"
    )
    # De-select existing selection
    viewer.layers.selection.clear()
    axis = viewer.dims.last_used
    slice_no = brain_data[0].shape[0] - 1
    viewer.dims.set_current_step(axis, slice_no)
    # Select images
    viewer.layers.selection.add(viewer.layers[0])
    viewer.layers.selection.add(viewer.layers[1])

    return deepcopy(fig)


def test_get_data_notimplemented_on_base(make_napari_viewer):
    viewer = make_napari_viewer()
    widget = ScatterBaseWidget(viewer)
    with pytest.raises(NotImplementedError):
        widget._get_data()
