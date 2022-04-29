import napari

viewer = napari.Viewer()
viewer.open_sample("napari", "kidney")
viewer.window.add_plugin_dock_widget(
    plugin_name="napari-matplotlib", widget_name="Matplotlib histogram"
)

if __name__ == "__main__":
    # The napari event loop needs to be run under here to allow the window
    # to be spawned from a Python script
    napari.run()
