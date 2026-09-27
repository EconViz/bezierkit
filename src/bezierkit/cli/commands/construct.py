from __future__ import annotations

import json
from typing import Annotated

import typer

from bezierkit import BezierCurve
from bezierkit.cli.parsing import parse_point, parse_vector
from bezierkit.construction import PlanarSlopes, TangentDirections

app = typer.Typer(help="Construct cubic Bézier control points from endpoint constraints.")


def _emit(curve: BezierCurve) -> None:
    payload = {"control_points": [list(point.coords) for point in curve.control_points]}
    typer.echo(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))


@app.command()
def slopes(
    start: Annotated[str, typer.Option("--start")],
    end: Annotated[str, typer.Option("--end")],
    start_slope: Annotated[float, typer.Option("--start-slope")],
    end_slope: Annotated[float, typer.Option("--end-slope")],
    start_handle: Annotated[float, typer.Option("--start-handle")] = 1.0,
    end_handle: Annotated[float, typer.Option("--end-handle")] = 1.0,
) -> None:
    """Construct a planar cubic from endpoint slopes."""
    curve = PlanarSlopes(
        start=parse_point(start),
        end=parse_point(end),
        start_slope=start_slope,
        end_slope=end_slope,
        start_handle=start_handle,
        end_handle=end_handle,
    ).build()
    _emit(curve)


@app.command()
def tangents(
    start: Annotated[str, typer.Option("--start")],
    end: Annotated[str, typer.Option("--end")],
    start_direction: Annotated[str, typer.Option("--start-direction")],
    end_direction: Annotated[str, typer.Option("--end-direction")],
    start_handle: Annotated[float, typer.Option("--start-handle")] = 1.0,
    end_handle: Annotated[float, typer.Option("--end-handle")] = 1.0,
) -> None:
    """Construct an n-dimensional cubic from tangent directions."""
    curve = TangentDirections(
        start=parse_point(start),
        end=parse_point(end),
        start_direction=parse_vector(start_direction),
        end_direction=parse_vector(end_direction),
        start_handle=start_handle,
        end_handle=end_handle,
    ).build()
    _emit(curve)
