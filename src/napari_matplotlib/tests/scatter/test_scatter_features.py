from copy import deepcopy
from typing import Any, Dict, Tuple

import numpy as np
import numpy.typing as npt
import pytest

from napari_matplotlib import FeaturesScatterWidget


@pytest.mark.mpl_image_compare
def test_features_scatter_widget_2D(
    make_napari_viewer, points_with_features_data
):
    viewer = make_napari_viewer()
    viewer.theme = "light"
    widget = FeaturesScatterWidget(viewer)

    viewer.add_points(
        points_with_features_data[0], **points_with_features_data[1]
    )
    assert len(viewer.layers) == 1
    # De-select existing selection
    viewer.layers.selection.clear()

    # Select points data and chosen features
    viewer.layers.selection.add(viewer.layers[0])  # images need to be selected
    widget.set_key("x", "feature_0")
    widget.set_key("y", "feature_1")

    fig = widget.figure

    return deepcopy(fig)


def make_labels_layer_with_features() -> (
    Tuple[npt.NDArray[np.uint16], Dict[str, Any]]
):
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
    """
    Test the get data method.
    """
    # make the label image
    label_image, feature_table = make_labels_layer_with_features()

    viewer = make_napari_viewer()
    labels_layer = viewer.add_labels(label_image, features=feature_table)
    scatter_widget = FeaturesScatterWidget(viewer)

    # select the labels layer
    viewer.layers.selection = [labels_layer]

    x_column = "feature_0"
    y_column = "feature_2"
    scatter_widget.set_key("x", x_column)
    scatter_widget.set_key("y", y_column)

    x, y, x_axis_name, y_axis_name = scatter_widget._get_data()
    np.testing.assert_allclose(x, feature_table[x_column])
    np.testing.assert_allclose(y, np.stack(feature_table[y_column]))
    assert x_axis_name == x_column
    assert y_axis_name == y_column


def test_get_valid_axis_keys(make_napari_viewer):
    """
    Test the values returned from _get_valid_keys() when there
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
