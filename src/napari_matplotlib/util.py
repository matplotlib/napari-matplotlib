from typing import Optional


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
