from napari_matplotlib import HistogramWidget


def test_example_q_widget(make_napari_viewer, image_data):
    # Smoke test adding a histogram widget
    viewer = make_napari_viewer()
    viewer.add_image(image_data[0], **image_data[1])
    HistogramWidget(viewer)
