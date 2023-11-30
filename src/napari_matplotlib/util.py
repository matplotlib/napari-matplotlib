from typing import Dict, Optional, Union
from warnings import warn

import napari.qt
import tinycss2
from napari.utils.theme import Theme
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

    @property
    def _helper_text(self) -> Optional[str]:
        """
        Helper text for widgets.
        """
        if self.lower is None and self.upper is None:
            helper_text = None
        elif self.lower is not None and self.upper is None:
            helper_text = (
                f"Select at least {self.lower} layers to generate plot"
            )
        elif self.lower is None and self.upper is not None:
            helper_text = (
                f"Select at most {self.upper} layers to generate plot"
            )
        elif self.lower == self.upper:
            helper_text = f"Select {self.lower} layers to generate plot"

        else:
            helper_text = (
                f"Select between {self.lower} and "
                f"{self.upper} layers to generate plot"
            )

        if helper_text is not None:
            helper_text = helper_text.replace("1 layers", "1 layer")

        return helper_text


def _has_id(nodes: list[tinycss2.ast.Node], id_name: str) -> bool:
    """
    Is `id_name` in IdentTokens in the list of CSS `nodes`?
    """
    return any(
        [node.type == "ident" and node.value == id_name for node in nodes]
    )


def _get_dimension(
    nodes: list[tinycss2.ast.Node], id_name: str
) -> Union[int, None]:
    """
    Get the value of the DimensionToken for the IdentToken `id_name`.

    Returns
    -------
        None if no IdentToken is found.
    """
    cleaned_nodes = [node for node in nodes if node.type != "whitespace"]
    for name, _, value, _ in zip(*(iter(cleaned_nodes),) * 4):
        if (
            name.type == "ident"
            and value.type == "dimension"
            and name.value == id_name
        ):
            return value.int_value
    warn(f"Unable to find DimensionToken for {id_name}", RuntimeWarning)
    return None


def from_napari_css_get_size_of(
    qt_element_name: str, fallback: tuple[int, int]
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


def style_sheet_from_theme(theme: Theme) -> Dict[str, str]:
    return {
        'axes.edgecolor':theme.secondary.as_hex(),
        # alternatively "axes.facecolor" could be background color or not be set at all, 
        # but this causes problems when saving figure as image
        'axes.facecolor':theme.canvas.as_hex(),
        'axes.labelcolor':theme.text.as_hex(),
        'boxplot.boxprops.color':theme.text.as_hex(),
        'boxplot.capprops.color':theme.text.as_hex(),
        'boxplot.flierprops.markeredgecolor':theme.text.as_hex(),
        'boxplot.whiskerprops.color':theme.text.as_hex(),
        'figure.edgecolor':theme.secondary.as_hex(),
        # alternatively "figure.facecolor" could not be set, but this causes problems 
        # when saving figure as image
        'figure.facecolor':theme.background.as_hex(),
        'grid.color':theme.foreground.as_hex(),
        'legend.edgecolor':theme.secondary.as_hex(),
        'legend.facecolor':theme.background.as_hex(),
        'text.color':theme.text.as_hex(),
        'xtick.color':theme.secondary.as_hex(),
        'xtick.labelcolor':theme.text.as_hex(),
        'ytick.color':theme.secondary.as_hex(),
        'ytick.labelcolor':theme.text.as_hex(),
    }