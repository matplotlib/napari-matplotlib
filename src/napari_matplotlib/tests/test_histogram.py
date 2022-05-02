import numpy as np
import pytest

from napari_matplotlib import HistogramWidget


# Test with 2D and 3D data
@pytest.mark.parametrize(
    "data", [np.random.random((100, 100)), np.random.random((100, 100, 100))]
)
def test_example_q_widget(make_napari_viewer, data):
    # Smoke test adding a histogram widget
    viewer = make_napari_viewer()
    viewer.add_image(data)
    HistogramWidget(viewer)
