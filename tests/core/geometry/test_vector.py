import pytest

from bezierkit.core.errors import DimensionMismatch
from bezierkit.core.geometry.vector import Vector


def test_vector_arithmetic() -> None:
    assert Vector(1, 2) + Vector(3, 4) == Vector(4, 6)
    assert Vector(3, 5) - Vector(1, 2) == Vector(2, 3)
    assert Vector(1, 2) * 3 == Vector(3, 6)
    assert 2 * Vector(1, 2) == Vector(2, 4)


def test_vector_dot_and_norm() -> None:
    assert Vector(2, 3).dot(Vector(2, 3)) == pytest.approx(13)
    assert Vector(3, 4).norm() == pytest.approx(5)


def test_vector_normalized() -> None:
    assert Vector(3, 4).normalized().norm() == pytest.approx(1)


def test_zero_vector_cannot_be_normalized() -> None:
    with pytest.raises(ValueError, match="zero vector"):
        Vector(0, 0).normalized()


def test_vector_dimension_mismatch_is_domain_error() -> None:
    with pytest.raises(DimensionMismatch):
        Vector(1, 2).dot(Vector(1, 2, 3))


def test_vector_is_immutable() -> None:
    vector = Vector(1, 2)
    with pytest.raises(AttributeError):
        vector.coords = (3.0, 4.0)
