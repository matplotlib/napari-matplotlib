from napari_matplotlib import FeatureHistogramWidget
import numpy as np

def test_example_q_widget(make_napari_viewer):
    # Smoke test adding a histogram widget
    viewer = make_napari_viewer()

    image = np.asarray([[0, 1], [2, 1]])
    labels = image.astype(int)


    viewer.add_image(image)

    labels_layer = viewer.add_labels(labels)

    labels_layer.features = {
        'labels': [1, 2],
        'area': [2, 1],
        'aspect_ratio': [2, 1]
    }

    FeatureHistogramWidget(viewer)
