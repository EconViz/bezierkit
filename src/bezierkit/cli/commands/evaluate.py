from __future__ import annotations

from typing import Annotated

import typer

from bezierkit import BezierCurve
from bezierkit.cli.formatting import render_json, render_table
from bezierkit.cli.parsing import parse_t_values, resolve_control_points

app = typer.Typer(help="Evaluate a Bézier curve or one of its derivatives.")


@app.callback(invoke_without_command=True)
def evaluate(
    t: Annotated[
        list[str], typer.Option("--t", help="Value or inclusive start:stop:step.")
    ],
    points: Annotated[
        list[str] | None,
        typer.Option("--points", help="Control point; omit to read construct JSON from stdin."),
    ] = None,
    order: Annotated[
        int, typer.Option("--order", help="Derivative order; zero evaluates B(t).")
    ] = 0,
    as_json: Annotated[bool, typer.Option("--json", help="Emit JSON.")] = False,
) -> None:
    """Evaluate a curve at one or more parameter values."""
    curve = BezierCurve(resolve_control_points(points))
    if order:
        curve = curve.derivative(order)
    rows = [
        {"t": value, "value": list(curve.at(value).coords)}
        for value in parse_t_values(t)
    ]
    typer.echo(render_json(rows) if as_json else render_table(rows))
