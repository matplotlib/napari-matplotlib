# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))
from sphinx_gallery import scrapers

# -- Project information -----------------------------------------------------

project = "napari-matplotlib"
copyright = "2022, David Stansby"
author = "David Stansby"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "numpydoc",
    "sphinx_gallery.gen_gallery",
    "sphinx_automodapi.automodapi",
    "sphinx_automodapi.smart_resolver",
    "sphinx.ext.intersphinx",
]


def reset_napari(gallery_conf, fname):  # type: ignore[no-untyped-def]
    from napari.settings import get_settings
    from qtpy.QtWidgets import QApplication

    settings = get_settings()
    settings.appearance.theme = "dark"

    # Disabling `QApplication.exec_` means example scripts can call `exec_`
    # (scripts work when run normally) without blocking example execution by
    # sphinx-gallery. (from qtgallery)
    QApplication.exec_ = lambda _: None


def napari_scraper(block, block_vars, gallery_conf):  # type: ignore[no-untyped-def]
    """Basic napari window scraper.

    Looks for any QtMainWindow instances and takes a screenshot of them.

    `app.processEvents()` allows Qt events to propagateo and prevents hanging.
    """
    import napari

    imgpath_iter = block_vars["image_path_iterator"]

    if app := napari.qt.get_app():
        app.processEvents()
    else:
        return ""

    img_paths = []
    for win, img_path in zip(
        reversed(napari._qt.qt_main_window._QtMainWindow._instances),
        imgpath_iter,
    ):
        img_paths.append(img_path)
        win._window.screenshot(img_path, canvas_only=False)

    napari.Viewer.close_all()
    app.processEvents()

    return scrapers.figure_rst(img_paths, gallery_conf["src_dir"])


sphinx_gallery_conf = {
    "filename_pattern": ".",
    "image_scrapers": (napari_scraper,),
    "reset_modules": (reset_napari,),
}
suppress_warnings = ["config.cache"]


numpydoc_show_class_members = False
automodapi_inheritance_diagram = True
inheritance_graph_attrs = {"rankdir": "TR"}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "napari": ("https://napari.org/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "matplotlib": ("https://matplotlib.org/", None),
    "PyQT6": ("https://www.riverbankcomputing.com/static/Docs/PyQt6/", None),
}

nitpicky = True
# Can't work out how to link this properly using intersphinx and the PyQT6 docs.
# TODO: fix at some point
nitpick_ignore = [
    ("py:class", "PyQt5.QtWidgets.QWidget"),
    ("py:class", "PyQt5.QtCore.QObject"),
    ("py:class", "PyQt5.QtGui.QPaintDevice"),
    ("py:class", "sip.simplewrapper"),
    ("py:class", "sip.wrapper"),
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

default_role = "py:obj"

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"
html_logo = "_static/logo.png"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

html_theme_options = {
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/matplotlib/napari-matplotlib",
            "icon": "fa-brands fa-square-github",
            "type": "fontawesome",
        }
    ],
    "logo": {
        "text": "napari-matplotlib",
    },
}
