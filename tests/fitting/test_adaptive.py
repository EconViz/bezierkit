import math

import pytest

from bezierkit import PiecewiseBezier, Point, Vector
from bezierkit.core.errors import ToleranceNotMet
from bezierkit.fitting import fit_graph, fit_parametric, hermite_error_bound


def test_fourth_derivative_bound_scales_by_one_sixteenth_when_halved() -> None:
    whole = hermite_error_bound(24.0, 0.0, 2.0)
    half = hermite_error_bound(24.0, 0.0, 1.0)
    assert whole == pytest.approx(1.0)
    assert half == pytest.approx(whole / 16.0)


def test_adaptive_graph_fit_meets_geometric_tolerance_and_exposes_errors() -> None:
    path = fit_graph(
        lambda x: x**4,
        lambda x: 4 * x**3,
        x0=-1,
        x1=1,
        tolerance=1e-3,
    )
    assert isinstance(path, PiecewiseBezier)
    assert len(path.segments) > 1
    assert all(segment.fit_error is not None for segment in path)
    assert max(segment.fit_error or 0 for segment in path) <= 1e-3


def test_adaptive_parametric_fit_supports_three_dimensions() -> None:
    path = fit_parametric(
        lambda t: Point(math.cos(t), math.sin(t), t),
        lambda t: Vector(-math.sin(t), math.cos(t), 1),
        t0=0,
        t1=1,
        tolerance=1e-4,
    )
    assert path.dimension == 3
    assert path.at(0) == Point(1, 0, 0)


def test_adaptive_fit_raises_when_limits_prevent_requested_tolerance() -> None:
    with pytest.raises(ToleranceNotMet):
        fit_graph(
            lambda x: math.sin(20 * x),
            lambda x: 20 * math.cos(20 * x),
            x0=0,
            x1=1,
            tolerance=1e-10,
            max_depth=0,
        )
