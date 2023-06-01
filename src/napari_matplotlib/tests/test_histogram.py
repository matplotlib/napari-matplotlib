from napari_matplotlib import HistogramWidget, FeaturesHistogramWidget


def test_example_q_widget(make_napari_viewer, image_data):
    # Smoke test adding a histogram widget
    viewer = make_napari_viewer()
    viewer.add_image(image_data[0], **image_data[1])
    HistogramWidget(viewer)

def test_feature_histogram(make_napari_viewer):

    import numpy as np

    n_points = 1000
    random_points = np.random.random((n_points,3))*10
    feature1 = np.random.random(n_points)
    feature2 = np.random.normal(size=n_points)

    viewer = make_napari_viewer()
    viewer.add_points(random_points, properties={'feature1': feature1, 'feature2': feature2}, face_color='feature1', size=1)

    widget = FeaturesHistogramWidget(viewer)
    viewer.window.add_dock_widget(widget)
    widget._set_axis_keys('feature1')
    widget._key_selection_widget()
    widget._set_axis_keys('feature2')
    widget._key_selection_widget()
