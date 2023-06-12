import os

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


@pytest.fixture
def points_with_features_data():
    n_points = 100
    np.random.seed(10)
    points_data = 100 * np.random.random((100, 2))
    points_features = {
        "feature_0": np.random.random((n_points,)),
        "feature_1": np.random.random((n_points,)),
        "feature_2": np.random.random((n_points,)),
    }

    return points_data, {"features": points_features}


@pytest.fixture(autouse=True, scope="session")
def set_strict_qt():
    env_var = "NAPARI_STRICT_QT"
    old_val = os.environ.get(env_var)
    os.environ[env_var] = "1"
    # Run tests
    yield
    # Reset to original value
    if old_val is not None:
        os.environ[env_var] = old_val
    else:
        del os.environ[env_var]
