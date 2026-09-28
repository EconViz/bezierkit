from __future__ import annotations

from bezierkit.bezier.path import PiecewiseBezier
from bezierkit.bezier.segment import CubicBezierSegment
from bezierkit.core.geometry.point import Point
from bezierkit.export._coordinates import CoordinateTransform, number, transformed


def _coordinate(point: Point, precision: int) -> str:
    return f"({number(point.x, precision)},{number(point.y, precision)})"


def segment_to_tikz(
    segment: CubicBezierSegment,
    *,
    precision: int = 6,
    transform: CoordinateTransform | None = None,
    include_start: bool = True,
) -> str:
    """Serialize one segment using native TikZ cubic control syntax."""
    if segment.dimension != 2:
        raise ValueError("TikZ path output requires two-dimensional geometry")
    p0, p1, p2, p3 = (
        transformed(point, transform) for point in segment.control_points
    )
    start = f"{_coordinate(p0, precision)} " if include_start else ""
    return (
        f"{start}.. controls {_coordinate(p1, precision)} and "
        f"{_coordinate(p2, precision)} .. {_coordinate(p3, precision)}"
    )


def to_tikz(
    path: PiecewiseBezier,
    *,
    precision: int = 6,
    transform: CoordinateTransform | None = None,
    options: str | None = None,
) -> str:
    """Serialize each subpath as a geometry-only TikZ draw command."""
    option_text = f"[{options}]" if options else ""
    lines: list[str] = []
    for subpath in path.subpaths:
        pieces = [
            segment_to_tikz(
                segment,
                precision=precision,
                transform=transform,
                include_start=index == 0,
            )
            for index, segment in enumerate(subpath.segments)
        ]
        close = " -- cycle" if subpath.closed else ""
        lines.append(f"\\draw{option_text} {' '.join(pieces)}{close};")
    return "\n".join(lines)
