import math

from bezierkit import Point
from bezierkit.fitting import fit_polyline, maximum_polyline_deviation


def test_polyline_fit_normalizes_duplicates_and_meets_tolerance() -> None:
    points = [Point(x, math.sin(x)) for x in [0, 0, 0.1, 0.2, 0.3, 0.3, 0.4, 0.5]]
    path = fit_polyline(points, tolerance=0.01, duplicate_tolerance=1e-12)
    assert len(path.segments) < len(points) - 1
    assert maximum_polyline_deviation(points, path) <= 0.01
    assert all(segment.fit_error is not None for segment in path)


def test_polyline_fit_preserves_configured_corner() -> None:
    points = [Point(0, 0), Point(1, 0), Point(1, 1), Point(1, 2)]
    preserved = fit_polyline(points, tolerance=2, preserve_corners=True, corner_angle=math.pi / 4)
    simplified = fit_polyline(points, tolerance=2, preserve_corners=False)
    assert any(segment.p3 == Point(1, 0) for segment in preserved)
    assert len(simplified.segments) == 1


def test_closed_polyline_is_closed_without_duplicate_input_endpoint() -> None:
    square = [Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1), Point(0, 0)]
    path = fit_polyline(square, tolerance=0.01, closed=True)
    assert path.closed
    assert path.segments[-1].p3 == path.segments[0].p0
    assert maximum_polyline_deviation(square, path) <= 0.01
