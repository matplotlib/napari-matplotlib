import napari
from pathlib import Path
from napari_matplotlib.base import NapariMPLWidget

click_icon_file_path = (Path(__file__).parent.parent / "src/napari_matplotlib/icons/black/Forward.png").__str__()


def on_click():
    print("clicked")


viewer = napari.Viewer()

plotter = NapariMPLWidget(viewer)
plotter.toolbar._add_new_button(
    'click', "Print click", click_icon_file_path, on_click, False)

viewer.window.add_dock_widget(plotter)

napari.run()
