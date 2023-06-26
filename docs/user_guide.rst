User guide
==========

Overview
--------
``napari-matplotlib`` contains a number of different ``napari`` Widgets. Each
widget is designed to map one or more ``napari`` Layers on to a ``matplotlib`` plot.
As an example, the `~.HistogramWidget` is used to
map one or more Image layers on to a 1D histogram plot.

The widgets split into two categories:

Layer plotting
~~~~~~~~~~~~~~
These widgets plot the data stored directly in napari layers.
Currently available are widgets to plot:

- 1D histograms
- 2D scatter plots (switching to 2D histograms for a large number of points)
- 1D slice line plots

To use these:

1. Open the desired widget using the ``Plugins > napari-matplotlib`` menu in napari.
2. Select the required number of layers using the napari layers list in the bottom left-hand side of the window.

Features plotting
~~~~~~~~~~~~~~~~~
These widgets plot the data stored in the ``.features`` attribute of individual napari layers.
Currently available are:

- 2D scatter plots of two features against each other.

To use these:

1. Open the desired widget using the ``Plugins > napari-matplotlib`` menu in napari.
2. Select a single layer that has a features table using the napari layers list in the bottom left-hand side of the window.
3. Use the drop down menu(s) under the Matplotlib figure to select the feature(s) to plot.
