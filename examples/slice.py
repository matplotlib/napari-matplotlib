"""
1D slices
=========
"""
import napari

viewer = napari.Viewer()
viewer.open_sample("napari", "kidney")

viewer.window.add_plugin_dock_widget(
    plugin_name="napari-matplotlib", widget_name="1D slice"
)

if __name__ == "__main__":
    napari.run()
