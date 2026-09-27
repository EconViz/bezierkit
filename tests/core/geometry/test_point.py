import numpy as np
import pytest

from bezierkit.core.errors import DimensionMismatch
from bezierkit.core.geometry.point import Point
from bezierkit.core.geometry.vector import Vector


def test_point_coordinates_and_dimension() -> None:
    point = Point(1, 2, 3)
    assert (point.x, point.y, point.z) == (1.0, 2.0, 3.0)
    assert point.dimension == 3


def test_point_missing_coordinate_raises() -> None:
    with pytest.raises(AttributeError):
        _ = Point(1).y


def test_point_is_immutable() -> None:
    point = Point(1, 2)
    with pytest.raises(AttributeError):
        point.coords = (3.0, 4.0)


def test_point_vector_arithmetic() -> None:
    assert Point(1, 2) + Vector(3, 4) == Point(4, 6)
    assert Point(4, 6) - Point(1, 2) == Vector(3, 4)


def test_point_dimension_mismatch_is_domain_error() -> None:
    with pytest.raises(DimensionMismatch):
        _ = Point(1, 2) + Vector(1, 2, 3)


def test_point_array_is_independent() -> None:
    values = Point(1, 2).as_array()
    values[0] = 99
    assert np.allclose(Point(1, 2).as_array(), [1, 2])


def test_point_requires_a_coordinate() -> None:
    with pytest.raises(ValueError):
        Point()
