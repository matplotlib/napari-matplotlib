import numpy as np
import pytest
from skimage import data


@pytest.fixture(
    params=[
        ((100, 100), {"rgb": False}),
        ((100, 100, 100), {"rgb": False}),
        ((100, 100, 3), {"rgb": True}),
    ]
)
def image_data(request):
    return np.ones(request.param[0]), request.param[1]


@pytest.fixture
def astronaut_data():
    return data.astronaut(), {"rgb": True}


@pytest.fixture
def brain_data():
    return data.brain(), {"rgb": False}
