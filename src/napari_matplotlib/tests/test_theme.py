import napari
import numpy as np
import pytest

from napari_matplotlib import ScatterWidget
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
    blue_theme = napari.utils.theme.get_theme("dark")
    blue_theme.label = "blue"
    blue_theme.background = "#4169e1"  # my favourite shade of blue
    napari.utils.theme.register_theme(
        "blue", blue_theme, source="napari-mpl-tests"
    )


def test_theme_background_check(make_napari_viewer):
    """
    Check that the hue saturation lightness can distinguish dark and light backgrounds.
    """
    viewer = make_napari_viewer()
    widget = NapariMPLWidget(viewer)

    viewer.theme = "dark"
    assert widget._napari_theme_has_light_bg() is False

    viewer.theme = "light"
    assert widget._napari_theme_has_light_bg() is True

    _mock_up_theme()
    viewer.theme = "blue"
    assert widget._napari_theme_has_light_bg() is True


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


@pytest.mark.mpl_image_compare
def test_no_theme_side_effects(make_napari_viewer):
    """Ensure that napari-matplotlib doesn't pollute the globally set style.

    A MWE to guard aganst issue matplotlib/#64. Should always reproduce a plot
    with the default matplotlib style.
    """
    import matplotlib.pyplot as plt

    np.random.seed(12345)

    # should not affect global matplotlib plot style
    viewer = make_napari_viewer()
    viewer.theme = "dark"
    NapariMPLWidget(viewer)

    # some plotting unrelated to napari-matplotlib
    normal_dist = np.random.normal(size=1000)
    unrelated_figure, ax = plt.subplots()
    ax.hist(normal_dist, bins=100)
    ax.set_xlabel("something unrelated to napari (x)")
    ax.set_ylabel("something unrelated to napari (y)")
    ax.set_title(
        "this plot style should not change with napari styles or themes"
    )
    unrelated_figure.tight_layout()

    return unrelated_figure
