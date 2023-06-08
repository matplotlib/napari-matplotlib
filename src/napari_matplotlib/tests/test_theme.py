import shutil
from pathlib import Path

import matplotlib
import napari
import numpy as np
import pytest
from matplotlib.colors import to_rgba

from napari_matplotlib import HistogramWidget, ScatterWidget
from napari_matplotlib.base import NapariMPLWidget


@pytest.mark.parametrize(
    "theme_name, expected_icons",
    [("dark", "white"), ("light", "black")],
)
def test_theme_mpl_toolbar_icons(
    make_napari_viewer, theme_name, expected_icons
):
    """Check that the icons are taken from the correct folder for each napari theme."""
    viewer = make_napari_viewer()
    viewer.theme = theme_name
    path_to_icons = NapariMPLWidget(viewer)._get_path_to_icon()
    assert path_to_icons.exists(), "The theme points to non-existant icons."
    assert (
        path_to_icons.stem == expected_icons
    ), "The theme is selecting unexpected icons."


def _mock_up_theme() -> None:
    """Mock up a new color theme based on dark mode but with a tasteful blue background.

    Based on:
    https://napari.org/stable/gallery/new_theme.html
    """
    blue_theme = napari.utils.theme.get_theme("dark", False)
    blue_theme.name = "blue"
    blue_theme.background = "#4169e1"  # my favourite shade of blue
    napari.utils.theme.register_theme("blue", blue_theme)


def test_theme_background_check(make_napari_viewer):
    """
    Check that the hue saturation lightness can distinguish dark and light backgrounds.
    """
    viewer = make_napari_viewer()
    widget = NapariMPLWidget(viewer)

    viewer.theme = "dark"
    assert widget._theme_has_light_bg() is False

    viewer.theme = "light"
    assert widget._theme_has_light_bg() is True

    _mock_up_theme()
    with pytest.warns(UserWarning, match="theme 'blue' is not supported"):
        viewer.theme = "blue"
        assert widget._theme_has_light_bg() is True


def test_unknown_theme_raises_warning(make_napari_viewer):
    """
    Check that widget construction warns if it doesn't recognise napari's theme.

    Note that testing for the expected warning when theme is changed _after_ the
    widget is created is part of ``test_theme_background_check``.
    """
    viewer = make_napari_viewer()
    _mock_up_theme()  # creates the 'blue' theme which is not a standard napari theme
    viewer.theme = "blue"
    with pytest.warns(UserWarning, match="theme 'blue' is not supported"):
        HistogramWidget(viewer)


@pytest.mark.parametrize(
    "theme_name, expected_text_colour",
    [
        ("dark", "#f0f1f2"),  # #f0f1f2 is a light grey (almost white)
        ("light", "#3b3a39"),  # #3b3a39 is a brownish dark grey (almost black)
    ],
)
def test_titles_respect_theme(
    make_napari_viewer, theme_name, expected_text_colour
):
    """
    Test that the axis labels and titles are the correct color for the napari theme.
    """
    viewer = make_napari_viewer()
    widget = ScatterWidget(viewer)
    viewer.theme = theme_name

    # make a scatter plot of two random layers
    viewer.add_image(np.random.random((10, 10)), name="first test image")
    viewer.add_image(np.random.random((10, 10)), name="second test image")
    viewer.layers.selection.clear()
    viewer.layers.selection.add(viewer.layers[0])
    viewer.layers.selection.add(viewer.layers[1])

    ax = widget.figure.gca()

    # sanity test to make sure we've got the correct image names
    assert ax.xaxis.label.get_text() == "first test image"
    assert ax.yaxis.label.get_text() == "second test image"

    # print(dir(ax.yaxis.label))
    # TODO: put checks of the axis tick labels here

    assert ax.xaxis.label.get_color() == expected_text_colour
    assert ax.yaxis.label.get_color() == expected_text_colour


def find_mpl_stylesheet(name: str) -> Path:
    """Find the built-in matplotlib stylesheet."""
    return Path(matplotlib.__path__[0]) / f"mpl-data/stylelib/{name}.mplstyle"


def test_stylesheet_in_cwd(tmpdir, make_napari_viewer, image_data):
    """
    Test that a stylesheet in the current directory is given precidence.

    Do this by copying over a stylesheet from matplotlib's built in styles,
    naming it correctly, and checking the colours are as expected.
    """
    with tmpdir.as_cwd():
        # Copy Solarize_Light2 to current dir as if it was a user-overriden stylesheet.
        shutil.copy(find_mpl_stylesheet("Solarize_Light2"), "./user.mplstyle")
        viewer = make_napari_viewer()
        viewer.add_image(image_data[0], **image_data[1])
        widget = HistogramWidget(viewer)
        ax = widget.figure.gca()

        # The axes should have a light brownish grey background:
        assert ax.get_facecolor() == to_rgba("#eee8d5")
        assert ax.patch.get_facecolor() == to_rgba("#eee8d5")

        # The figure background and axis gridlines are light yellow:
        assert widget.figure.patch.get_facecolor() == to_rgba("#fdf6e3")
        for gridline in ax.get_xgridlines() + ax.get_ygridlines():
            assert gridline.get_visible() is True
            assert gridline.get_color() == "#fdf6e3"
