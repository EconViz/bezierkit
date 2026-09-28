import numpy as np
import pytest

from bezierkit.core.domain.interval import Interval


def test_interval_contains_clamps_and_samples() -> None:
    interval = Interval(0, 1)
    assert interval.contains(0)
    assert interval.contains(1)
    assert not interval.contains(1.1)
    assert interval.clamp(-1) == 0
    assert interval.clamp(2) == 1
    assert np.allclose(interval.linspace(5), [0, 0.25, 0.5, 0.75, 1])


def test_interval_rejects_inverted_bounds() -> None:
    with pytest.raises(ValueError, match="start"):
        Interval(1, 0)


def test_interval_rejects_non_finite_bounds() -> None:
    with pytest.raises(ValueError, match="finite"):
        Interval(0, float("inf"))


def test_interval_is_immutable() -> None:
    interval = Interval(0, 1)
    with pytest.raises(AttributeError):
        interval.start = 2
