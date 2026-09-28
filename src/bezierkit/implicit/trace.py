from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Callable, Iterable
from dataclasses import dataclass

import numpy as np

from bezierkit.bezier.path import PiecewiseBezier
from bezierkit.bezier.segment import CubicBezierSegment
from bezierkit.core.geometry.point import Point
from bezierkit.core.geometry.vector import Vector
from bezierkit.fitting.polyline import fit_polyline

ScalarField = Callable[[float, float], float]
Gradient = Callable[[float, float], tuple[float, float] | Vector]


@dataclass(frozen=True, slots=True)
class LevelContours:
    """All disconnected paths traced for one scalar level."""

    level: float
    paths: tuple[PiecewiseBezier, ...]


@dataclass(frozen=True, slots=True)
class ContourSet:
    """Immutable traced contours grouped by level."""

    contours: tuple[LevelContours, ...]

    @property
    def level_values(self) -> tuple[float, ...]:
        return tuple(contour.level for contour in self.contours)

    @property
    def paths(self) -> tuple[PiecewiseBezier, ...]:
        return tuple(path for contour in self.contours for path in contour.paths)

    def for_level(self, level: float) -> tuple[PiecewiseBezier, ...]:
        value = float(level)
        for contour in self.contours:
            if contour.level == value:
                return contour.paths
        raise KeyError(f"level {value} was not traced")


def _interpolate(
    first: tuple[float, float],
    second: tuple[float, float],
    first_value: float,
    second_value: float,
    level: float,
) -> Point:
    denominator = second_value - first_value
    fraction = 0.5 if denominator == 0.0 else (level - first_value) / denominator
    fraction = min(1.0, max(0.0, fraction))
    return Point(
        first[0] + fraction * (second[0] - first[0]),
        first[1] + fraction * (second[1] - first[1]),
    )


def _marching_segments(
    xs: np.ndarray, ys: np.ndarray, values: np.ndarray, level: float
) -> list[tuple[Point, Point]]:
    segments: list[tuple[Point, Point]] = []
    for row in range(len(ys) - 1):
        for column in range(len(xs) - 1):
            corners = (
                (float(xs[column]), float(ys[row])),
                (float(xs[column + 1]), float(ys[row])),
                (float(xs[column + 1]), float(ys[row + 1])),
                (float(xs[column]), float(ys[row + 1])),
            )
            samples = (
                float(values[row, column]),
                float(values[row, column + 1]),
                float(values[row + 1, column + 1]),
                float(values[row + 1, column]),
            )
            high = tuple(value >= level for value in samples)
            edges = ((0, 1), (1, 2), (2, 3), (3, 0))
            crossings = {
                edge: _interpolate(
                    corners[start], corners[end], samples[start], samples[end], level
                )
                for edge, (start, end) in enumerate(edges)
                if high[start] != high[end]
            }
            if len(crossings) == 2:
                first, second = crossings.values()
                if first != second:
                    segments.append((first, second))
            elif len(crossings) == 4:
                center_high = sum(samples) / 4.0 >= level
                pairs = ((0, 1), (2, 3)) if center_high == high[0] else ((0, 3), (1, 2))
                segments.extend((crossings[first], crossings[second]) for first, second in pairs)
    return segments


def _stitch(
    segments: Iterable[tuple[Point, Point]], *, tolerance: float
) -> list[tuple[list[Point], bool]]:
    scale = max(tolerance, np.finfo(float).eps)

    def key(point: Point) -> tuple[int, int]:
        return (round(point.x / scale), round(point.y / scale))

    unique: dict[tuple[tuple[int, int], tuple[int, int]], tuple[Point, Point]] = {}
    for first, second in segments:
        first_key = key(first)
        second_key = key(second)
        if first_key == second_key:
            continue
        edge_key = tuple(sorted((first_key, second_key)))
        unique[edge_key] = (first, second)
    edges = list(unique.values())
    adjacency: dict[tuple[int, int], list[int]] = defaultdict(list)
    for index, (first, second) in enumerate(edges):
        adjacency[key(first)].append(index)
        adjacency[key(second)].append(index)
    unused = set(range(len(edges)))
    chains: list[tuple[list[Point], bool]] = []

    def walk(start_edge: int, start_key: tuple[int, int]) -> tuple[list[Point], bool]:
        chain: list[Point] = []
        current_edge = start_edge
        current_key = start_key
        origin = start_key
        while current_edge in unused:
            unused.remove(current_edge)
            first, second = edges[current_edge]
            if key(first) == current_key:
                chain.extend([first] if not chain else [])
                chain.append(second)
                current_key = key(second)
            else:
                chain.extend([second] if not chain else [])
                chain.append(first)
                current_key = key(first)
            if current_key == origin:
                return chain, True
            if len(adjacency[current_key]) != 2:
                return chain, False
            candidates = sorted(edge for edge in adjacency[current_key] if edge in unused)
            if not candidates:
                return chain, False
            current_edge = candidates[0]
        return chain, current_key == origin

    boundary_nodes = sorted(node for node, attached in adjacency.items() if len(attached) != 2)
    for node in boundary_nodes:
        for edge in sorted(adjacency[node]):
            if edge in unused:
                chains.append(walk(edge, node))
    while unused:
        edge = min(unused)
        chains.append(walk(edge, min(key(edges[edge][0]), key(edges[edge][1]))))
    return chains


def _gradient_segment(
    segment: CubicBezierSegment,
    gradient: Gradient,
    tolerance: float,
) -> CubicBezierSegment:
    chord = segment.p3 - segment.p0
    length = chord.norm()
    if length == 0.0:
        return segment

    def tangent(point: Point) -> Vector | None:
        raw = gradient(point.x, point.y)
        gx, gy = raw.coords if isinstance(raw, Vector) else raw
        direction = Vector(float(gy), -float(gx))
        if direction.norm() == 0.0:
            return None
        unit = direction.normalized()
        return unit if unit.dot(chord) >= 0.0 else unit * -1.0

    first = tangent(segment.p0)
    second = tangent(segment.p3)
    if first is None or second is None:
        return segment
    p1 = segment.p0 + first * (length / 3.0)
    p2 = segment.p3 - second * (length / 3.0)
    assert isinstance(p2, Point)
    candidate = CubicBezierSegment(segment.p0, p1, p2, segment.p3)
    samples = candidate.at_many(np.linspace(0.0, 1.0, 9))
    line = segment.p3 - segment.p0
    line_array = line.as_array()
    denominator = float(line_array @ line_array)
    deviations = []
    for point in samples:
        offset = point.as_array() - segment.p0.as_array()
        position = float(np.clip((offset @ line_array) / denominator, 0.0, 1.0))
        deviations.append(
            float(
                np.linalg.norm(
                    point.as_array() - (segment.p0.as_array() + position * line_array)
                )
            )
        )
    error = max(segment.fit_error or 0.0, max(deviations))
    if error > tolerance:
        return segment
    return CubicBezierSegment(*candidate.control_points, fit_error=error)


def trace_implicit(
    function: ScalarField,
    *,
    levels: float | Iterable[float],
    viewport: tuple[float, float, float, float],
    resolution: tuple[int, int] = (101, 101),
    tolerance: float = 1e-2,
    gradient: Gradient | None = None,
) -> ContourSet:
    """Trace ``F(x, y)=level`` using marching squares and cubic paths."""
    xmin, xmax, ymin, ymax = (float(value) for value in viewport)
    if not xmin < xmax or not ymin < ymax:
        raise ValueError("viewport bounds must be finite and increasing")
    if not all(math.isfinite(value) for value in (xmin, xmax, ymin, ymax)):
        raise ValueError("viewport bounds must be finite and increasing")
    nx, ny = resolution
    if nx < 2 or ny < 2:
        raise ValueError("resolution dimensions must be at least 2")
    allowed = float(tolerance)
    if not math.isfinite(allowed) or allowed <= 0.0:
        raise ValueError("tolerance must be finite and positive")
    level_values = (
        (float(levels),)
        if isinstance(levels, (int, float))
        else tuple(map(float, levels))
    )
    if not level_values or not all(math.isfinite(level) for level in level_values):
        raise ValueError("levels must contain finite values")

    xs = np.linspace(xmin, xmax, nx)
    ys = np.linspace(ymin, ymax, ny)
    values = np.asarray([[function(float(x), float(y)) for x in xs] for y in ys], dtype=float)
    if not np.all(np.isfinite(values)):
        raise ValueError("scalar field returned a non-finite value inside the viewport")
    join_tolerance = max((xmax - xmin) / (nx - 1), (ymax - ymin) / (ny - 1)) * 1e-7
    traced: list[LevelContours] = []
    for level in level_values:
        raw = _marching_segments(xs, ys, values, level)
        components = _stitch(raw, tolerance=join_tolerance)
        paths: list[PiecewiseBezier] = []
        for points, closed in components:
            if len(points) < (4 if closed else 2):
                continue
            path = fit_polyline(
                points,
                tolerance=allowed,
                closed=closed,
                preserve_corners=False,
                duplicate_tolerance=join_tolerance,
            )
            if gradient is not None:
                path = PiecewiseBezier(
                    [_gradient_segment(segment, gradient, allowed) for segment in path],
                    closed=path.closed,
                )
            paths.append(path)
        traced.append(LevelContours(level, tuple(paths)))
    return ContourSet(tuple(traced))
