import json

import pytest

from bezierkit import CubicBezierSegment, PiecewiseBezier, Point
from bezierkit.export.json import PathDocument, dumps, loads


def compound_path() -> PiecewiseBezier:
    closed = PiecewiseBezier(
        [
            CubicBezierSegment.from_line(Point(0, 0), Point(2, 0)),
            CubicBezierSegment.from_line(Point(2, 0), Point(0, 0)),
        ],
        closed=True,
    )
    open_path = PiecewiseBezier(
        [CubicBezierSegment.from_line(Point(3, 1), Point(4, 2))]
    )
    return PiecewiseBezier.compound([closed, open_path])


def test_json_round_trip_preserves_controls_subpaths_closure_and_metadata() -> None:
    path = compound_path()
    encoded = dumps(path, metadata={"name": "fixture", "weight": 2})
    payload = json.loads(encoded)

    assert payload["schema"] == "bezierkit.path"
    assert payload["version"] == 1
    assert payload["dimension"] == 2
    assert payload["subpaths"][0]["closed"] is True
    assert payload["subpaths"][1]["closed"] is False

    decoded = loads(encoded)
    assert decoded == PathDocument(path=path, metadata={"name": "fixture", "weight": 2})


def test_json_is_deterministic_and_rejects_non_finite_values() -> None:
    path = compound_path()
    assert dumps(path, metadata={"b": 2, "a": 1}) == dumps(
        path, metadata={"a": 1, "b": 2}
    )
    payload = json.loads(dumps(path))
    payload["subpaths"][0]["segments"][0][0][0] = float("nan")
    with pytest.raises(ValueError, match="finite"):
        loads(json.dumps(payload))


def test_json_rejects_unknown_schema_versions() -> None:
    payload = json.loads(dumps(compound_path()))
    payload["version"] = 999
    with pytest.raises(ValueError, match="version"):
        loads(json.dumps(payload))
