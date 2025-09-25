Changelog
=========

4.0.0
-----
Dependencies
~~~~~~~~~~~~

- Dropped support for Python 3.10
- Added explicit support and testing for Python 3.13

3.0.1
-----
Bug fixes
~~~~~~~~~
- Fix an error that happened when changing the contrast limit when the histogram widget was open

3.0.0
-----
New features
~~~~~~~~~~~~
- Added a GUI element to manually set the number of bins in the histogram widgets.

2.0.3
-----
Bug fixes
~~~~~~~~~
- Fix an error that happened when the histogram widget was open, but a layer that doesn't support
  histogramming (e.g., a labels layer) was selected.

2.0.2
-----
Dependencies
~~~~~~~~~~~~
napari-matplotlib now adheres to `SPEC 0 <https://scientific-python.org/specs/spec-0000/>`_, and has:

- Dropped support for Python 3.9
- Added support for Python 3.12
- Added a minimum required numpy verison of 1.23
- Pinned the maximum napari version to ``< 0.5``.
  Version 3.0 of ``napari-matplotlib`` will introduce support for ``napari`` version 0.5.

2.0.1
-----
Bug fixes
~~~~~~~~~
- Fixed using the ``HistogramWidget`` with layers containing multiscale data.
- Make sure ``HistogramWidget`` uses 100 bins (not 99) when floating point data is
  selected.

2.0.0
-----
Changes to custom theming
~~~~~~~~~~~~~~~~~~~~~~~~~
``napari-matplotlib`` now uses colours from the current napari theme to customise the
Matplotlib plots. See `the example on creating a new napari theme
<https://napari.org/stable/gallery/new_theme.html>`_ for a helpful guide on how to
create custom napari themes.

This means support for custom Matplotlib styles sheets has been removed.

If you spot any issues with the new theming, please report them at
https://github.com/matplotlib/napari-matplotlib/issues.

Other changes
~~~~~~~~~~~~~
- Histogram bin sizes for integer-type data are now force to be an integer.
- The ``HistogramWidget`` now has two vertical lines showing the contrast limits used
  to render the selected layer in the main napari window.
- Added an example gallery for the ``FeaturesHistogramWidget``.

1.2.0
-----
Changes
~~~~~~~
- Dropped support for Python 3.8, and added support for Python 3.11.
- Histogram plots of points and vector layers are now coloured with their napari colourmap.
- Added support for Matplotlib 3.8

1.1.0
-----
Additions
~~~~~~~~~
- Added a widget to draw a histogram of features.

Changes
~~~~~~~
- The slice widget is now limited to slicing along the x/y dimensions. Support
  for slicing along z has been removed for now to make the code simpler.
- The slice widget now uses a slider to select the slice value.

Bug fixes
~~~~~~~~~
- Fixed creating 1D slices of 2D images.
- Removed the limitation that only the first 99 indices could be sliced using
  the slice widget.

1.0.2
-----
Bug fixes
~~~~~~~~~
- A full dataset is no longer read into memory when using ``HistogramWidget``.
  Only the current slice is loaded.
- Fixed compatibility with napari 0.4.18.

Changes
~~~~~~~
- Histogram bin limits are now caclualted from the slice being histogrammed, and
  not the whole dataset. This is as a result of the above bug fix.

1.0.1
-----
Bug fixes
~~~~~~~~~
- Pinned that maximum version of `napari` to 0.4.17, since ``napari-matplotlib``
  does not yet work with ``napari`` 0.4.18.

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
