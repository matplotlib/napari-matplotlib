from typing import Generator, List, Optional, Tuple, Union
from warnings import warn

import napari.qt
import tinycss2
from qtpy.QtCore import QSize


class Interval:
    """
    An integer interval.
    """

    def __init__(self, lower_bound: Optional[int], upper_bound: Optional[int]):
        """
        Parameters
        ----------
        lower_bound, upper_bound:
            Bounds. Use `None` to specify an open bound.
        """
        if (
            lower_bound is not None
            and upper_bound is not None
            and lower_bound > upper_bound
        ):
            raise ValueError("lower_bound must be <= upper_bound")

        self.lower = lower_bound
        self.upper = upper_bound

    def __repr__(self) -> str:
        """
        Get string representation.
        """
        return f"Interval({self.lower}, {self.upper})"

    def __contains__(self, val: int) -> bool:
        """
        Return True if val is in the current interval.
        """
        if not isinstance(val, int):
            raise ValueError("variable must be an integer")
        if self.lower is not None and val < self.lower:
            return False
        if self.upper is not None and val > self.upper:
            return False
        return True


def _logical_lines(
    nodes: List[tinycss2.ast.Node],
) -> Generator[Tuple[tinycss2.ast.Node, tinycss2.ast.Node], None, None]:
    """Generator to provide logical lines (thing: value) of css (terminated by ';')"""
    ident, dimension = None, None
    for node in nodes:
        if node == ";":
            yield (ident, dimension)
            ident, dimension = None, None
        elif node.type == "ident":
            ident = node
        elif node.type == "dimension":
            dimension = node


def _has_id(nodes: List[tinycss2.ast.Node], id_name: str) -> bool:
    """
    Is `id_name` in IdentTokens in the list of CSS `nodes`?
    """
    return any(
        [node.type == "ident" and node.value == id_name for node in nodes]
    )


def _get_dimension(
    nodes: List[tinycss2.ast.Node], id_name: str
) -> Union[int, None]:
    """
    Get the value of the DimensionToken for the IdentToken `id_name`.

    Returns
    -------
        None if no IdentToken is found.
    """
    for name, value in _logical_lines(nodes):
        if name.value == id_name:
            return value.int_value
    warn(f"Unable to find DimensionToken for {id_name}", RuntimeWarning)
    return None


def from_napari_css_get_size_of(
    qt_element_name: str, fallback: Tuple[int, int]
) -> QSize:
    """
    Get the size of `qt_element_name` from napari's current stylesheet.

    TODO: Confirm that the napari.qt.get_current_stylesheet changes with napari
          theme (docs seem to indicate it should)

    Returns
    -------
        QSize of the element if it's found, the `fallback` if it's not found..
    """
    rules = tinycss2.parse_stylesheet(
        napari.qt.get_current_stylesheet(),
        skip_comments=True,
        skip_whitespace=True,
    )
    w, h = None, None
    for rule in rules:
        if _has_id(rule.prelude, qt_element_name):
            w = _get_dimension(rule.content, "max-width")
            h = _get_dimension(rule.content, "max-height")
            if w and h:
                return QSize(w, h)
    warn(
        f"Unable to find {qt_element_name} or unable to find its size in "
        f"the current Napari stylesheet, falling back to {fallback}",
        RuntimeWarning,
    )
    return QSize(*fallback)
