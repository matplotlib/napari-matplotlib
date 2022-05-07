import numpy as np

from napari_matplotlib import SliceWidget


def test_scatter(make_napari_viewer):
    # Smoke test adding a histogram widget
    viewer = make_napari_viewer()
    viewer.add_image(np.random.random((100, 100, 100)))
    SliceWidget(viewer)
