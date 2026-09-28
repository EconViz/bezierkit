import pytest

from bezierkit import CubicBezierSegment, PiecewiseBezier, Point
from bezierkit.bezier.path import BezierSubpath


def line(start: tuple[float, float], end: tuple[float, float]) -> CubicBezierSegment:
    return CubicBezierSegment.from_line(Point(*start), Point(*end))


def test_piecewise_path_exposes_segments_controls_and_uniform_evaluation() -> None:
    first = line((0, 0), (2, 0))
    second = line((2, 0), (2, 4))
    path = PiecewiseBezier([first, second])

    assert path.segments == (first, second)
    assert path.control_points == (first.control_points, second.control_points)
    assert tuple(path) == path.segments
    assert path.at(0.25) == Point(1, 0)
    assert path.at(0.75) == Point(2, 2)
    assert path.at(1.0) == Point(2, 4)


def test_piecewise_path_validates_continuity_with_explicit_tolerance() -> None:
    first = line((0, 0), (1, 0))
    almost = line((1.00001, 0), (2, 0))
    tolerant = PiecewiseBezier([first, almost], continuity_tolerance=1e-4)
    left, right = tolerant.split(0.25)
    assert left.at(1) == right.at(0)
    with pytest.raises(ValueError, match="not continuous"):
        PiecewiseBezier([first, almost], continuity_tolerance=1e-8)


def test_closed_path_is_metadata_and_does_not_add_a_segment() -> None:
    segments = [line((0, 0), (1, 0)), line((1, 0), (0, 0))]
    path = PiecewiseBezier(segments, closed=True)
    assert path.closed is True
    assert len(path.segments) == 2


def test_closed_path_requires_last_endpoint_to_meet_first() -> None:
    with pytest.raises(ValueError, match="closed path"):
        PiecewiseBezier([line((0, 0), (1, 0))], closed=True)


def test_compound_path_preserves_independent_subpaths() -> None:
    outer = PiecewiseBezier([line((0, 0), (2, 0)), line((2, 0), (0, 0))], closed=True)
    hole = PiecewiseBezier([line((0.5, 0), (1.5, 0)), line((1.5, 0), (0.5, 0))], closed=True)
    compound = PiecewiseBezier.compound([outer, hole])

    assert len(compound.subpaths) == 2
    assert all(isinstance(subpath, BezierSubpath) for subpath in compound.subpaths)
    assert compound.segments == outer.segments + hole.segments
    with pytest.raises(ValueError, match="compound"):
        compound.at(0.5)


def test_piecewise_reversal_and_split_preserve_geometry() -> None:
    path = PiecewiseBezier([line((0, 0), (2, 0)), line((2, 0), (2, 4))])
    assert path.reversed().at(0.2) == path.at(0.8)
    left, right = path.split(0.25)
    assert left.at(1) == path.at(0.25)
    assert right.at(0) == path.at(0.25)
    assert left.at(0) == path.at(0)
    assert right.at(1) == path.at(1)


def test_split_rejects_closed_and_compound_paths() -> None:
    closed = PiecewiseBezier([line((0, 0), (1, 0)), line((1, 0), (0, 0))], closed=True)
    with pytest.raises(ValueError, match="open"):
        closed.split(0.5)
    with pytest.raises(ValueError, match="compound"):
        PiecewiseBezier.compound([closed, closed]).split(0.5)
