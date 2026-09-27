import pytest

from bezierkit.construction.endpoint.tangents import TangentDirections
from bezierkit.core.errors import DimensionMismatch
from bezierkit.core.geometry.point import Point
from bezierkit.core.geometry.vector import Vector


def test_tangent_directions_normalize_and_scale_handles() -> None:
    curve = TangentDirections(
        start=Point(0, 0),
        end=Point(5, 3),
        start_direction=Vector(10, 0),
        end_direction=Vector(0, 2),
        start_handle=2,
        end_handle=1,
    ).build()
    assert curve.derivative().at(0) == Point(6, 0)
    assert curve.derivative().at(1) == Point(0, 3)


def test_doubling_handle_doubles_tangent_length() -> None:
    def start_speed(handle: float) -> float:
        point = TangentDirections(
            Point(0, 0), Point(2, 2), Vector(1, 1), Vector(1, 0), start_handle=handle
        ).build().derivative().at(0)
        return Vector(*point.coords).norm()

    assert start_speed(2) == pytest.approx(2 * start_speed(1))


def test_tangent_directions_validate_dimensions_and_handles() -> None:
    with pytest.raises(DimensionMismatch):
        TangentDirections(Point(0, 0), Point(1, 1), Vector(1, 0, 0), Vector(1, 0))
    with pytest.raises(ValueError, match="non-negative"):
        TangentDirections(
            Point(0, 0), Point(1, 1), Vector(1, 0), Vector(1, 0), start_handle=-1
        )
