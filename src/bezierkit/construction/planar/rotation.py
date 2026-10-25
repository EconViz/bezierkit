"""A quadratic connector whose bend follows the angle between two radial points."""

from __future__ import annotations

import math
from dataclasses import dataclass

from bezierkit.bezier.curve import BezierCurve
from bezierkit.construction.construction import Construction
from bezierkit.core.errors import DegenerateGeometry, DimensionMismatch
from bezierkit.core.geometry.point import Point
from bezierkit.core.geometry.vector import Vector


def _cross(first: Vector, second: Vector) -> float:
    return first.coords[0] * second.coords[1] - first.coords[1] * second.coords[0]


@dataclass(frozen=True, slots=True)
class RotationConnector(Construction[BezierCurve]):
    """Construct a quadratic connector between two points around ``pivot``.

    The open, concave side of the connector faces the pivot by default, so the
    control point lies on the opposite chord normal. Its normalized offset is
    derived from the included angle ``theta``::

        curvature = 0.5 * tan((pi / 2 - min(theta, pi / 2)) / 2)

    The endpoint tangents therefore turn through ``2 atan(2 * curvature)``;
    that turn plus ``theta`` is a right angle. Angles at or above 90 degrees
    use a straight connector. Set ``concave_toward_pivot=False`` for the
    mirrored connector.
    """

    start: Point
    end: Point
    pivot: Point
    concave_toward_pivot: bool = True

    def __post_init__(self) -> None:
        dimensions = {self.start.dimension, self.end.dimension, self.pivot.dimension}
        if dimensions != {2}:
            if len(dimensions) == 1:
                raise DimensionMismatch("RotationConnector requires 2D points")
            raise DimensionMismatch(f"rotation connector dimensions differ: {sorted(dimensions)}")
        if self.start == self.end:
            raise DegenerateGeometry("rotation connector endpoints must differ")
        if self.start == self.pivot or self.end == self.pivot:
            raise DegenerateGeometry("rotation connector rays must have non-zero length")

    @property
    def included_angle(self) -> float:
        """The unsigned smaller angle between the two pivot rays, in radians."""
        first = self.start - self.pivot
        second = self.end - self.pivot
        assert isinstance(first, Vector) and isinstance(second, Vector)
        first = first.normalized()
        second = second.normalized()
        return abs(math.atan2(_cross(first, second), first.dot(second)))

    @property
    def curvature(self) -> float:
        """The non-negative control-point offset as a fraction of chord length."""
        angle = min(self.included_angle, math.pi / 2)
        return 0.5 * math.tan((math.pi / 2 - angle) / 2)

    @property
    def control(self) -> Point:
        """The derived quadratic control point."""
        chord = self.end - self.start
        assert isinstance(chord, Vector)
        midpoint = Point(
            (self.start.x + self.end.x) / 2,
            (self.start.y + self.end.y) / 2,
        )
        normal = Vector(chord.coords[1], -chord.coords[0])
        toward = self.pivot - midpoint
        assert isinstance(toward, Vector)
        # A quadratic bulges toward its control point and opens the other way.
        # Put the control point away from the pivot so the concavity faces it.
        if normal.dot(toward) > 0:
            normal = normal * -1
        if not self.concave_toward_pivot:
            normal = normal * -1
        return midpoint + normal * self.curvature

    def build(self) -> BezierCurve:
        return BezierCurve.quadratic(self.start, self.control, self.end)
