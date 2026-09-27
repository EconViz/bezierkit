import numpy as np
import pytest

from bezierkit.core.capabilities.curve import ParametricCurve
from bezierkit.core.domain.interval import Interval
from bezierkit.core.geometry.point import Point
from bezierkit.core.geometry.point_set import PointSet
from bezierkit.sampling.sampler import Sampler
from bezierkit.sampling.uniform import UniformSampler


class Line(ParametricCurve):
    @property
    def dimension(self) -> int:
        return 2

    @property
    def domain(self) -> Interval:
        return Interval(2, 4)

    def at(self, t: float) -> Point:
        return Point(t, 2 * t)

    def at_many(self, t: object) -> PointSet:
        return PointSet([[value, 2 * value] for value in t])


def test_sampler_is_abstract() -> None:
    with pytest.raises(TypeError):
        Sampler()


def test_uniform_sampler_uses_curve_domain_and_count() -> None:
    sample = UniformSampler(5).sample(Line())
    assert np.allclose(sample.t, [2, 2.5, 3, 3.5, 4])
    assert np.allclose(sample.points.array, [[2, 4], [2.5, 5], [3, 6], [3.5, 7], [4, 8]])


@pytest.mark.parametrize("count", [-1, 0, 1])
def test_uniform_sampler_requires_two_points(count: int) -> None:
    with pytest.raises(ValueError, match="at least 2"):
        UniformSampler(count)
