from __future__ import annotations

import json
import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from bezierkit.bezier.path import BezierSubpath, PiecewiseBezier
from bezierkit.bezier.segment import CubicBezierSegment
from bezierkit.core.geometry.point import Point

SCHEMA = "bezierkit.path"
VERSION = 1


@dataclass(frozen=True, slots=True)
class PathDocument:
    """A versioned path plus language-neutral metadata."""

    path: PiecewiseBezier
    metadata: Mapping[str, Any] = field(default_factory=dict)


def _payload(path: PiecewiseBezier, metadata: Mapping[str, Any] | None) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "dimension": path.dimension,
        "subpaths": [
            {
                "closed": subpath.closed,
                "segments": [
                    [list(point.coords) for point in segment.control_points]
                    for segment in subpath.segments
                ],
            }
            for subpath in path.subpaths
        ],
        "metadata": dict(metadata or {}),
    }


def dumps(
    path: PiecewiseBezier,
    *,
    metadata: Mapping[str, Any] | None = None,
    indent: int | None = None,
) -> str:
    """Serialize a path using the stable, versioned JSON representation."""
    return json.dumps(
        _payload(path, metadata),
        allow_nan=False,
        ensure_ascii=False,
        indent=indent,
        separators=None if indent is not None else (",", ":"),
        sort_keys=True,
    )


def _coordinate(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("coordinates must be numbers")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("coordinates must be finite")
    return result


def loads(value: str) -> PathDocument:
    """Deserialize and validate a BezierKit path document."""
    try:
        payload = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError("invalid JSON path document") from exc
    if not isinstance(payload, dict) or payload.get("schema") != SCHEMA:
        raise ValueError(f"schema must be {SCHEMA!r}")
    if payload.get("version") != VERSION:
        raise ValueError(f"unsupported schema version {payload.get('version')!r}")
    dimension = payload.get("dimension")
    if not isinstance(dimension, int) or isinstance(dimension, bool) or dimension < 1:
        raise ValueError("dimension must be a positive integer")
    raw_subpaths = payload.get("subpaths")
    if not isinstance(raw_subpaths, list) or not raw_subpaths:
        raise ValueError("subpaths must be a non-empty array")
    subpaths: list[BezierSubpath] = []
    for raw_subpath in raw_subpaths:
        if not isinstance(raw_subpath, dict) or not isinstance(raw_subpath.get("closed"), bool):
            raise ValueError("each subpath requires a boolean closed value")
        raw_segments = raw_subpath.get("segments")
        if not isinstance(raw_segments, list) or not raw_segments:
            raise ValueError("each subpath requires a non-empty segments array")
        segments: list[CubicBezierSegment] = []
        for raw_segment in raw_segments:
            if not isinstance(raw_segment, list) or len(raw_segment) != 4:
                raise ValueError("each cubic segment requires four control points")
            points: list[Point] = []
            for raw_point in raw_segment:
                if not isinstance(raw_point, list) or len(raw_point) != dimension:
                    raise ValueError("control point dimension does not match document dimension")
                points.append(Point(*(_coordinate(coordinate) for coordinate in raw_point)))
            segments.append(CubicBezierSegment(*points))
        subpaths.append(BezierSubpath(segments, closed=raw_subpath["closed"]))
    metadata = payload.get("metadata", {})
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be a JSON object")
    json.dumps(metadata, allow_nan=False)
    return PathDocument(PiecewiseBezier._from_subpaths(subpaths), metadata)
