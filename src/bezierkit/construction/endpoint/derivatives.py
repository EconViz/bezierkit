from __future__ import annotations

from dataclasses import dataclass

from bezierkit.bezier.curve import BezierCurve
from bezierkit.construction.construction import Construction
from bezierkit.core.errors import DimensionMismatch
from bezierkit.core.geometry.point import Point
from bezierkit.core.geometry.vector import Vector


@dataclass(frozen=True, slots=True)
class EndpointDerivatives(Construction[BezierCurve]):
    """Construct a cubic from endpoint positions and derivatives."""

    start: Point
    end: Point
    start_derivative: Vector
    end_derivative: Vector

    def __post_init__(self) -> None:
        dimensions = {
            self.start.dimension,
            self.end.dimension,
            self.start_derivative.dimension,
            self.end_derivative.dimension,
        }
        if len(dimensions) != 1:
            raise DimensionMismatch(f"endpoint and derivative dimensions differ: {sorted(dimensions)}")

    def build(self) -> BezierCurve:
        p1 = self.start + self.start_derivative * (1.0 / 3.0)
        p2 = self.end - self.end_derivative * (1.0 / 3.0)
        assert isinstance(p2, Point)
        return BezierCurve.cubic(self.start, p1, p2, self.end)
