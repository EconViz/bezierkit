"""The array RDP and fit error return exactly what the per-point loops returned."""

from __future__ import annotations

import math

import numpy as np
import pytest

from bezierkit.bezier.segment import CubicBezierSegment
from bezierkit.core.geometry.point import Point
from bezierkit.fitting import polyline
from bezierkit.fitting.polyline import _normalize_points, _point_segment_distance, fit_polyline


def reference_rdp(points, start, end, tolerance):
    if end <= start + 1:
        return [start, end]
    distances = [
        _point_segment_distance(points[i], points[start], points[end])
        for i in range(start + 1, end)
    ]
    maximum = max(distances)
    if maximum <= tolerance:
        return [start, end]
    split = start + 1 + distances.index(maximum)
    return reference_rdp(points, start, split, tolerance)[:-1] + reference_rdp(
        points, split, end, tolerance
    )


def random_polylines(seed: int = 7):
    rng = np.random.default_rng(seed)
    for _ in range(150):
        n = int(rng.integers(3, 60))
        kind = rng.integers(0, 4)
        t = np.sort(rng.uniform(0, 2 * np.pi, n))
        if kind == 0:  # noisy circle
            pts = np.c_[np.cos(t), np.sin(t)] + rng.normal(0, 0.01, (n, 2))
        elif kind == 1:  # integer grid, many collinear and repeated points
            pts = rng.integers(0, 6, (n, 2)).astype(float)
        elif kind == 2:  # a line
            pts = np.c_[t, 2 * t + 1]
        else:
            pts = rng.uniform(-1, 1, (n, 2))
        yield [Point(float(x), float(y)) for x, y in pts]


@pytest.mark.parametrize("tolerance", [0.0, 0.005, 0.05, 0.5])
def test_rdp_indices_match(tolerance: float) -> None:
    for points in random_polylines():
        last = len(points) - 1
        assert polyline._rdp_indices(points, 0, last, tolerance) == reference_rdp(
            points, 0, last, tolerance
        )


@pytest.mark.parametrize("closed", [False, True])
@pytest.mark.parametrize("corners", [False, True])
def test_fit_polyline_matches_reference(closed: bool, corners: bool) -> None:
    checked = 0
    for points in random_polylines(11):
        for tolerance in (0.005, 0.05):
            try:
                normalized = _normalize_points(points, duplicate_tolerance=1e-9, closed=closed)
            except ValueError:
                continue
            fitted = fit_polyline(
                points,
                tolerance=tolerance,
                closed=closed,
                duplicate_tolerance=1e-9,
                preserve_corners=corners,
            )
            required = {0, len(normalized) - 1}
            if corners:
                required.update(
                    i
                    for i in range(1, len(normalized) - 1)
                    if polyline._turning_angle(normalized[i - 1], normalized[i], normalized[i + 1])
                    >= math.pi / 4.0
                )
            anchors, ordered = [], sorted(required)
            for start, end in zip(ordered, ordered[1:], strict=False):
                anchors.extend(reference_rdp(normalized, start, end, tolerance)[:-1])
            anchors.append(ordered[-1])
            expected = []
            for start, end in zip(anchors, anchors[1:], strict=False):
                error = max(
                    _point_segment_distance(p, normalized[start], normalized[end])
                    for p in normalized[start : end + 1]
                )
                line = CubicBezierSegment.from_line(normalized[start], normalized[end])
                expected.append(CubicBezierSegment(*line.control_points, fit_error=error))
            assert len(fitted.segments) == len(expected)
            for a, b in zip(fitted.segments, expected, strict=True):
                assert a.control_points == b.control_points
                assert a.fit_error == b.fit_error
            checked += 1
    assert checked > 100
