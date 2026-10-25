import math

import pytest

from bezierkit.construction import RotationConnector
from bezierkit.core.errors import DegenerateGeometry, DimensionMismatch
from bezierkit.core.geometry.point import Point
from bezierkit.core.geometry.vector import Vector


def radial_point(degrees: float, radius: float = 1.0) -> Point:
    angle = math.radians(degrees)
    return Point(radius * math.cos(angle), radius * math.sin(angle))


def test_fifteen_degree_rotation_derives_preferred_curvature() -> None:
    connector = RotationConnector(Point(1, 0), radial_point(15), Point(0, 0))

    assert connector.included_angle == pytest.approx(math.radians(15))
    assert connector.curvature == pytest.approx(0.3836634939894802)
    assert connector.build().control_points[1] == connector.control


def test_connector_is_invariant_under_translation_rotation_and_scale() -> None:
    original = RotationConnector(Point(2, 0), radial_point(30, 2), Point(0, 0))
    transformed = RotationConnector(Point(4, 7), Point(2, 3 + 2 * math.sqrt(3)), Point(4, 3))

    assert transformed.included_angle == pytest.approx(original.included_angle)
    assert transformed.curvature == pytest.approx(original.curvature)
    expected = Point(4 - 2 * original.control.y, 3 + 2 * original.control.x)
    assert transformed.control.x == pytest.approx(expected.x)
    assert transformed.control.y == pytest.approx(expected.y)


def test_opposite_concavity_mirrors_control_across_chord() -> None:
    toward = RotationConnector(Point(1, 0), Point(0, 1), Point(0, 0))
    away = RotationConnector(
        Point(1, 0),
        Point(0, 1),
        Point(0, 0),
        concave_toward_pivot=False,
    )
    midpoint = Point(0.5, 0.5)
    toward_offset = toward.control - midpoint
    away_offset = away.control - midpoint

    assert isinstance(toward_offset, Vector) and isinstance(away_offset, Vector)
    assert toward_offset.coords == pytest.approx(tuple(-value for value in away_offset.coords))


def test_angles_at_or_above_right_angle_use_straight_connector() -> None:
    connector = RotationConnector(Point(1, 0), radial_point(120), Point(0, 0))

    assert connector.curvature == pytest.approx(0)
    assert connector.control == Point(
        (connector.start.x + connector.end.x) / 2,
        (connector.start.y + connector.end.y) / 2,
    )


@pytest.mark.parametrize(
    "start,end,pivot,message",
    [
        (Point(1, 0), Point(1, 0), Point(0, 0), "endpoints"),
        (Point(0, 0), Point(1, 0), Point(0, 0), "non-zero"),
    ],
)
def test_degenerate_connectors_fail_predictably(start, end, pivot, message) -> None:
    with pytest.raises(DegenerateGeometry, match=message):
        RotationConnector(start, end, pivot)


def test_connector_requires_matching_2d_points() -> None:
    with pytest.raises(DimensionMismatch, match="2D"):
        RotationConnector(Point(1, 0, 0), Point(0, 1, 0), Point(0, 0, 0))
    with pytest.raises(DimensionMismatch, match="dimensions differ"):
        RotationConnector(Point(1, 0), Point(0, 1), Point(0, 0, 0))
