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
    return _coordinate_distance(point.as_array(), start.as_array(), end.as_array())


def _coordinate_distance(value: np.ndarray, first: np.ndarray, last: np.ndarray) -> float:
    """Distance from ``value`` to the segment ``first``-``last``, one point at a time."""
    chord = last - first
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


# A batched norm or dot product can differ from the scalar one in the last bit on some platforms
# (OpenBLAS on x86-64 fuses multiply and add), so the points that could be the farthest are
# measured again one at a time, with the scalar formula. The result is then that of the
# point-by-point loop on every platform, not only where the two happen to agree. A point can be
# the farthest if its batched distance is within ``_BAND`` of the largest, relative to that
# distance, or within ``_BAND_ABSOLUTE`` of it relative to the size of the coordinates.
_BAND = 1e-9
_BAND_ABSOLUTE = 1e-12


def _batched_distances(
    array: np.ndarray, start: int, end: int, *, inclusive: bool = False
) -> np.ndarray:
    """Distances of the points between ``start`` and ``end`` to the chord, in one operation."""
    first = array[start]
    chord = array[end] - first
    denominator = float(chord @ chord)
    span = array[start : end + 1] if inclusive else array[start + 1 : end]
    if denominator == 0.0:
        return np.linalg.norm(span - first, axis=1)
    position = np.clip(((span - first) @ chord) / denominator, 0.0, 1.0)
    return np.linalg.norm(span - (first + position[:, None] * chord), axis=1)


_SCALAR_SPAN = 10  # below this many points one at a time is faster than the array calls


def _farthest(
    array: np.ndarray,
    start: int,
    end: int,
    *,
    inclusive: bool,
    floor: float,
    magnitude: float,
) -> tuple[int, float] | None:
    """Offset and exact distance of the farthest point from the chord.

    ``None`` when the batched maximum is clearly below ``floor``, so the exact maximum is
    too and the caller needs neither the point nor the distance. The first of equally far
    points wins, as in the point-by-point loop. ``magnitude`` is the largest coordinate.
    """
    first, last = array[start], array[end]
    base = start if inclusive else start + 1
    count = end + 1 - base if inclusive else end - base
    if count < _SCALAR_SPAN:
        best_offset, best = -1, -1.0
        for offset in range(count):
            value = _coordinate_distance(array[base + offset], first, last)
            if value > best:
                best_offset, best = offset, value
        return best_offset, best
    distances = _batched_distances(array, start, end, inclusive=inclusive)
    top = float(distances.max())
    band = max(_BAND * max(top, floor), _BAND_ABSOLUTE * magnitude)
    if top < floor - band:
        return None
    best_offset, best = -1, -1.0
    for offset in np.flatnonzero(distances >= top - band).tolist():
        value = _coordinate_distance(array[base + offset], first, last)
        if value > best:
            best_offset, best = offset, value
    return best_offset, best


def _magnitude(array: np.ndarray) -> float:
    return max(1.0, float(np.abs(array).max()))


def _rdp_indices(points: Sequence[Point], start: int, end: int, tolerance: float) -> list[int]:
    array = np.asarray([point.coords for point in points], dtype=float)
    return _rdp_array(array, start, end, tolerance, _magnitude(array))


def _rdp_array(
    array: np.ndarray, start: int, end: int, tolerance: float, magnitude: float
) -> list[int]:
    if end <= start + 1:
        return [start, end]
    far = _farthest(array, start, end, inclusive=False, floor=tolerance, magnitude=magnitude)
    if far is None or far[1] <= tolerance:
        return [start, end]
    split = start + 1 + far[0]
    return _rdp_array(array, start, split, tolerance, magnitude)[:-1] + _rdp_array(
        array, split, end, tolerance, magnitude
    )


def _span_error(array: np.ndarray, start: int, end: int, magnitude: float) -> float:
    """The largest distance from a point of ``start``..``end`` to its chord, exactly."""
    far = _farthest(array, start, end, inclusive=True, floor=0.0, magnitude=magnitude)
    assert far is not None  # floor 0 never prunes
    return far[1]


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
    normalized = _normalize_points(points, duplicate_tolerance=duplicate_tolerance, closed=closed)
    required = {0, len(normalized) - 1}
    if preserve_corners:
        required.update(
            index
            for index in range(1, len(normalized) - 1)
            if _turning_angle(normalized[index - 1], normalized[index], normalized[index + 1])
            >= threshold
        )
    array = np.asarray([point.coords for point in normalized], dtype=float)
    magnitude = _magnitude(array)
    anchors: list[int] = []
    ordered = sorted(required)
    for start, end in zip(ordered, ordered[1:], strict=False):
        section = _rdp_array(array, start, end, allowed, magnitude)
        anchors.extend(section[:-1])
    anchors.append(ordered[-1])

    segments: list[CubicBezierSegment] = []
    for start, end in zip(anchors, anchors[1:], strict=False):
        error = _span_error(array, start, end, magnitude)
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
