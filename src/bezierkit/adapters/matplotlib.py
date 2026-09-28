from __future__ import annotations

import math
from typing import TYPE_CHECKING

import numpy as np

from bezierkit.bezier.conversion import line_to_cubic, quadratic_to_cubic
from bezierkit.bezier.path import BezierSubpath, PiecewiseBezier
from bezierkit.bezier.segment import CubicBezierSegment
from bezierkit.core.geometry.point import Point
from bezierkit.fitting.polyline import fit_polyline

if TYPE_CHECKING:
    from matplotlib.path import Path
    from matplotlib.transforms import Transform


def _matplotlib_path_type() -> type[Path]:
    try:
        from matplotlib.path import Path
    except ImportError as exc:  # pragma: no cover - exercised in package smoke tests
        raise ImportError(
            "Matplotlib interoperability requires `pip install 'bezierkit[matplotlib]'`"
        ) from exc
    return Path


def _transform_point(point: Point, transform: Transform | None) -> Point:
    if transform is None:
        return point
    values = np.asarray(transform.transform(np.asarray([point.coords], dtype=float)))[0]
    return Point(*values)


def _transform_segment(
    segment: CubicBezierSegment, transform: Transform | None
) -> CubicBezierSegment:
    return CubicBezierSegment(
        *(_transform_point(point, transform) for point in segment.control_points)
    )


def from_path(path: Path, *, transform: Transform | None = None) -> PiecewiseBezier:
    """Convert Matplotlib path codes exactly, optionally under an affine transform."""
    Path = _matplotlib_path_type()
    if transform is not None and not transform.is_affine:
        raise ValueError(
            "non-affine transforms are not exact; use approximate_path with a tolerance"
        )
    vertices = np.asarray(path.vertices, dtype=float)
    if vertices.ndim != 2 or vertices.shape[1] != 2 or not np.all(np.isfinite(vertices)):
        raise ValueError("Matplotlib path vertices must be finite two-dimensional values")
    codes = path.codes
    if codes is None:
        codes = np.asarray([Path.MOVETO, *([Path.LINETO] * (len(vertices) - 1))])
    if len(codes) != len(vertices):
        raise ValueError("Matplotlib path vertices and codes must have matching lengths")

    subpaths: list[BezierSubpath] = []
    segments: list[CubicBezierSegment] = []
    current: Point | None = None
    start: Point | None = None

    def finish(*, closed: bool = False) -> None:
        nonlocal segments, current, start
        if segments:
            subpaths.append(BezierSubpath(segments, closed=closed))
        segments = []
        current = None
        start = None

    index = 0
    while index < len(vertices):
        code = int(codes[index])
        point = Point(*vertices[index])
        if code == Path.MOVETO:
            finish()
            current = point
            start = point
            index += 1
        elif code == Path.LINETO:
            if current is None:
                raise ValueError("LINETO requires a preceding MOVETO")
            segments.append(line_to_cubic(current, point))
            current = point
            index += 1
        elif code == Path.CURVE3:
            if current is None or index + 1 >= len(vertices) or codes[index + 1] != Path.CURVE3:
                raise ValueError("CURVE3 requires two consecutive vertices")
            end = Point(*vertices[index + 1])
            segments.append(quadratic_to_cubic(current, point, end))
            current = end
            index += 2
        elif code == Path.CURVE4:
            if (
                current is None
                or index + 2 >= len(vertices)
                or codes[index + 1] != Path.CURVE4
                or codes[index + 2] != Path.CURVE4
            ):
                raise ValueError("CURVE4 requires three consecutive vertices")
            second = Point(*vertices[index + 1])
            end = Point(*vertices[index + 2])
            segments.append(CubicBezierSegment(current, point, second, end))
            current = end
            index += 3
        elif code == Path.CLOSEPOLY:
            if current is None or start is None:
                raise ValueError("CLOSEPOLY requires an active subpath")
            if current != start:
                segments.append(line_to_cubic(current, start))
            finish(closed=True)
            index += 1
        elif code == Path.STOP:
            finish()
            index += 1
        else:
            raise ValueError(f"unsupported Matplotlib path code {code}")
    finish()
    if not subpaths:
        raise ValueError("Matplotlib path contains no drawable segments")
    converted = PiecewiseBezier._from_subpaths(subpaths)
    if transform is None:
        return converted
    return PiecewiseBezier._from_subpaths(
        [
            BezierSubpath(
                [_transform_segment(segment, transform) for segment in subpath.segments],
                closed=subpath.closed,
            )
            for subpath in converted.subpaths
        ]
    )


def to_path(path: PiecewiseBezier) -> Path:
    """Convert every cubic and subpath boundary to a Matplotlib Path."""
    Path = _matplotlib_path_type()
    if path.dimension != 2:
        raise ValueError("Matplotlib Path requires two-dimensional geometry")
    vertices: list[tuple[float, float]] = []
    codes: list[int] = []
    for subpath in path.subpaths:
        start = subpath.segments[0].p0
        vertices.append((start.x, start.y))
        codes.append(Path.MOVETO)
        for segment in subpath.segments:
            for point in (segment.p1, segment.p2, segment.p3):
                vertices.append((point.x, point.y))
                codes.append(Path.CURVE4)
        if subpath.closed:
            vertices.append((start.x, start.y))
            codes.append(Path.CLOSEPOLY)
    return Path(np.asarray(vertices), np.asarray(codes, dtype=np.uint8))


def _distance_to_chord(point: Point, start: Point, end: Point) -> float:
    value = point.as_array()
    first = start.as_array()
    chord = end.as_array() - first
    denominator = float(chord @ chord)
    if denominator == 0.0:
        return float(np.linalg.norm(value - first))
    position = float(np.clip(((value - first) @ chord) / denominator, 0.0, 1.0))
    return float(np.linalg.norm(value - (first + position * chord)))


def _flatten_transformed(
    segment: CubicBezierSegment,
    transform: Transform,
    tolerance: float,
    *,
    max_depth: int = 20,
) -> list[Point]:
    def transformed_at(parameter: float) -> Point:
        return _transform_point(segment.at(parameter), transform)

    def refine(
        t0: float, p0: Point, t1: float, p1: Point, depth: int
    ) -> list[Point]:
        midpoint = (t0 + t1) / 2.0
        middle = transformed_at(midpoint)
        if _distance_to_chord(middle, p0, p1) <= tolerance:
            return [p0, p1]
        if depth >= max_depth:
            raise ValueError("non-affine approximation did not meet tolerance")
        left = refine(t0, p0, midpoint, middle, depth + 1)
        right = refine(midpoint, middle, t1, p1, depth + 1)
        return left[:-1] + right

    return refine(0.0, transformed_at(0.0), 1.0, transformed_at(1.0), 0)


def approximate_path(
    path: Path,
    transform: Transform,
    *,
    tolerance: float,
    max_depth: int = 20,
) -> PiecewiseBezier:
    """Explicitly approximate a path under a non-affine transform."""
    allowed = float(tolerance)
    if not math.isfinite(allowed) or allowed <= 0.0:
        raise ValueError("tolerance must be finite and positive")
    source = from_path(path)
    approximated: list[PiecewiseBezier] = []
    for subpath in source.subpaths:
        points: list[Point] = []
        for segment in subpath.segments:
            flattened = _flatten_transformed(
                segment, transform, allowed / 2.0, max_depth=max_depth
            )
            points.extend(flattened if not points else flattened[1:])
        approximated.append(
            fit_polyline(
                points,
                tolerance=allowed / 2.0,
                closed=subpath.closed,
                preserve_corners=True,
            )
        )
    return PiecewiseBezier.compound(approximated) if len(approximated) > 1 else approximated[0]
