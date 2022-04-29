"""
Histograms
==========
"""
import napari
from skimage import data

from napari_matplotlib import HistogramWidget

viewer = napari.Viewer()
viewer.add_image(data.brain())

widget = HistogramWidget(viewer)
widget
