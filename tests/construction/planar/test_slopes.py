import numpy as np
import pytest

from bezierkit.construction.planar.slopes import PlanarSlopes
from bezierkit.core.errors import DimensionMismatch
from bezierkit.core.geometry.point import Point


def slope_at(curve: object, t: float) -> float:
    derivative = curve.derivative().at(t)
    return derivative.y / derivative.x


def test_planar_slopes_match_endpoint_slopes() -> None:
    curve = PlanarSlopes(Point(0, 5), Point(5, 0), -2, -0.3).build()
    assert slope_at(curve, 0) == pytest.approx(-2)
    assert slope_at(curve, 1) == pytest.approx(-0.3)


def test_economic_demand_curve_is_monotone() -> None:
    curve = PlanarSlopes(Point(0, 5), Point(5, 0), -2, -0.3).build()
    points = curve.at_many(np.linspace(0, 1, 101))
    assert np.all(np.diff(points.x) > 0)
    assert np.all(np.diff(points.y) < 0)


def test_planar_slopes_require_two_dimensions() -> None:
    with pytest.raises(DimensionMismatch):
        PlanarSlopes(Point(0, 0, 0), Point(1, 1, 1), 1, 1)


def test_planar_slopes_require_finite_values() -> None:
    with pytest.raises(ValueError, match="finite"):
        PlanarSlopes(Point(0, 0), Point(1, 1), float("inf"), 1)
