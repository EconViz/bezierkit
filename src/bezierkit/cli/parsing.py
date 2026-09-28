from __future__ import annotations

import json
import math
import sys
from typing import TextIO

from bezierkit import Point, Vector
from bezierkit.core.errors import BezierKitError


def parse_point(raw: str) -> Point:
    try:
        parts = [part.strip() for part in raw.split(",")]
        if not parts or any(not part for part in parts):
            raise ValueError
        return Point(*(float(part) for part in parts))
    except (TypeError, ValueError) as exc:
        raise BezierKitError(
            f"invalid point '{raw}': expected comma-separated numbers"
        ) from exc


def parse_vector(raw: str) -> Vector:
    point = parse_point(raw)
    return Vector(*point.coords)


def resolve_control_points(
    raw_points: list[str] | None,
    *,
    stream: TextIO | None = None,
) -> list[Point]:
    if raw_points:
        return [parse_point(raw) for raw in raw_points]
    input_stream = stream or sys.stdin
    if input_stream.isatty():
        raise BezierKitError("control points are required via --points or stdin JSON")
    try:
        payload = json.loads(input_stream.read())
        coordinates = payload["control_points"]
        if not isinstance(coordinates, list) or not coordinates:
            raise ValueError
        return [Point(*row) for row in coordinates]
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise BezierKitError(
            "invalid stdin: expected JSON object with a non-empty control_points array"
        ) from exc


def _parse_range(raw: str) -> list[float]:
    parts = raw.split(":")
    if len(parts) != 3:
        raise ValueError("range requires start:stop:step")
    start, stop, step = (float(part) for part in parts)
    if not all(math.isfinite(value) for value in (start, stop, step)):
        raise ValueError("range values must be finite")
    if step == 0 or (stop - start) * step < 0:
        raise ValueError("range step must move from start toward stop")
    count = int(math.floor(abs((stop - start) / step) + 1e-12)) + 1
    if count > 1_000_000:
        raise ValueError("range contains too many values")
    values = [start + index * step for index in range(count)]
    if not math.isclose(values[-1], stop, rel_tol=1e-12, abs_tol=1e-12):
        values.append(stop)
    else:
        values[-1] = stop
    return values


def parse_t_values(raw: list[str]) -> list[float]:
    try:
        values: list[float] = []
        for item in raw:
            values.extend(_parse_range(item) if ":" in item else [float(item)])
        if not values or not all(math.isfinite(value) for value in values):
            raise ValueError("at least one finite value is required")
        return values
    except (TypeError, ValueError) as exc:
        raise BezierKitError(
            "invalid parameter value: expected a number or start:stop:step"
        ) from exc
