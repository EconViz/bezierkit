from __future__ import annotations

import math
from dataclasses import dataclass

from bezierkit.bezier.curve import BezierCurve
from bezierkit.construction.construction import Construction
from bezierkit.construction.endpoint.tangents import TangentDirections
from bezierkit.core.errors import DimensionMismatch
from bezierkit.core.geometry.point import Point
from bezierkit.core.geometry.vector import Vector


@dataclass(frozen=True, slots=True)
class PlanarSlopes(Construction[BezierCurve]):
    """Construct a planar cubic from endpoint slopes ``dy / dx``."""

    start: Point
    end: Point
    start_slope: float
    end_slope: float
    start_handle: float = 1.0
    end_handle: float = 1.0

    def __post_init__(self) -> None:
        if self.start.dimension != 2 or self.end.dimension != 2:
            raise DimensionMismatch("PlanarSlopes requires 2D points")
        if not math.isfinite(self.start_slope) or not math.isfinite(self.end_slope):
            raise ValueError("slopes must be finite")

    def build(self) -> BezierCurve:
        return TangentDirections(
            start=self.start,
            end=self.end,
            start_direction=Vector(1.0, self.start_slope),
            end_direction=Vector(1.0, self.end_slope),
            start_handle=self.start_handle,
            end_handle=self.end_handle,
        ).build()
