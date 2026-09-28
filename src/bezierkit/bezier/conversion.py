from __future__ import annotations

from bezierkit.bezier.curve import BezierCurve
from bezierkit.bezier.segment import CubicBezierSegment
from bezierkit.core.errors import DegreeError, DimensionMismatch
from bezierkit.core.geometry.point import Point


def _require_same_dimension(*points: Point) -> None:
    dimensions = {point.dimension for point in points}
    if len(dimensions) != 1:
        raise DimensionMismatch(f"control point dimensions differ: {sorted(dimensions)}")


def line_to_cubic(p0: Point, p3: Point) -> CubicBezierSegment:
    """Elevate a line segment to an exactly equivalent cubic."""
    _require_same_dimension(p0, p3)
    chord = p3 - p0
    return CubicBezierSegment(p0, p0 + chord * (1.0 / 3.0), p0 + chord * (2.0 / 3.0), p3)


def quadratic_to_cubic(p0: Point, control: Point, p3: Point) -> CubicBezierSegment:
    """Elevate a quadratic Bézier segment to an exactly equivalent cubic."""
    _require_same_dimension(p0, control, p3)
    first = p0 + (control - p0) * (2.0 / 3.0)
    second = p3 + (control - p3) * (2.0 / 3.0)
    return CubicBezierSegment(p0, first, second, p3)


def to_cubic(curve: BezierCurve | CubicBezierSegment) -> CubicBezierSegment:
    """Normalize a linear, quadratic, or cubic curve to a cubic segment."""
    if isinstance(curve, CubicBezierSegment):
        return curve
    points = tuple(curve.control_points)
    if curve.degree == 1:
        return line_to_cubic(points[0], points[1])
    if curve.degree == 2:
        return quadratic_to_cubic(points[0], points[1], points[2])
    if curve.degree == 3:
        return CubicBezierSegment.from_curve(curve)
    raise DegreeError(f"only degree 1, 2, or 3 curves can be converted, got degree {curve.degree}")
