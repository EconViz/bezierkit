"""A small mathematical toolkit for constructing and analyzing Bézier curves."""

from importlib.metadata import PackageNotFoundError, version

from bezierkit.bezier.curve import BezierCurve
from bezierkit.bezier.path import BezierSubpath, PiecewiseBezier
from bezierkit.bezier.segment import CubicBezierSegment
from bezierkit.core.errors import (
    BezierKitError,
    DegreeError,
    DimensionMismatch,
    ParameterOutOfDomain,
    ToleranceNotMet,
)
from bezierkit.core.geometry.point import Point
from bezierkit.core.geometry.vector import Vector

try:
    __version__ = version("bezierkit")
except PackageNotFoundError:  # pragma: no cover - not installed, e.g. running from source
    __version__ = "0.0.0+unknown"

__all__ = [
    "BezierCurve",
    "BezierKitError",
    "BezierSubpath",
    "CubicBezierSegment",
    "DegreeError",
    "DimensionMismatch",
    "ParameterOutOfDomain",
    "PiecewiseBezier",
    "Point",
    "ToleranceNotMet",
    "Vector",
    "__version__",
]
