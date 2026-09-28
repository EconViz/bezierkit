from abc import ABC

import pytest

from bezierkit.core.capabilities.curve import ParametricCurve
from bezierkit.core.capabilities.differentiable import Differentiable
from bezierkit.core.capabilities.reversible import Reversible
from bezierkit.core.capabilities.subdividable import Subdividable
from bezierkit.core.domain.interval import Interval
from bezierkit.core.geometry.point import Point
from bezierkit.core.geometry.point_set import PointSet


class Line(ParametricCurve):
    @property
    def dimension(self) -> int:
        return 2

    @property
    def domain(self) -> Interval:
        return Interval(0, 1)

    def at(self, t: float) -> Point:
        return Point(t, t)

    def at_many(self, t: object) -> PointSet:
        return PointSet([[value, value] for value in t])


def test_parametric_curve_contract_is_usable() -> None:
    line = Line()
    assert line(0.5) == Point(0.5, 0.5)
    assert line.at_many([0, 1]).count == 2


@pytest.mark.parametrize(
    "capability", [ParametricCurve, Differentiable, Subdividable, Reversible]
)
def test_capabilities_are_abstract(capability: type[ABC]) -> None:
    with pytest.raises(TypeError):
        capability()
