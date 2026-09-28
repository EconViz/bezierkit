import pytest

from bezierkit import Point, Vector
from bezierkit.interpolation import graph_hermite, parametric_hermite


def test_graph_hermite_uses_one_third_horizontal_handles() -> None:
    segment = graph_hermite(x0=1, x1=4, y0=2, y1=5, m0=-2, m1=0.5)
    assert segment.control_points == (
        Point(1, 2),
        Point(2, 0),
        Point(3, 4.5),
        Point(4, 5),
    )
    start = segment.derivative().at(0)
    end = segment.derivative().at(1)
    assert start.y / start.x == pytest.approx(-2)
    assert end.y / end.x == pytest.approx(0.5)


def test_graph_hermite_supports_reversed_but_not_zero_width_domains() -> None:
    reversed_segment = graph_hermite(x0=4, x1=1, y0=5, y1=2, m0=0.5, m1=-2)
    assert reversed_segment.p0 == Point(4, 5)
    assert reversed_segment.p3 == Point(1, 2)
    with pytest.raises(ValueError, match="non-zero"):
        graph_hermite(x0=1, x1=1, y0=2, y1=3, m0=0, m1=0)


def test_parametric_hermite_scales_endpoint_derivatives_by_interval() -> None:
    segment = parametric_hermite(
        Point(1, 2, 3),
        Point(5, 7, 11),
        Vector(2, 0, -1),
        Vector(0, 3, 2),
        t0=2,
        t1=5,
    )
    assert segment.derivative().at(0) == Point(6, 0, -3)
    assert segment.derivative().at(1) == Point(0, 9, 6)


def test_parametric_hermite_handles_zero_derivatives_and_reversed_interval() -> None:
    segment = parametric_hermite(
        Point(0, 0), Point(1, 1), Vector(0, 0), Vector(0, 0), t0=2, t1=-1
    )
    assert segment.p0 == segment.p1 == Point(0, 0)
    assert segment.p2 == segment.p3 == Point(1, 1)
    with pytest.raises(ValueError, match="non-zero"):
        parametric_hermite(Point(0, 0), Point(1, 1), Vector(1, 0), Vector(1, 0), t0=2, t1=2)
