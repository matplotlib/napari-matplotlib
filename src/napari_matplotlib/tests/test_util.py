import pytest
from qtpy.QtCore import QSize

from napari_matplotlib.util import Interval, from_css_get_size_of


def test_interval():
    interval = Interval(4, 9)
    for i in range(4, 10):
        assert i in interval

    assert 3 not in interval
    assert 10 not in interval

    with pytest.raises(ValueError, match="must be an integer"):
        "string" in interval  # type: ignore


def test_get_size_from_css(mocker):
    """Test getting the max-width and max-height from something in css"""
    test_css = """
        Flibble {
            min-width : 0;
            max-width : 123px;
            min-height : 0px;
            max-height : 456px;
            padding: 0px;
        }
        """
    mocker.patch("napari.qt.get_current_stylesheet").return_value = test_css
    assert from_css_get_size_of("Flibble", (1, 1)) == QSize(123, 456)


def test_fallback_if_missing_dimensions(mocker):
    """Test fallback if given something that doesn't have dimensions"""
    test_css = " Flobble { background-color: rgb(0, 97, 163); } "
    mocker.patch("napari.qt.get_current_stylesheet").return_value = test_css
    assert from_css_get_size_of("Flobble", (1, 1)) == QSize(1, 1)


def test_fallback_if_prelude_not_in_css():
    """Test fallback if given something not in the css"""
    assert from_css_get_size_of("AQButtonThatDoesntExist", (1, 1)) == QSize(
        1, 1
    )
