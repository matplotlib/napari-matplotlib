import importlib
import sys

import pytest
from qtpy.QtCore import QSize

from napari_matplotlib.util import Interval, from_napari_css_get_size_of


def test_version_fallback(mocker):
    """Test the versioning fallback (in case setuptools_scm didn't work)"""
    import napari_matplotlib  # fmt: skip

    assert napari_matplotlib.__version__ != "unknown"  # type: ignore[attr-defined]

    mocker.patch.dict(sys.modules, {"napari_matplotlib._version": None})
    importlib.reload(napari_matplotlib)
    assert napari_matplotlib.__version__ == "unknown"  # type: ignore[attr-defined]


def test_interval():
    interval = Interval(4, 9)
    for i in range(4, 10):
        assert i in interval

    assert 3 not in interval
    assert 10 not in interval

    with pytest.raises(ValueError, match="must be an integer"):
        assert "string" in interval  # type: ignore[operator]

    with pytest.raises(ValueError, match="must be <= upper_bound"):
        Interval(5, 3)


@pytest.mark.parametrize(
    "lower, upper, text",
    [
        (None, None, None),
        (1, None, "Select at least 1 layer to generate plot"),
        (4, None, "Select at least 4 layers to generate plot"),
        (None, 1, "Select at most 1 layer to generate plot"),
        (None, 5939, "Select at most 5939 layers to generate plot"),
        (1, 1, "Select 1 layer to generate plot"),
        (2, 2, "Select 2 layers to generate plot"),
        (1, 2, "Select between 1 and 2 layers to generate plot"),
    ],
)
def test_interval_helper_text(lower, upper, text):
    assert Interval(lower, upper)._helper_text == text


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
    assert from_napari_css_get_size_of("Flibble", (1, 2)) == QSize(123, 456)


def test_fallback_if_missing_dimensions(mocker):
    """Test fallback if given something that doesn't have dimensions"""
    test_css = " Flobble { background-color: rgb(0, 97, 163); } "
    mocker.patch("napari.qt.get_current_stylesheet").return_value = test_css
    with pytest.warns(RuntimeWarning, match="Unable to find DimensionToken"):
        with pytest.warns(RuntimeWarning, match="Unable to find Flobble"):
            assert from_napari_css_get_size_of("Flobble", (1, 2)) == QSize(1, 2)


def test_fallback_if_prelude_not_in_css():
    """Test fallback if given something not in the css"""
    doesntexist = "AQButtonThatDoesntExist"
    with pytest.warns(RuntimeWarning, match=f"Unable to find {doesntexist}"):
        assert from_napari_css_get_size_of(doesntexist, (1, 2)) == QSize(1, 2)
