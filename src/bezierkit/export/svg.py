from __future__ import annotations

import re
from collections.abc import Iterator

from bezierkit.bezier.path import BezierSubpath, PiecewiseBezier
from bezierkit.bezier.segment import CubicBezierSegment
from bezierkit.core.geometry.point import Point
from bezierkit.export._coordinates import CoordinateTransform, number, transformed

_TOKEN = re.compile(r"[MCZ]|[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?", re.IGNORECASE)


def _pair(point: Point, precision: int) -> str:
    return f"{number(point.x, precision)} {number(point.y, precision)}"


def to_svg_path_data(
    path: PiecewiseBezier,
    *,
    precision: int = 6,
    transform: CoordinateTransform | None = None,
) -> str:
    """Serialize geometry as deterministic SVG path data using M, C, and Z."""
    if path.dimension != 2:
        raise ValueError("SVG path data requires two-dimensional geometry")
    commands: list[str] = []
    for subpath in path.subpaths:
        start = transformed(subpath.segments[0].p0, transform)
        commands.extend(("M", _pair(start, precision)))
        for segment in subpath.segments:
            p1, p2, p3 = (
                transformed(point, transform)
                for point in (segment.p1, segment.p2, segment.p3)
            )
            commands.extend(("C", _pair(p1, precision), _pair(p2, precision), _pair(p3, precision)))
        if subpath.closed:
            commands.append("Z")
    return " ".join(commands)


def _numbers(tokens: Iterator[str], count: int) -> list[float]:
    values: list[float] = []
    for _ in range(count):
        try:
            token = next(tokens)
        except StopIteration as exc:
            raise ValueError("incomplete SVG path command") from exc
        if token.upper() in {"M", "C", "Z"}:
            raise ValueError("incomplete SVG path command")
        values.append(float(token))
    return values


def from_svg_path_data(value: str) -> PiecewiseBezier:
    """Parse the absolute M/C/Z subset emitted by :func:`to_svg_path_data`."""
    raw_tokens = _TOKEN.findall(value)
    if "".join(raw_tokens).lower() != re.sub(r"[\s,]+", "", value).lower():
        raise ValueError("unsupported SVG path syntax")
    tokens = iter(raw_tokens)
    subpaths: list[BezierSubpath] = []
    segments: list[CubicBezierSegment] = []
    current: Point | None = None
    closed = False

    def finish() -> None:
        nonlocal segments, closed
        if segments:
            subpaths.append(BezierSubpath(segments, closed=closed))
        segments = []
        closed = False

    for token in tokens:
        command = token.upper()
        if command == "M":
            finish()
            current = Point(*_numbers(tokens, 2))
        elif command == "C":
            if current is None:
                raise ValueError("SVG cubic command requires a current point")
            coordinates = _numbers(tokens, 6)
            p1 = Point(*coordinates[0:2])
            p2 = Point(*coordinates[2:4])
            p3 = Point(*coordinates[4:6])
            segments.append(CubicBezierSegment(current, p1, p2, p3))
            current = p3
        elif command == "Z":
            if not segments:
                raise ValueError("SVG close command requires a subpath")
            closed = True
            finish()
            current = None
        else:
            raise ValueError(f"unsupported SVG path command {token!r}")
    finish()
    if not subpaths:
        raise ValueError("SVG path data contains no cubic segments")
    return PiecewiseBezier._from_subpaths(subpaths)
