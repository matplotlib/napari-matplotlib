Third-party plugins
===================
This page explains how ``napari-matplotlib`` can be used within third party plugins.

``napari-matplotlib`` provides a ready-to-go widget with a Matplotlib toolbar and figure to third party plugin developers
This widget is customised to match the theme of the main napari window.

The widget can be found at `napari_matplotlib.base.NapariMPLWidget`.
This class inherits from `~PyQt6.QtWidgets.QWidget`.

The recommended way to use `~napari_matplotlib.base.NapariMPLWidget` is inside a new widget, adding it to the layout.
This means you can add additional elements to your plugin layout alongside the Matplotlib figure.
Here's a short example:

.. code-block:: python

    from qtpy.QtWidgets import QWidget
    from napari_matplotlib.base import NapariMPLWidget

    class MyPlugin(QWidget):
        def __init__(self, napari_viewer: napari.viewer.Viewer, parent=None):
            super().__init__(parent=parent)

            # Any custom setup for your custom widget
            ...

            # Set up the plot widget
            plot_widget =  NapariMPLWidget(napari_viewer, parent=self)
            self.layout().addWidget(plot_widget)

The following properties and methods are useful for working with the figure and any axes within the widget:

- `~.BaseNapariMPLWidget.figure` provides access to the figure
- :meth:`~.BaseNapariMPLWidget.add_single_axes` adds a single axes to the figure, which can be accessed using the ``.axes`` attribute.
- :meth:`~.BaseNapariMPLWidget.apply_napari_colorscheme` can be used to apply the napari colorscheme to any Axes you setup manually on the figure.

Working with napari layers
--------------------------
When either the layer selection or z-step in the napari viewer is changed
:meth:`~.NapariMPLWidget.clear` and :meth:`~.NapariMPLWidget.draw` are called
in turn. By default these do nothing, and are designed to be overriden by
plugins to automatically re-draw any figures within the widget. Plugins can
also override :meth:`~.NapariMPLWidget.on_update_layers` to do something when
the layer selection changes. This can be used to do something without clearing
or re-drawing any plots.

Validating layer numbers and types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
By default :meth:`~.NapariMPLWidget.draw` will be called when any number of any
type of napari layers are selected. The `~.NapariMPLWidget.n_layers_input`
and `~.NapariMPLWidget.input_layer_types` class variables can be overriden to
specify the number of selected napari layers and valid layer
types that are taken as input. If the number of selected layers and their
types do not match up with these class variables, no re-draw is called.
