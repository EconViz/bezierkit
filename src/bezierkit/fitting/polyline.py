from __future__ import annotations

import math
from collections.abc import Iterable, Sequence

import numpy as np

from bezierkit.bezier.path import PiecewiseBezier
from bezierkit.bezier.segment import CubicBezierSegment
from bezierkit.core.geometry.point import Point


def _distance(first: Point, second: Point) -> float:
    return math.dist(first.coords, second.coords)


def _point_segment_distance(point: Point, start: Point, end: Point) -> float:
    value = point.as_array()
    first = start.as_array()
    chord = end.as_array() - first
    denominator = float(chord @ chord)
    if denominator == 0.0:
        return float(np.linalg.norm(value - first))
    position = float(np.clip(((value - first) @ chord) / denominator, 0.0, 1.0))
    return float(np.linalg.norm(value - (first + position * chord)))


def _normalize_points(
    points: Iterable[Point], *, duplicate_tolerance: float, closed: bool
) -> list[Point]:
    tolerance = float(duplicate_tolerance)
    if not math.isfinite(tolerance) or tolerance < 0.0:
        raise ValueError("duplicate_tolerance must be finite and non-negative")
    materialized = list(points)
    if not materialized:
        raise ValueError("a polyline requires points")
    dimension = materialized[0].dimension
    if any(point.dimension != dimension for point in materialized):
        raise ValueError("polyline point dimensions must match")
    normalized = [materialized[0]]
    for point in materialized[1:]:
        if _distance(point, normalized[-1]) > tolerance:
            normalized.append(point)
    if closed and len(normalized) > 1 and _distance(normalized[-1], normalized[0]) <= tolerance:
        normalized.pop()
    minimum = 3 if closed else 2
    if len(normalized) < minimum:
        raise ValueError(f"a {'closed' if closed else 'open'} polyline requires {minimum} points")
    if closed:
        seam = min(range(len(normalized)), key=lambda index: normalized[index].coords)
        normalized = normalized[seam:] + normalized[:seam]
        normalized.append(normalized[0])
    return normalized


def _turning_angle(previous: Point, current: Point, following: Point) -> float:
    incoming = current.as_array() - previous.as_array()
    outgoing = following.as_array() - current.as_array()
    denominator = float(np.linalg.norm(incoming) * np.linalg.norm(outgoing))
    if denominator == 0.0:
        return 0.0
    cosine = float(np.clip((incoming @ outgoing) / denominator, -1.0, 1.0))
    return math.acos(cosine)


def _rdp_indices(points: Sequence[Point], start: int, end: int, tolerance: float) -> list[int]:
    if end <= start + 1:
        return [start, end]
    distances = [
        _point_segment_distance(points[index], points[start], points[end])
        for index in range(start + 1, end)
    ]
    maximum = max(distances)
    if maximum <= tolerance:
        return [start, end]
    split = start + 1 + distances.index(maximum)
    return _rdp_indices(points, start, split, tolerance)[:-1] + _rdp_indices(
        points, split, end, tolerance
    )


def fit_polyline(
    points: Iterable[Point],
    *,
    tolerance: float,
    closed: bool = False,
    duplicate_tolerance: float = 1e-12,
    preserve_corners: bool = True,
    corner_angle: float = math.pi / 4.0,
) -> PiecewiseBezier:
    """Simplify a sampled polyline and encode its chords as exact cubics."""
    allowed = float(tolerance)
    if not math.isfinite(allowed) or allowed < 0.0:
        raise ValueError("tolerance must be finite and non-negative")
    threshold = float(corner_angle)
    if not 0.0 <= threshold <= math.pi:
        raise ValueError("corner_angle must lie in [0, pi]")
    normalized = _normalize_points(
        points, duplicate_tolerance=duplicate_tolerance, closed=closed
    )
    required = {0, len(normalized) - 1}
    if preserve_corners:
        required.update(
            index
            for index in range(1, len(normalized) - 1)
            if _turning_angle(
                normalized[index - 1], normalized[index], normalized[index + 1]
            )
            >= threshold
        )
    anchors: list[int] = []
    ordered = sorted(required)
    for start, end in zip(ordered, ordered[1:], strict=False):
        section = _rdp_indices(normalized, start, end, allowed)
        anchors.extend(section[:-1])
    anchors.append(ordered[-1])

    segments: list[CubicBezierSegment] = []
    for start, end in zip(anchors, anchors[1:], strict=False):
        error = max(
            _point_segment_distance(point, normalized[start], normalized[end])
            for point in normalized[start : end + 1]
        )
        segment = CubicBezierSegment.from_line(normalized[start], normalized[end])
        segments.append(CubicBezierSegment(*segment.control_points, fit_error=error))
    return PiecewiseBezier(segments, closed=closed)


def maximum_polyline_deviation(points: Iterable[Point], path: PiecewiseBezier) -> float:
    """Measure source vertices against the nearest output segment chord."""
    materialized = list(points)
    if not materialized:
        raise ValueError("a polyline requires points")
    return max(
        min(_point_segment_distance(point, segment.p0, segment.p3) for segment in path)
        for point in materialized
    )
