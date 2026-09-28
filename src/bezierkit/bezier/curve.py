from __future__ import annotations

from collections.abc import Iterable

import numpy as np

from bezierkit.bezier.evaluation.casteljau import DeCasteljauEvaluator
from bezierkit.bezier.evaluation.evaluator import Evaluator
from bezierkit.bezier.operations.hodograph import Hodograph
from bezierkit.bezier.operations.subdivision import Subdivider
from bezierkit.bezier.polygon import ControlPolygon
from bezierkit.core.capabilities.curve import ParametricCurve
from bezierkit.core.capabilities.differentiable import Differentiable
from bezierkit.core.capabilities.reversible import Reversible
from bezierkit.core.capabilities.subdividable import Subdividable
from bezierkit.core.domain.interval import Interval
from bezierkit.core.domain.parameter import ParameterValues
from bezierkit.core.errors import DimensionMismatch
from bezierkit.core.geometry.point import Point
from bezierkit.core.geometry.point_set import PointSet


class BezierCurve(ParametricCurve, Differentiable, Subdividable, Reversible):
    """An immutable, degree-generic Bézier curve."""

    def __init__(
        self,
        points: ControlPolygon | PointSet | Iterable[Point] | np.ndarray,
        *,
        evaluator: Evaluator | None = None,
    ) -> None:
        self._polygon = points if isinstance(points, ControlPolygon) else ControlPolygon(points)
        self._evaluator = evaluator or DeCasteljauEvaluator()

    @property
    def evaluator(self) -> Evaluator:
        """The explicitly selected evaluation strategy."""
        return self._evaluator

    @property
    def dimension(self) -> int:
        return self._polygon.dimension

    @property
    def degree(self) -> int:
        return self._polygon.degree

    @property
    def control_points(self) -> PointSet:
        return self._polygon.points

    @property
    def domain(self) -> Interval:
        return Interval(0.0, 1.0)

    def at(self, t: float) -> Point:
        return self.at_many([t])[0]

    def at_many(self, t: Iterable[float] | np.ndarray) -> PointSet:
        values = ParameterValues.from_input(t, domain=self.domain)
        return PointSet(self._evaluator.evaluate(self._polygon, values.array))

    def derivative(self, order: int = 1) -> BezierCurve:
        if not isinstance(order, int) or order < 0:
            raise ValueError("derivative order must be a non-negative integer")
        polygon = self._polygon
        for _ in range(order):
            polygon = Hodograph.of(polygon)
        return BezierCurve(polygon, evaluator=self._evaluator)

    def split(self, t: float) -> tuple[BezierCurve, BezierCurve]:
        left, right = Subdivider.split(self._polygon, t)
        return (
            BezierCurve(left, evaluator=self._evaluator),
            BezierCurve(right, evaluator=self._evaluator),
        )

    def segment(self, t0: float, t1: float) -> BezierCurve:
        return BezierCurve(
            Subdivider.segment(self._polygon, t0, t1),
            evaluator=self._evaluator,
        )

    def reversed(self) -> BezierCurve:
        return BezierCurve(self._polygon.points.array[::-1], evaluator=self._evaluator)

    @classmethod
    def _from_points(cls, points: tuple[Point, ...]) -> BezierCurve:
        dimensions = {point.dimension for point in points}
        if len(dimensions) != 1:
            raise DimensionMismatch(f"control point dimensions differ: {sorted(dimensions)}")
        return cls(points)

    @classmethod
    def linear(cls, p0: Point, p1: Point) -> BezierCurve:
        return cls._from_points((p0, p1))

    @classmethod
    def quadratic(cls, p0: Point, p1: Point, p2: Point) -> BezierCurve:
        return cls._from_points((p0, p1, p2))

    @classmethod
    def cubic(cls, p0: Point, p1: Point, p2: Point, p3: Point) -> BezierCurve:
        return cls._from_points((p0, p1, p2, p3))
