from __future__ import annotations

import math

from bezierkit.bezier.segment import CubicBezierSegment
from bezierkit.core.errors import DimensionMismatch
from bezierkit.core.geometry.point import Point
from bezierkit.core.geometry.vector import Vector


def parametric_hermite(
    p0: Point,
    p3: Point,
    derivative0: Vector,
    derivative1: Vector,
    *,
    t0: float = 0.0,
    t1: float = 1.0,
) -> CubicBezierSegment:
    """Interpolate positions and derivatives over a non-zero parameter interval."""
    start = float(t0)
    end = float(t1)
    if not math.isfinite(start) or not math.isfinite(end):
        raise ValueError("parameter interval must be finite")
    width = end - start
    if width == 0.0:
        raise ValueError("parameter interval must have non-zero width")
    dimensions = {p0.dimension, p3.dimension, derivative0.dimension, derivative1.dimension}
    if len(dimensions) != 1:
        raise DimensionMismatch(f"endpoint and derivative dimensions differ: {sorted(dimensions)}")
    p1 = p0 + derivative0 * (width / 3.0)
    p2 = p3 - derivative1 * (width / 3.0)
    assert isinstance(p2, Point)
    return CubicBezierSegment(p0, p1, p2, p3)


def graph_hermite(
    *,
    x0: float,
    x1: float,
    y0: float,
    y1: float,
    m0: float,
    m1: float,
) -> CubicBezierSegment:
    """Interpolate ``y=f(x)`` using endpoint values and slopes."""
    values = (x0, x1, y0, y1, m0, m1)
    if not all(math.isfinite(float(value)) for value in values):
        raise ValueError("graph interpolation values must be finite")
    return parametric_hermite(
        Point(x0, y0),
        Point(x1, y1),
        Vector(1.0, m0),
        Vector(1.0, m1),
        t0=x0,
        t1=x1,
    )
