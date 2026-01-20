import napari
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from napari_matplotlib.line import FeaturesLineWidget

labels = np.array([[0, 0, 1, 0],
                   [0, 2, 1, 0],
                   [2, 2, 2, 0],
                   [3, 3, 2, 0],
                   [0, 3, 0, 0]])
table = pd.DataFrame(data=np.array([np.array([1, 2, 3]), np.array([2, 5, 3]), np.array([0, 1, 0.5])]).T,
                     columns=['label', 'measurement1', 'measurement2'])

viewer = napari.Viewer()
viewer.add_labels(labels, features=table, name='labels')

plotter_widget = FeaturesLineWidget(viewer)
viewer.window.add_dock_widget(plotter_widget)

napari.run()
