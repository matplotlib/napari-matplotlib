from copy import deepcopy

import pytest

from napari_matplotlib import SliceWidget


@pytest.mark.mpl_image_compare
def test_slice(make_napari_viewer, brain_data):
    viewer = make_napari_viewer()
    viewer.add_image(brain_data[0], **brain_data[1])
    fig = SliceWidget(viewer).figure
    # Need to return a copy, as original figure is too eagerley garbage
    # collected by the widget
    return deepcopy(fig)
