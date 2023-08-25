from copy import deepcopy

import numpy as np
import pytest

from napari_matplotlib import FeatureHistogramWidget


@pytest.mark.mpl_image_compare
def test_feature_histogram(make_napari_viewer):
    # Smoke test adding a histogram widget
    viewer = make_napari_viewer()
    viewer.theme = "light"

    image = np.asarray([[0, 1], [2, 1]])

    viewer.add_image(image)
    labels_layer = viewer.add_labels(image.astype(int))
    labels_layer.features = {
        "labels": [1, 2],
        "area": [2, 1],
        "aspect_ratio": [2, 1],
    }

    fig = FeatureHistogramWidget(viewer).figure
    return deepcopy(fig)
