import pytest
from qtpy.QtCore import QSize
from qtpy.QtGui import QImage

from napari_matplotlib import HistogramWidget, ScatterWidget, SliceWidget


def _are_different(a: QImage, b: QImage) -> bool:
    """
    Check that a and b are identical, pixel by pixel. Via a stupid nested for loop.
    """
    assert not a.isNull()
    assert not b.isNull()
    assert a.size() == b.size()
    for x in range(a.width()):
        for y in range(a.height()):
            if a.pixel(x, y) != b.pixel(x, y):
                return True  # exit quickly
    return False


@pytest.mark.parametrize("Widget", [HistogramWidget, ScatterWidget, SliceWidget])
def test_mpl_toolbar_buttons_checked(make_napari_viewer, Widget):
    """Test that the icons for checkable actions change when when a tool is selected.

    A simple test of NapariNavigationToolbar._update_buttons_checked. Make sure the
    checked and unchecked icons are not the same.
    """
    checkable_actions = ["Zoom", "Pan"]

    viewer = make_napari_viewer()
    widget = Widget(viewer)

    # search through all of the icons for the ones whose icons are expected to
    # change when checked
    for action in widget.toolbar.actions():
        if action.text() in checkable_actions:
            assert action.isChecked() is False
            assert action.isCheckable() is True
            unchecked = action.icon().pixmap(QSize(48, 48)).toImage()

            # simulate the user click (QTest.mouseClick can't take a QAction)
            action.trigger()

            assert action.isChecked() is True
            checked = action.icon().pixmap(QSize(48, 48)).toImage()
            assert _are_different(unchecked, checked)
