import numpy as np

from napari_matplotlib import FeaturesScatterWidget, ScatterWidget


def test_scatter(make_napari_viewer):
    # Smoke test adding a scatter widget
    viewer = make_napari_viewer()
    viewer.add_image(np.random.random((100, 100)))
    viewer.add_image(np.random.random((100, 100)))
    ScatterWidget(viewer)


def test_features_scatter_widget(make_napari_viewer):
    # Smoke test adding a features scatter widget
    viewer = make_napari_viewer()
    viewer.add_image(np.random.random((100, 100)))
    viewer.add_labels(np.random.randint(0, 5, (100, 100)))
    FeaturesScatterWidget(viewer)


def make_labels_layer_with_features():
    label_image = np.zeros((100, 100), dtype=np.uint16)
    for label_value, start_index in enumerate([10, 30, 50], start=1):
        end_index = start_index + 10
        label_image[start_index:end_index, start_index:end_index] = label_value
    feature_table = {
        "index": [1, 2, 3],
        "feature_0": np.random.random((3,)),
        "feature_1": np.random.random((3,)),
        "feature_2": np.random.random((3,)),
    }
    return label_image, feature_table


def test_features_scatter_get_data(make_napari_viewer):
    """Test the get data method"""
    # make the label image
    label_image, feature_table = make_labels_layer_with_features()

    viewer = make_napari_viewer()
    labels_layer = viewer.add_labels(label_image, features=feature_table)
    scatter_widget = FeaturesScatterWidget(viewer)

    # select the labels layer
    viewer.layers.selection = [labels_layer]

    x_column = "feature_0"
    scatter_widget.x_axis_key = x_column
    y_column = "feature_2"
    scatter_widget.y_axis_key = y_column

    data, x_axis_name, y_axis_name = scatter_widget._get_data()
    np.testing.assert_allclose(
        data, np.stack((feature_table[x_column], feature_table[y_column]))
    )
    assert x_axis_name == x_column.replace("_", " ")
    assert y_axis_name == y_column.replace("_", " ")


def test_get_valid_axis_keys(make_napari_viewer):
    """Test the values returned from
    FeaturesScatterWidget._get_valid_keys() when there
    are valid keys.
    """
    # make the label image
    label_image, feature_table = make_labels_layer_with_features()

    viewer = make_napari_viewer()
    labels_layer = viewer.add_labels(label_image, features=feature_table)
    scatter_widget = FeaturesScatterWidget(viewer)

    viewer.layers.selection = [labels_layer]
    valid_keys = scatter_widget._get_valid_axis_keys()
    assert set(valid_keys) == set(feature_table.keys())


def test_get_valid_axis_keys_no_valid_keys(make_napari_viewer):
    """Test the values returned from
    FeaturesScatterWidget._get_valid_keys() when there
    are not valid keys.
    """
    # make the label image
    label_image, _ = make_labels_layer_with_features()

    viewer = make_napari_viewer()
    labels_layer = viewer.add_labels(label_image)
    image_layer = viewer.add_image(np.random.random((100, 100)))
    scatter_widget = FeaturesScatterWidget(viewer)

    # no features in a label image
    viewer.layers.selection = [labels_layer]
    valid_keys = scatter_widget._get_valid_axis_keys()
    assert set(valid_keys) == set()

    # image layer doesn't have features
    viewer.layers.selection = [image_layer]
    valid_keys = scatter_widget._get_valid_axis_keys()
    assert set(valid_keys) == set()
