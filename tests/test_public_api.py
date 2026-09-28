from bezierkit import (
    BezierCurve,
    BezierKitError,
    BezierSubpath,
    CubicBezierSegment,
    DegreeError,
    DimensionMismatch,
    ParameterOutOfDomain,
    PiecewiseBezier,
    Point,
    Vector,
    __version__,
)
from bezierkit.construction import EndpointDerivatives, PlanarSlopes, TangentDirections
from bezierkit.sampling import Sample, UniformSampler


def test_documented_public_api_is_importable() -> None:
    curve = BezierCurve.linear(Point(0, 0), Point(1, 1))
    assert curve.at(0.5) == Point(0.5, 0.5)
    assert Vector(1, 2).dimension == 2
    assert __version__ == "0.3.0"
    assert all(
        value is not None
        for value in [
            BezierKitError,
            BezierSubpath,
            CubicBezierSegment,
            DegreeError,
            DimensionMismatch,
            ParameterOutOfDomain,
            EndpointDerivatives,
            TangentDirections,
            PlanarSlopes,
            Sample,
            UniformSampler,
            PiecewiseBezier,
        ]
    )
