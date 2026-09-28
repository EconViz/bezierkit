from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from bezierkit import BezierCurve, CubicBezierSegment, Point
from bezierkit.core.errors import DegreeError, DimensionMismatch


def make_segment() -> CubicBezierSegment:
    return CubicBezierSegment(
        Point(0, 0),
        Point(1, 2),
        Point(3, 2),
        Point(4, 0),
    )


def test_segment_exposes_four_immutable_control_points() -> None:
    segment = make_segment()
    assert segment.control_points == (segment.p0, segment.p1, segment.p2, segment.p3)
    assert segment.dimension == 2
    with pytest.raises(FrozenInstanceError):
        segment.p0 = Point(9, 9)  # type: ignore[misc]


def test_segment_delegates_evaluation_derivatives_split_and_reversal() -> None:
    segment = make_segment()
    assert segment.at(0.5) == Point(2, 1.5)
    assert segment.derivative().at(0) == Point(3, 6)
    left, right = segment.split(0.25)
    assert isinstance(left, CubicBezierSegment)
    assert isinstance(right, CubicBezierSegment)
    assert left.p3 == segment.at(0.25) == right.p0
    assert segment.reversed().reversed() == segment


def test_segment_has_exact_axis_aligned_bounding_box() -> None:
    segment = make_segment()
    minimum, maximum = segment.bounding_box
    assert minimum == Point(0, 0)
    assert maximum == Point(4, 1.5)


def test_segment_is_dimension_generic_and_validates_dimensions() -> None:
    segment = CubicBezierSegment(
        Point(0, 0, 0), Point(1, 2, 3), Point(2, 3, 4), Point(5, 8, 13)
    )
    assert segment.at(0.5).dimension == 3
    with pytest.raises(DimensionMismatch):
        CubicBezierSegment(Point(0, 0), Point(1, 1), Point(2, 2), Point(3, 3, 3))


def test_segment_interoperates_with_degree_generic_curve() -> None:
    segment = make_segment()
    curve = segment.as_curve()
    assert isinstance(curve, BezierCurve)
    assert np.array_equal(curve.control_points.array, [point.coords for point in segment])
    assert CubicBezierSegment.from_curve(curve) == segment
    with pytest.raises(DegreeError):
        CubicBezierSegment.from_curve(BezierCurve.linear(Point(0, 0), Point(1, 1)))


def test_segment_equality_and_repr_are_deterministic() -> None:
    segment = make_segment()
    assert segment == make_segment()
    assert repr(segment) == repr(make_segment())
