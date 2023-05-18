Changelog
=========

0.4.0
-----

Changes
~~~~~~~
- The scatter widgets no longer use a LogNorm() for 2D histogram scaling.
  This is to move the widget in line with the philosophy of using Matplotlib default
  settings throughout ``napari-matplotlib``. This still leaves open the option of
  adding the option to change the normalization in the future. If this is something
  you would be interested in please open an issue at https://github.com/matplotlib/napari-matplotlib.
- Labels plotting with the features scatter widget no longer have underscores
  replaced with spaces.
