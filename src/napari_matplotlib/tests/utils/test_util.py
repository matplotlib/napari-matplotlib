# import pytest

# from napari_matplotlib.util import Interval


# def test_interval():
#     interval = Interval(4, 9)
#     for i in range(4, 10):
#         assert i in interval

#     assert 3 not in interval
#     assert 10 not in interval

#     with pytest.raises(ValueError, match="must be an integer"):
#         "string" in interval
