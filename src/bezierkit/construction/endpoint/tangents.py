from __future__ import annotations

from dataclasses import dataclass

from bezierkit.bezier.curve import BezierCurve
from bezierkit.construction.construction import Construction
from bezierkit.construction.endpoint.derivatives import EndpointDerivatives
from bezierkit.core.errors import DimensionMismatch
from bezierkit.core.geometry.point import Point
from bezierkit.core.geometry.vector import Vector


@dataclass(frozen=True, slots=True)
class TangentDirections(Construction[BezierCurve]):
    """Construct a cubic from endpoint tangent directions and handle lengths."""

    start: Point
    end: Point
    start_direction: Vector
    end_direction: Vector
    start_handle: float = 1.0
    end_handle: float = 1.0

    def __post_init__(self) -> None:
        dimensions = {
            self.start.dimension,
            self.end.dimension,
            self.start_direction.dimension,
            self.end_direction.dimension,
        }
        if len(dimensions) != 1:
            raise DimensionMismatch(
                f"endpoint and direction dimensions differ: {sorted(dimensions)}"
            )
        if self.start_handle < 0 or self.end_handle < 0:
            raise ValueError("handle lengths must be non-negative")

    def build(self) -> BezierCurve:
        return EndpointDerivatives(
            start=self.start,
            end=self.end,
            start_derivative=self.start_direction.normalized() * (3.0 * self.start_handle),
            end_derivative=self.end_direction.normalized() * (3.0 * self.end_handle),
        ).build()
