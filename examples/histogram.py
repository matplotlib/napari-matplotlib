"""
Histograms
==========
"""
import napari
from skimage import data

viewer = napari.Viewer()
viewer.add_image(data.brain())

viewer.window.add_plugin_dock_widget(
    plugin_name="napari-matplotlib", widget_name="Histogram"
)

if __name__ == "__main__":
    napari.run()
