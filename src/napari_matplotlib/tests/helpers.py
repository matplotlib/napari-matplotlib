from io import BytesIO

import numpy as np
import numpy.typing as npt
import pytest
from matplotlib.figure import Figure


def fig_to_array(fig: Figure) -> npt.NDArray[np.uint8]:
    """
    Convert a figure to an RGB array.
    """
    with BytesIO() as io_buf:
        fig.savefig(io_buf, format="raw")
        io_buf.seek(0)
        img_arr: npt.NDArray[np.uint8] = np.reshape(
            np.frombuffer(io_buf.getvalue(), dtype=np.uint8),
            shape=(int(fig.bbox.bounds[3]), int(fig.bbox.bounds[2]), -1),
        )
    return img_arr


def assert_figures_equal(fig1: Figure, fig2: Figure) -> None:
    np.testing.assert_equal(fig_to_array(fig1), fig_to_array(fig2))


def assert_figures_not_equal(fig1: Figure, fig2: Figure) -> None:
    with pytest.raises(AssertionError, match="Arrays are not equal"):
        assert_figures_equal(fig1, fig2)
