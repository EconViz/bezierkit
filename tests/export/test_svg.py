import numpy as np

from bezierkit import CubicBezierSegment, PiecewiseBezier, Point
from bezierkit.export.svg import from_svg_path_data, to_svg_path_data


def fixture() -> PiecewiseBezier:
    outer = PiecewiseBezier(
        [
            CubicBezierSegment.from_line(Point(0, 0), Point(2, 0)),
            CubicBezierSegment.from_line(Point(2, 0), Point(0, 0)),
        ],
        closed=True,
    )
    inner = PiecewiseBezier(
        [CubicBezierSegment(Point(3, 0), Point(3, 1), Point(4, 1), Point(4, 0))]
    )
    return PiecewiseBezier.compound([outer, inner])


def test_svg_emits_native_cubics_and_round_trips_compound_geometry() -> None:
    path = fixture()
    data = to_svg_path_data(path, precision=3)
    assert data.startswith("M 0.000 0.000 C")
    assert data.count("M ") == 2
    assert data.count("C ") == 3
    assert " Z " in f" {data} "

    decoded = from_svg_path_data(data)
    assert tuple(subpath.closed for subpath in decoded.subpaths) == (True, False)
    for actual, expected in zip(decoded.segments, path.segments, strict=True):
        assert np.allclose(
            actual.at_many(np.linspace(0, 1, 101)).array,
            expected.at_many(np.linspace(0, 1, 101)).array,
            atol=1e-3,
        )


def test_svg_precision_and_coordinate_transform_are_configurable() -> None:
    data = to_svg_path_data(
        PiecewiseBezier([CubicBezierSegment.from_line(Point(0, 0), Point(1, 0))]),
        precision=2,
        transform=lambda point: Point(point.x + 10, -point.y + 5),
    )
    assert data == "M 10.00 5.00 C 10.33 5.00 10.67 5.00 11.00 5.00"
