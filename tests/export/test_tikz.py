from bezierkit import CubicBezierSegment, PiecewiseBezier, Point
from bezierkit.export.tikz import segment_to_tikz, to_tikz


def test_segment_tikz_exposes_native_control_points() -> None:
    segment = CubicBezierSegment(
        Point(1, 4), Point(1.166666, 3.333333), Point(1.333333, 2.962963), Point(1.5, 2.666667)
    )
    assert segment_to_tikz(segment, precision=5) == (
        "(1.00000,4.00000) .. controls (1.16667,3.33333) and "
        "(1.33333,2.96296) .. (1.50000,2.66667)"
    )


def test_tikz_supports_consecutive_closed_and_compound_paths_without_theme() -> None:
    closed = PiecewiseBezier(
        [
            CubicBezierSegment.from_line(Point(0, 0), Point(1, 0)),
            CubicBezierSegment.from_line(Point(1, 0), Point(0, 0)),
        ],
        closed=True,
    )
    open_path = PiecewiseBezier(
        [CubicBezierSegment.from_line(Point(2, 0), Point(3, 0))]
    )
    output = to_tikz(PiecewiseBezier.compound([closed, open_path]), precision=2)
    assert output.count("\\draw ") == 2
    assert output.count(".. controls") == 3
    assert "-- cycle;" in output
    assert "color=" not in output


def test_tikz_accepts_explicit_style_and_transform() -> None:
    path = PiecewiseBezier([CubicBezierSegment.from_line(Point(0, 0), Point(1, 0))])
    output = to_tikz(
        path,
        precision=1,
        options="thick,draw=blue",
        transform=lambda point: Point(point.x * 2, point.y + 1),
    )
    assert output.startswith("\\draw[thick,draw=blue] (0.0,1.0)")
    assert output.endswith("(2.0,1.0);")
