import shutil
import subprocess

import numpy as np
import pytest
from matplotlib.path import Path

from bezierkit import BezierCurve, CubicBezierSegment, PiecewiseBezier, Point
from bezierkit.adapters.matplotlib import from_path, to_path
from bezierkit.bezier.conversion import to_cubic
from bezierkit.export.json import dumps, loads
from bezierkit.export.svg import from_svg_path_data, to_svg_path_data
from bezierkit.export.tikz import to_tikz


def shared_fixture() -> PiecewiseBezier:
    line = to_cubic(BezierCurve.linear(Point(0, 0), Point(1, 1)))
    quadratic = to_cubic(
        BezierCurve.quadratic(Point(1, 1), Point(2, 3), Point(3, 1))
    )
    cubic = CubicBezierSegment(Point(3, 1), Point(4, 2), Point(5, 0), Point(0, 0))
    closed = PiecewiseBezier([line, quadratic, cubic], closed=True)
    open_path = PiecewiseBezier(
        [CubicBezierSegment.from_line(Point(10, 0), Point(11, 1))]
    )
    return PiecewiseBezier.compound([closed, open_path])


def assert_geometry_equal(actual: PiecewiseBezier, expected: PiecewiseBezier) -> None:
    assert tuple(subpath.closed for subpath in actual.subpaths) == tuple(
        subpath.closed for subpath in expected.subpaths
    )
    assert len(actual.segments) == len(expected.segments)
    parameters = np.linspace(0.0, 1.0, 101)
    for actual_segment, expected_segment in zip(
        actual.segments, expected.segments, strict=True
    ):
        assert np.allclose(
            actual_segment.at_many(parameters).array,
            expected_segment.at_many(parameters).array,
            atol=1e-6,
        )


def test_json_svg_and_matplotlib_share_source_geometry() -> None:
    fixture = shared_fixture()
    assert_geometry_equal(loads(dumps(fixture)).path, fixture)
    assert_geometry_equal(
        from_svg_path_data(to_svg_path_data(fixture, precision=9)), fixture
    )
    assert_geometry_equal(from_path(to_path(fixture)), fixture)


def test_exporters_retain_native_cubics() -> None:
    fixture = shared_fixture()
    svg = to_svg_path_data(fixture)
    tikz = to_tikz(fixture)
    matplotlib_path = to_path(fixture)

    assert svg.count("C ") == len(fixture.segments)
    assert tikz.count(".. controls") == len(fixture.segments)
    assert np.count_nonzero(matplotlib_path.codes == Path.CURVE4) == 3 * len(
        fixture.segments
    )


@pytest.mark.skipif(shutil.which("pdflatex") is None, reason="pdflatex is not installed")
def test_tikz_fixture_compiles_when_tex_is_available(tmp_path) -> None:
    source = tmp_path / "fixture.tex"
    source.write_text(
        "\\documentclass{standalone}\n"
        "\\usepackage{tikz}\n"
        "\\begin{document}\n"
        "\\begin{tikzpicture}\n"
        f"{to_tikz(shared_fixture())}\n"
        "\\end{tikzpicture}\n"
        "\\end{document}\n"
    )
    result = subprocess.run(
        ["pdflatex", "-halt-on-error", "-interaction=batchmode", source.name],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
