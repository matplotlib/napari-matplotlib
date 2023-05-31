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
