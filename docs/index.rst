napari-matplotlib
=================
``napari-matplotlib`` is a `Napari <https://napari.org>`_ plugin for generating
`Matplotlib <https://matplotlib.org/>`_ plots from one or more ``napari`` Layers.

Design
------
``napari-matplotlib`` contains a number of different ``napari`` Widgets. Each
widget is designed to map one or more ``napari`` Layers on to a ``matplotlib`` plot.
As an example, the `~.HistogramWidget` is used to
map one or more Image layers on to a 1D histogram plot.

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   auto_examples/index
   api
