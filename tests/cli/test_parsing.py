import json

import pytest

from bezierkit.cli.formatting import render_csv, render_json, render_table
from bezierkit.cli.parsing import parse_point, parse_t_values, parse_vector
from bezierkit.core.errors import BezierKitError
from bezierkit.core.geometry.point import Point
from bezierkit.core.geometry.vector import Vector


def test_parse_point_and_vector() -> None:
    assert parse_point("1, 2.5") == Point(1, 2.5)
    assert parse_vector("3,-4") == Vector(3, -4)


@pytest.mark.parametrize("raw", ["", "abc", "1,"])
def test_parse_point_wraps_invalid_input(raw: str) -> None:
    with pytest.raises(BezierKitError, match="invalid point"):
        parse_point(raw)


def test_parse_t_values_supports_values_and_inclusive_ranges() -> None:
    assert parse_t_values(["0.2", "0.8"]) == [0.2, 0.8]
    assert parse_t_values(["0:1:0.5"]) == [0, 0.5, 1]
    assert parse_t_values(["1:0:-0.5"]) == [1, 0.5, 0]


@pytest.mark.parametrize("raw", [["0:1:0"], ["0:1"], ["bad"]])
def test_parse_t_values_wraps_invalid_ranges(raw: list[str]) -> None:
    with pytest.raises(BezierKitError, match="invalid parameter"):
        parse_t_values(raw)


def test_renderers_produce_machine_readable_formats() -> None:
    rows = [{"t": 0.0, "x": 1.0}, {"t": 1.0, "x": 2.0}]
    assert json.loads(render_json(rows)) == rows
    assert render_csv(rows).splitlines() == ["t,x", "0.0,1.0", "1.0,2.0"]
    table = render_table(rows)
    assert "t" in table and "x" in table and "2.0" in table
