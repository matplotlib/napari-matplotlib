import napari
import pytest

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
    """Check that the hue, saturation, lightness can distinguish dark and light backgrounds."""
    viewer = make_napari_viewer()
    widget = NapariMPLWidget(viewer)

    viewer.theme = "dark"
    assert widget._theme_has_light_bg() is False

    viewer.theme = "light"
    assert widget._theme_has_light_bg() is True

    _mock_up_theme()
    viewer.theme = "blue"
    assert widget._theme_has_light_bg() is True
