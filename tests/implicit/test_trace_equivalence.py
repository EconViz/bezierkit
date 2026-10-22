"""The array implementations return exactly what the cell-by-cell loops returned.

The reference functions below are the previous implementations, kept verbatim.
"""

from __future__ import annotations

import numpy as np
import pytest

from bezierkit.core.geometry.point import Point
from bezierkit.implicit import trace_implicit, trace_sampled
from bezierkit.implicit.trace import _interpolate, _marching_segments, _stitch


def reference_marching_segments(xs, ys, values, level):
    segments = []
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
                segments.extend((crossings[a], crossings[b]) for a, b in pairs)
    return segments


FIELDS = {
    "circle": lambda x, y: x * x + y * y,
    "hyperbola": lambda x, y: x * y,
    "saddles": lambda x, y: np.sin(2 * x) * np.cos(2 * y),
    "plateau": lambda x, y: np.floor(x) + np.floor(y),  # equal corner values everywhere
    "cubic": lambda x, y: x**3 - 3 * x + y * y,
}


@pytest.mark.parametrize("name", FIELDS)
def test_marching_segments_match_the_loop(name: str) -> None:
    xs, ys = np.linspace(-3, 3, 61), np.linspace(-2, 2, 41)
    values = FIELDS[name](*np.meshgrid(xs, ys))
    quantiles = np.quantile(values, [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]).tolist()
    for level in quantiles + [0.0, 1.0, 2.5]:
        assert _marching_segments(xs, ys, values, level) == reference_marching_segments(
            xs, ys, values, level
        )


def test_marching_segments_without_crossings() -> None:
    xs = ys = np.linspace(0, 1, 5)
    assert _marching_segments(xs, ys, np.ones((5, 5)), 2.0) == []


def reference_stitch(segments, *, tolerance):
    """The previous _stitch: the key of every endpoint is computed where it is used."""
    from collections import defaultdict

    scale = max(tolerance, np.finfo(float).eps)

    def key(point):
        return (round(point.x / scale), round(point.y / scale))

    unique = {}
    for first, second in segments:
        first_key, second_key = key(first), key(second)
        if first_key == second_key:
            continue
        unique[tuple(sorted((first_key, second_key)))] = (first, second)
    edges = list(unique.values())
    adjacency = defaultdict(list)
    for index, (first, second) in enumerate(edges):
        adjacency[key(first)].append(index)
        adjacency[key(second)].append(index)
    unused = set(range(len(edges)))
    chains = []

    def walk(start_edge, start_key):
        chain, current_edge, current_key, origin = [], start_edge, start_key, start_key
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

    for node in sorted(node for node, attached in adjacency.items() if len(attached) != 2):
        for edge in sorted(adjacency[node]):
            if edge in unused:
                chains.append(walk(edge, node))
    while unused:
        edge = min(unused)
        chains.append(walk(edge, min(key(edges[edge][0]), key(edges[edge][1]))))
    return chains


@pytest.mark.parametrize("name", ["circle", "hyperbola", "saddles", "cubic"])
def test_stitch_matches_per_point_keys(name: str) -> None:
    xs, ys = np.linspace(-3, 3, 61), np.linspace(-2, 2, 41)
    values = FIELDS[name](*np.meshgrid(xs, ys))
    tolerance = 6 / 60 * 1e-7
    for level in (0.0, 0.5, 1.0):
        raw = reference_marching_segments(xs, ys, values, level)
        assert _stitch(raw, tolerance=tolerance) == reference_stitch(raw, tolerance=tolerance)


def test_stitch_with_huge_coordinates_uses_the_per_point_path() -> None:
    raw = [(Point(1e10, 0.0), Point(2e10, 0.0)), (Point(2e10, 0.0), Point(3e10, 1.0))]
    assert _stitch(raw, tolerance=1e-9) == reference_stitch(raw, tolerance=1e-9)


def test_trace_sampled_equals_trace_implicit() -> None:
    def field(x: float, y: float) -> float:
        return x * x + 2.0 * y * y

    viewport, resolution = (-2.0, 2.0, -2.0, 2.0), (61, 51)
    xs, ys = np.linspace(-2.0, 2.0, 61), np.linspace(-2.0, 2.0, 51)
    values = np.asarray([[field(float(x), float(y)) for x in xs] for y in ys])
    a = trace_implicit(field, levels=[0.5, 1.5], viewport=viewport, resolution=resolution)
    b = trace_sampled(xs, ys, values, levels=[0.5, 1.5])
    assert a == b


def test_trace_sampled_validates_its_input() -> None:
    xs = ys = np.linspace(0.0, 1.0, 4)
    good = np.zeros((4, 4))
    with pytest.raises(ValueError):
        trace_sampled(xs, ys, np.zeros((3, 4)), levels=0.0)
    with pytest.raises(ValueError):
        trace_sampled(xs[::-1], ys, good, levels=0.0)
    with pytest.raises(ValueError):
        trace_sampled(xs, ys, good, levels=[])
    with pytest.raises(ValueError):
        trace_sampled(xs, ys, good, levels=0.0, tolerance=0.0)
    bad = good.copy()
    bad[1, 1] = np.nan
    with pytest.raises(ValueError):
        trace_sampled(xs, ys, bad, levels=0.0)
