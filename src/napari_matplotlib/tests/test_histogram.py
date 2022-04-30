import numpy as np

from napari_matplotlib import HistogramWidget


def test_example_q_widget(make_napari_viewer):
    # Smoke test adding a histogram widget
    viewer = make_napari_viewer()
    viewer.add_image(np.random.random((100, 100)))
    HistogramWidget(viewer)
