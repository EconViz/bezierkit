import numpy as np
import pytest

from bezierkit.bezier.curve import BezierCurve
from bezierkit.bezier.evaluation.evaluator import Evaluator
from bezierkit.bezier.polygon import ControlPolygon
from bezierkit.core.errors import DimensionMismatch, ParameterOutOfDomain
from bezierkit.core.geometry.point import Point


class FixedEvaluator(Evaluator):
    def evaluate(self, polygon: ControlPolygon, t: np.ndarray) -> np.ndarray:
        return np.full((len(t), polygon.dimension), 42.0)


def test_curve_factories_and_scalar_evaluation_return_points() -> None:
    curve = BezierCurve.cubic(Point(0, 0), Point(1, 2), Point(3, 2), Point(4, 0))
    assert curve.degree == 3
    assert curve.dimension == 2
    assert curve(0) == Point(0, 0)
    assert curve(1) == Point(4, 0)
    assert curve(0.5) == Point(2, 1.5)


def test_curve_vectorized_evaluation_returns_point_set() -> None:
    curve = BezierCurve.linear(Point(0, 0), Point(4, 2))
    points = curve.at_many([0, 0.5, 1])
    assert np.allclose(points.array, [[0, 0], [2, 1], [4, 2]])


def test_curve_rejects_parameter_outside_domain() -> None:
    curve = BezierCurve.linear(Point(0, 0), Point(1, 1))
    with pytest.raises(ParameterOutOfDomain):
        curve.at(1.1)


def test_curve_uses_injected_evaluator() -> None:
    curve = BezierCurve([[0, 0], [1, 1]], evaluator=FixedEvaluator())
    assert curve.at(0.5) == Point(42, 42)


def test_curve_accepts_control_polygon() -> None:
    polygon = ControlPolygon([[0, 0], [1, 1]])
    assert BezierCurve(polygon).at(0.5) == Point(0.5, 0.5)


def test_factory_rejects_mixed_dimensions() -> None:
    with pytest.raises(DimensionMismatch):
        BezierCurve.linear(Point(0, 0), Point(1, 1, 1))


def test_curve_derivative_obeys_endpoint_theorem() -> None:
    curve = BezierCurve.cubic(Point(0, 0), Point(1, 2), Point(3, 2), Point(4, 0))
    derivative = curve.derivative()
    assert derivative.degree == 2
    assert derivative.at(0) == Point(3, 6)
    assert derivative.at(1) == Point(3, -6)


def test_curve_higher_derivative_closes_on_zero_constant() -> None:
    curve = BezierCurve.linear(Point(0, 0), Point(4, 2))
    second = curve.derivative(2)
    assert second.degree == 0
    assert second.at(0.7) == Point(0, 0)


def test_curve_derivative_validates_order() -> None:
    curve = BezierCurve.linear(Point(0, 0), Point(1, 1))
    with pytest.raises(ValueError, match="non-negative"):
        curve.derivative(-1)


def test_curve_split_and_segment_preserve_parameterization() -> None:
    curve = BezierCurve.cubic(Point(0, 0), Point(1, 2), Point(3, 2), Point(4, 0))
    left, right = curve.split(0.3)
    assert left.at(1) == curve.at(0.3)
    assert right.at(0) == curve.at(0.3)
    segment = curve.segment(0.25, 0.75)
    assert segment.at(0) == curve.at(0.25)
    assert segment.at(1) == curve.at(0.75)
    assert segment.at(0.5) == curve.at(0.5)


def test_curve_reversal_is_an_involution() -> None:
    curve = BezierCurve.quadratic(Point(0, 0), Point(1, 3), Point(4, 2))
    reversed_curve = curve.reversed()
    for t in [0, 0.2, 0.8, 1]:
        assert reversed_curve.at(t) == curve.at(1 - t)
        assert reversed_curve.reversed().at(t) == curve.at(t)


def test_curve_exposes_immutable_control_points() -> None:
    curve = BezierCurve.linear(Point(0, 0), Point(2, 3))
    assert list(curve.control_points) == [Point(0, 0), Point(2, 3)]
    with pytest.raises(ValueError):
        curve.control_points.array[0, 0] = 9
