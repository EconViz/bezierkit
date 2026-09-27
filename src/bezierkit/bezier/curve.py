from __future__ import annotations

from collections.abc import Iterable

import numpy as np

from bezierkit.bezier.evaluation.casteljau import DeCasteljauEvaluator
from bezierkit.bezier.evaluation.evaluator import Evaluator
from bezierkit.bezier.polygon import ControlPolygon
from bezierkit.core.capabilities.curve import ParametricCurve
from bezierkit.core.domain.interval import Interval
from bezierkit.core.domain.parameter import ParameterValues
from bezierkit.core.errors import DimensionMismatch
from bezierkit.core.geometry.point import Point
from bezierkit.core.geometry.point_set import PointSet


class BezierCurve(ParametricCurve):
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
    def dimension(self) -> int:
        return self._polygon.dimension

    @property
    def degree(self) -> int:
        return self._polygon.degree

    @property
    def domain(self) -> Interval:
        return Interval(0.0, 1.0)

    def at(self, t: float) -> Point:
        return self.at_many([t])[0]

    def at_many(self, t: Iterable[float] | np.ndarray) -> PointSet:
        values = ParameterValues.from_input(t, domain=self.domain)
        return PointSet(self._evaluator.evaluate(self._polygon, values.array))

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
