import numpy as np
import pytest

from bezierkit.core.geometry.point import Point
from bezierkit.core.geometry.point_set import PointSet


def test_point_set_shape_columns_and_iteration() -> None:
    points = PointSet([[0, 1], [2, 3]])
    assert (points.count, points.dimension) == (2, 2)
    assert np.allclose(points.x, [0, 2])
    assert np.allclose(points.y, [1, 3])
    assert list(points) == [Point(0, 1), Point(2, 3)]


def test_point_set_accepts_points() -> None:
    points = PointSet([Point(0, 0), Point(1, 1)])
    assert np.allclose(points.array, [[0, 0], [1, 1]])


def test_point_set_rejects_non_matrix() -> None:
    with pytest.raises(ValueError, match="2D"):
        PointSet([0, 1, 2])


def test_point_set_rejects_empty_axes() -> None:
    with pytest.raises(ValueError):
        PointSet(np.empty((0, 2)))


def test_point_set_missing_z_raises() -> None:
    with pytest.raises(AttributeError):
        _ = PointSet([[0, 1]]).z


def test_point_set_owns_read_only_copy() -> None:
    source = np.array([[0.0, 1.0]])
    points = PointSet(source)
    source[0, 0] = 9
    assert points.x[0] == 0
    with pytest.raises(ValueError):
        points.array[0, 0] = 5


def test_point_set_rejects_non_finite_coordinates() -> None:
    with pytest.raises(ValueError, match="finite"):
        PointSet([[0, float("nan")]])
