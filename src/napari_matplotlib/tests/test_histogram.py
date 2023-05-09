import pytest

from napari_matplotlib import HistogramWidget


@pytest.mark.mpl_image_compare
def test_example_q_widget(make_napari_viewer, image_data):
    # Smoke test adding a histogram widget
    viewer = make_napari_viewer()
    viewer.add_image(image_data[0], **image_data[1])
    fig = HistogramWidget(viewer).figure
    return fig
