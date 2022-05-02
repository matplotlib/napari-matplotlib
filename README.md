# napari-matplotlib

[![License](https://img.shields.io/pypi/l/napari-matplotlib.svg?color=green)](https://github.com/dstansby/napari-matplotlib/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-matplotlib.svg?color=green)](https://pypi.org/project/napari-matplotlib)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-matplotlib.svg?color=green)](https://python.org)
[![tests](https://github.com/dstansby/napari-matplotlib/workflows/tests/badge.svg)](https://github.com/dstansby/napari-matplotlib/actions)
[![codecov](https://codecov.io/gh/dstansby/napari-matplotlib/branch/main/graph/badge.svg)](https://codecov.io/gh/dstansby/napari-matplotlib)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-matplotlib)](https://napari-hub.org/plugins/napari-matplotlib)

A plugin to create Matplotlib plots from napari layers

----------------------------------

## Introduction
`napari-matplotlib` is a bridge between `napari` and `matplotlib`, making it easy to create publication quality `Matplotlib` plots based on the data loaded in `napari` layers.

Currently you can:

- Draw histograms of individual image layers
- Scatter plot two image layers against each other

Here's a demo of the scatter widget:

![](examples/short_scatter.gif)

## Installation

You can install `napari-matplotlib` via [pip]:

    pip install napari-matplotlib



To install latest development version :

    pip install git+https://github.com/dstansby/napari-matplotlib.git


## Contributing

Contributions are very welcome! Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [BSD-3] license,
`napari-matplotlib` is free and open source software.

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[@napari]: https://github.com/napari
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause

[file an issue]: https://github.com/dstansby/napari-matplotlib/issues

[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/
