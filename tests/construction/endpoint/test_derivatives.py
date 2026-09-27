import pytest

from bezierkit.construction.endpoint.derivatives import EndpointDerivatives
from bezierkit.core.errors import DimensionMismatch
from bezierkit.core.geometry.point import Point
from bezierkit.core.geometry.vector import Vector


def test_endpoint_derivatives_reconstruct_requested_values() -> None:
    curve = EndpointDerivatives(
        start=Point(0, 0, 0),
        end=Point(4, 2, 1),
        start_derivative=Vector(3, 6, 9),
        end_derivative=Vector(6, -3, 0),
    ).build()
    assert curve.at(0) == Point(0, 0, 0)
    assert curve.at(1) == Point(4, 2, 1)
    assert curve.derivative().at(0) == Point(3, 6, 9)
    assert curve.derivative().at(1) == Point(6, -3, 0)


def test_endpoint_derivatives_reject_dimension_mismatch() -> None:
    with pytest.raises(DimensionMismatch):
        EndpointDerivatives(
            start=Point(0, 0),
            end=Point(1, 1),
            start_derivative=Vector(1, 2, 3),
            end_derivative=Vector(1, 1),
        )
