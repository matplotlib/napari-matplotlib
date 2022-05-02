import numpy as np
import pytest


@pytest.fixture(
    params=[
        ((100, 100), {"rgb": False}),
        ((100, 100, 100), {"rgb": False}),
        ((100, 100, 3), {"rgb": True}),
    ]
)
def image_data(request):
    return np.ones(request.param[0]), request.param[1]
