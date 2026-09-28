from __future__ import annotations

import math
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass

import numpy as np

from bezierkit.bezier.segment import CubicBezierSegment
from bezierkit.core.capabilities.curve import ParametricCurve
from bezierkit.core.capabilities.reversible import Reversible
from bezierkit.core.capabilities.subdividable import Subdividable
from bezierkit.core.domain.interval import Interval
from bezierkit.core.domain.parameter import ParameterValues
from bezierkit.core.errors import DimensionMismatch
from bezierkit.core.geometry.point import Point
from bezierkit.core.geometry.point_set import PointSet


def _distance(first: Point, second: Point) -> float:
    if first.dimension != second.dimension:
        raise DimensionMismatch(
            f"endpoint dimensions differ: {first.dimension} and {second.dimension}"
        )
    return math.dist(first.coords, second.coords)


@dataclass(frozen=True, slots=True)
class BezierSubpath:
    """One continuous sequence of cubic segments."""

    segments: tuple[CubicBezierSegment, ...]
    closed: bool = False
    continuity_tolerance: float = 1e-9

    def __init__(
        self,
        segments: Iterable[CubicBezierSegment],
        *,
        closed: bool = False,
        continuity_tolerance: float = 1e-9,
    ) -> None:
        materialized = tuple(segments)
        tolerance = float(continuity_tolerance)
        if not materialized:
            raise ValueError("a subpath requires at least one segment")
        if not math.isfinite(tolerance) or tolerance < 0.0:
            raise ValueError("continuity_tolerance must be finite and non-negative")
        dimensions = {segment.dimension for segment in materialized}
        if len(dimensions) != 1:
            raise DimensionMismatch(f"segment dimensions differ: {sorted(dimensions)}")
        for first, second in zip(materialized, materialized[1:], strict=False):
            if _distance(first.p3, second.p0) > tolerance:
                raise ValueError("adjacent segments are not continuous within the tolerance")
        if closed and _distance(materialized[-1].p3, materialized[0].p0) > tolerance:
            raise ValueError("closed path endpoints do not meet within the tolerance")
        object.__setattr__(self, "segments", materialized)
        object.__setattr__(self, "closed", bool(closed))
        object.__setattr__(self, "continuity_tolerance", tolerance)

    @property
    def dimension(self) -> int:
        return self.segments[0].dimension


@dataclass(frozen=True, slots=True, init=False)
class PiecewiseBezier(ParametricCurve, Subdividable, Reversible):
    """A renderer-neutral collection of continuous cubic subpaths.

    For a single subpath, the unit parameter interval is divided uniformly
    across segments. Evaluation and splitting are intentionally undefined for
    compound paths because their subpaths are independent.
    """

    subpaths: tuple[BezierSubpath, ...]

    def __init__(
        self,
        segments: Iterable[CubicBezierSegment],
        *,
        closed: bool = False,
        continuity_tolerance: float = 1e-9,
    ) -> None:
        object.__setattr__(
            self,
            "subpaths",
            (BezierSubpath(segments, closed=closed, continuity_tolerance=continuity_tolerance),),
        )

    @classmethod
    def _from_subpaths(cls, subpaths: Sequence[BezierSubpath]) -> PiecewiseBezier:
        if not subpaths:
            raise ValueError("a piecewise path requires at least one subpath")
        dimensions = {subpath.dimension for subpath in subpaths}
        if len(dimensions) != 1:
            raise DimensionMismatch(f"subpath dimensions differ: {sorted(dimensions)}")
        result = object.__new__(cls)
        object.__setattr__(result, "subpaths", tuple(subpaths))
        return result

    @classmethod
    def compound(cls, paths: Iterable[PiecewiseBezier]) -> PiecewiseBezier:
        subpaths: list[BezierSubpath] = []
        for path in paths:
            subpaths.extend(path.subpaths)
        return cls._from_subpaths(subpaths)

    @property
    def segments(self) -> tuple[CubicBezierSegment, ...]:
        return tuple(segment for subpath in self.subpaths for segment in subpath.segments)

    @property
    def control_points(self) -> tuple[tuple[Point, Point, Point, Point], ...]:
        return tuple(segment.control_points for segment in self.segments)

    @property
    def closed(self) -> bool:
        return len(self.subpaths) == 1 and self.subpaths[0].closed

    @property
    def is_compound(self) -> bool:
        return len(self.subpaths) > 1

    @property
    def dimension(self) -> int:
        return self.subpaths[0].dimension

    @property
    def domain(self) -> Interval:
        return Interval(0.0, 1.0)

    def __iter__(self) -> Iterator[CubicBezierSegment]:
        return iter(self.segments)

    def _single_segments(self, operation: str) -> tuple[CubicBezierSegment, ...]:
        if self.is_compound:
            raise ValueError(f"cannot {operation} a compound path")
        return self.subpaths[0].segments

    def at(self, t: float) -> Point:
        segments = self._single_segments("evaluate")
        value = float(ParameterValues.from_input([t], domain=self.domain).array[0])
        if value == 1.0:
            return segments[-1].at(1.0)
        scaled = value * len(segments)
        index = min(int(scaled), len(segments) - 1)
        return segments[index].at(scaled - index)

    def at_many(self, t: Iterable[float] | np.ndarray) -> PointSet:
        values = ParameterValues.from_input(t, domain=self.domain)
        return PointSet([self.at(float(value)) for value in values.array])

    def reversed(self) -> PiecewiseBezier:
        reversed_subpaths = [
            BezierSubpath(
                (segment.reversed() for segment in reversed(subpath.segments)),
                closed=subpath.closed,
                continuity_tolerance=subpath.continuity_tolerance,
            )
            for subpath in self.subpaths
        ]
        return self._from_subpaths(reversed_subpaths)

    def split(self, t: float) -> tuple[PiecewiseBezier, PiecewiseBezier]:
        segments = self._single_segments("split")
        if self.closed:
            raise ValueError("can only split an open path")
        tolerance = self.subpaths[0].continuity_tolerance
        value = float(ParameterValues.from_input([t], domain=self.domain).array[0])
        if value == 0.0:
            point = segments[0].p0
            return (
                PiecewiseBezier(
                    [CubicBezierSegment.from_line(point, point)],
                    continuity_tolerance=tolerance,
                ),
                self,
            )
        if value == 1.0:
            point = segments[-1].p3
            return self, PiecewiseBezier(
                [CubicBezierSegment.from_line(point, point)],
                continuity_tolerance=tolerance,
            )
        scaled = value * len(segments)
        index = min(int(scaled), len(segments) - 1)
        local = scaled - index
        if local == 0.0:
            return (
                PiecewiseBezier(segments[:index], continuity_tolerance=tolerance),
                PiecewiseBezier(segments[index:], continuity_tolerance=tolerance),
            )
        left_segment, right_segment = segments[index].split(local)
        return (
            PiecewiseBezier(
                (*segments[:index], left_segment),
                continuity_tolerance=tolerance,
            ),
            PiecewiseBezier(
                (right_segment, *segments[index + 1 :]),
                continuity_tolerance=tolerance,
            ),
        )

    def segment(self, t0: float, t1: float) -> PiecewiseBezier:
        start = float(ParameterValues.from_input([t0], domain=self.domain).array[0])
        end = float(ParameterValues.from_input([t1], domain=self.domain).array[0])
        if start > end:
            raise ValueError(f"t0 ({start}) must be <= t1 ({end})")
        if start == end:
            point = self.at(start)
            return PiecewiseBezier(
                [CubicBezierSegment.from_line(point, point)],
                continuity_tolerance=self.subpaths[0].continuity_tolerance,
            )
        if start == 0.0 and end == 1.0:
            return self
        _, suffix = self.split(start)
        relative_end = (end - start) / (1.0 - start)
        prefix, _ = suffix.split(relative_end)
        return prefix
