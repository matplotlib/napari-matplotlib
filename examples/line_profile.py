import napari
import numpy as np
from napari_matplotlib.line import LineWidget

viewer = napari.Viewer()
image = np.random.random((10, 10))
image2 = np.arange(100).reshape((10, 10))

line = np.array([[1, 1], [7, 4]])
viewer.add_image(image, colormap='green')
viewer.add_image(image2, colormap='magenta', blending='additive')
shapes_layer = viewer.add_shapes([line], shape_type='line', edge_width=1, edge_color='coral')

viewer.window.add_dock_widget(LineWidget(viewer), area='right')

napari.run()
