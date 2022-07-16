import pytest

from napari_matplotlib.layer_selectors import (
    LayerListSelector,
    get_layer_selector,
)


def test_get_layer_selector_string():
    selector = get_layer_selector("LayerListSelector")

    assert selector is LayerListSelector


def test_get_layer_selector_object():
    selector = get_layer_selector(LayerListSelector)

    assert selector is LayerListSelector


def test_get_layer_selector_invalid():
    with pytest.raises(TypeError):
        _ = get_layer_selector(5)
