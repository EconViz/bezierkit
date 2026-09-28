from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field

import numpy as np

from bezierkit.bezier.curve import BezierCurve
from bezierkit.bezier.evaluation.casteljau import DeCasteljauEvaluator
from bezierkit.bezier.evaluation.evaluator import Evaluator
from bezierkit.core.capabilities.curve import ParametricCurve
from bezierkit.core.capabilities.differentiable import Differentiable
from bezierkit.core.capabilities.reversible import Reversible
from bezierkit.core.capabilities.subdividable import Subdividable
from bezierkit.core.domain.interval import Interval
from bezierkit.core.errors import DegreeError, DimensionMismatch
from bezierkit.core.geometry.point import Point
from bezierkit.core.geometry.point_set import PointSet


@dataclass(frozen=True, slots=True)
class CubicBezierSegment(ParametricCurve, Differentiable, Subdividable, Reversible):
    """An immutable cubic Bézier segment with inspectable control points."""

    p0: Point
    p1: Point
    p2: Point
    p3: Point
    _evaluator: Evaluator = field(
        default_factory=DeCasteljauEvaluator,
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        dimensions = {point.dimension for point in self.control_points}
        if len(dimensions) != 1:
            raise DimensionMismatch(f"control point dimensions differ: {sorted(dimensions)}")

    @property
    def control_points(self) -> tuple[Point, Point, Point, Point]:
        return (self.p0, self.p1, self.p2, self.p3)

    @property
    def dimension(self) -> int:
        return self.p0.dimension

    @property
    def domain(self) -> Interval:
        return Interval(0.0, 1.0)

    @property
    def evaluator(self) -> Evaluator:
        return self._evaluator

    @property
    def bounding_box(self) -> tuple[Point, Point]:
        """Return the tight axis-aligned bounds of the polynomial segment."""
        controls = np.asarray([point.coords for point in self.control_points], dtype=float)
        a = -controls[0] + 3.0 * controls[1] - 3.0 * controls[2] + controls[3]
        b = 3.0 * controls[0] - 6.0 * controls[1] + 3.0 * controls[2]
        c = -3.0 * controls[0] + 3.0 * controls[1]
        parameters = {0.0, 1.0}
        for axis in range(self.dimension):
            roots = np.roots([3.0 * a[axis], 2.0 * b[axis], c[axis]])
            parameters.update(
                float(root.real)
                for root in roots
                if abs(root.imag) <= 1e-12 and 0.0 < root.real < 1.0
            )
        values = self.at_many(sorted(parameters)).array
        return Point(*values.min(axis=0)), Point(*values.max(axis=0))

    def __iter__(self) -> Iterator[Point]:
        return iter(self.control_points)

    def as_curve(self) -> BezierCurve:
        return BezierCurve(self.control_points, evaluator=self._evaluator)

    def at(self, t: float) -> Point:
        return self.as_curve().at(t)

    def at_many(self, t: Iterable[float] | np.ndarray) -> PointSet:
        return self.as_curve().at_many(t)

    def derivative(self, order: int = 1) -> BezierCurve:
        return self.as_curve().derivative(order)

    def split(self, t: float) -> tuple[CubicBezierSegment, CubicBezierSegment]:
        left, right = self.as_curve().split(t)
        return self.from_curve(left), self.from_curve(right)

    def segment(self, t0: float, t1: float) -> CubicBezierSegment:
        curve = self.as_curve().segment(t0, t1)
        if curve.degree == 0:
            point = curve.at(0.0)
            return CubicBezierSegment(point, point, point, point, self._evaluator)
        return self.from_curve(curve)

    def reversed(self) -> CubicBezierSegment:
        return CubicBezierSegment(self.p3, self.p2, self.p1, self.p0, self._evaluator)

    @classmethod
    def from_curve(cls, curve: BezierCurve) -> CubicBezierSegment:
        if curve.degree != 3:
            raise DegreeError(f"a cubic segment requires degree 3, got degree {curve.degree}")
        p0, p1, p2, p3 = tuple(curve.control_points)
        return cls(p0, p1, p2, p3, curve.evaluator)

    @classmethod
    def from_line(cls, p0: Point, p3: Point) -> CubicBezierSegment:
        from bezierkit.bezier.conversion import line_to_cubic

        return line_to_cubic(p0, p3)

    @classmethod
    def from_quadratic(cls, p0: Point, control: Point, p3: Point) -> CubicBezierSegment:
        from bezierkit.bezier.conversion import quadratic_to_cubic

        return quadratic_to_cubic(p0, control, p3)
