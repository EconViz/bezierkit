import numpy as np
import pytest

from bezierkit.bezier.polygon import ControlPolygon
from bezierkit.core.errors import DegreeError
from bezierkit.core.geometry.point import Point


def test_control_polygon_properties_and_differences() -> None:
    polygon = ControlPolygon([Point(0, 0), Point(1, 2), Point(3, 3)])
    assert polygon.degree == 2
    assert polygon.dimension == 2
    assert np.allclose(polygon.differences(), [[1, 2], [2, 1]])
    assert list(polygon.points) == [Point(0, 0), Point(1, 2), Point(3, 3)]


def test_control_polygon_accepts_constant_curve() -> None:
    polygon = ControlPolygon([[2, 3]])
    assert polygon.degree == 0
    assert polygon.differences().shape == (0, 2)


def test_control_polygon_rejects_no_points() -> None:
    with pytest.raises(DegreeError):
        ControlPolygon(np.empty((0, 2)))


def test_control_polygon_is_immutable_copy() -> None:
    source = np.array([[0.0, 0.0], [1.0, 1.0]])
    polygon = ControlPolygon(source)
    source[0, 0] = 9
    assert polygon.points[0] == Point(0, 0)
    with pytest.raises(ValueError):
        polygon.points.array[0, 0] = 2
