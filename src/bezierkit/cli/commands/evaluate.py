from __future__ import annotations

import typer

from bezierkit import BezierCurve
from bezierkit.cli.formatting import render_json, render_table
from bezierkit.cli.parsing import parse_point, parse_t_values

app = typer.Typer(help="Evaluate a Bézier curve or one of its derivatives.")


@app.callback(invoke_without_command=True)
def evaluate(
    points: list[str] = typer.Option(..., "--points", help="Control point, e.g. '0,0'."),
    t: list[str] = typer.Option(..., "--t", help="Value or inclusive start:stop:step."),
    order: int = typer.Option(0, "--order", help="Derivative order; zero evaluates B(t)."),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON."),
) -> None:
    """Evaluate a curve at one or more parameter values."""
    curve = BezierCurve([parse_point(raw) for raw in points])
    if order:
        curve = curve.derivative(order)
    rows = [
        {"t": value, "value": list(curve.at(value).coords)}
        for value in parse_t_values(t)
    ]
    typer.echo(render_json(rows) if as_json else render_table(rows))
