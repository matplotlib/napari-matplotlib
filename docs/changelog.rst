Changelog
=========

1.0.0
-----

New features
~~~~~~~~~~~~
- Added ``MPLWidget`` as a widget containing just a Matplotlib canvas
  without any association with a napari viewer.
- Added text to each widget indicating how many layers need to be selected
  for the widget to plot something.

Visual improvements
~~~~~~~~~~~~~~~~~~~
- The background of ``napari-matplotlib`` figures and axes is now transparent, and the text and axis colour respects the ``napari`` theme.
- The icons in the Matplotlib toolbar are now the same size as icons in the napari window.
- Custom style sheets can now be set to customise plots. See the user guide
  for more information.

Changes
~~~~~~~
- The scatter widgets no longer use a LogNorm() for 2D histogram scaling.
  This is to move the widget in line with the philosophy of using Matplotlib default
  settings throughout ``napari-matplotlib``. This still leaves open the option of
  adding the option to change the normalization in the future. If this is something
  you would be interested in please open an issue at https://github.com/matplotlib/napari-matplotlib.
- Labels plotting with the features scatter widget no longer have underscores
  replaced with spaces.
- ``NapariMPLWidget.update_layers()`` has been removed as it is intended to be
  private API. Use ``NapariMPLWidget.on_update_layers`` instead to implement
  funcitonality when layer selection is changed.
- The slice widget now only plots x-ticks at integer locations.

Bug fixes
~~~~~~~~~
- Importing ``napari-matplotlib`` no longer affects how plots are rendered in
  Jupyter notebooks.

Other
~~~~~
- ``napari-matplotlib`` is now tested on macOS and Windows.
- Type annotations have been completed throughout the code base.
