import numpy as np

from bezierkit import BezierCurve, CubicBezierSegment, Point
from bezierkit.bezier.conversion import to_cubic


def assert_same_geometry(curve: BezierCurve, cubic: CubicBezierSegment) -> None:
    parameters = np.linspace(0.0, 1.0, 501)
    assert np.allclose(curve.at_many(parameters).array, cubic.at_many(parameters).array)


def test_line_elevates_exactly_to_cubic_in_n_dimensions() -> None:
    curve = BezierCurve.linear(Point(0, 3, -2), Point(6, 9, 4))
    cubic = to_cubic(curve)
    assert cubic.control_points == (
        Point(0, 3, -2),
        Point(2, 5, 0),
        Point(4, 7, 2),
        Point(6, 9, 4),
    )
    assert_same_geometry(curve, cubic)


def test_quadratic_elevates_exactly_to_cubic() -> None:
    curve = BezierCurve.quadratic(Point(0, 0), Point(3, 6), Point(9, 0))
    cubic = to_cubic(curve)
    assert cubic.control_points == (Point(0, 0), Point(2, 4), Point(5, 4), Point(9, 0))
    assert_same_geometry(curve, cubic)


def test_cubic_conversion_preserves_control_points() -> None:
    curve = BezierCurve.cubic(Point(0, 0), Point(1, 2), Point(3, 2), Point(4, 0))
    assert to_cubic(curve).control_points == tuple(curve.control_points)
