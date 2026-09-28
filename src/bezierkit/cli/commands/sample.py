from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from bezierkit import BezierCurve, BezierKitError
from bezierkit.cli.formatting import render_csv, render_json, render_table
from bezierkit.cli.parsing import resolve_control_points
from bezierkit.sampling import Sample, UniformSampler

app = typer.Typer(help="Uniformly sample a Bézier curve.")


def _rows(result: Sample) -> list[dict[str, float]]:
    labels = ["x", "y", "z"]
    rows: list[dict[str, float]] = []
    for t, point in result:
        row = {"t": float(t)}
        for index, coordinate in enumerate(point.coords):
            name = labels[index] if index < len(labels) else f"c{index}"
            row[name] = float(coordinate)
        rows.append(row)
    return rows


@app.callback(invoke_without_command=True)
def sample(
    points: Annotated[
        list[str] | None,
        typer.Option("--points", help="Control point; omit to read construct JSON from stdin."),
    ] = None,
    count: Annotated[
        int, typer.Option("--count", help="Number of samples, including endpoints.")
    ] = 50,
    output_format: Annotated[str, typer.Option("--format", help="table, csv, or json.")] = "table",
    output: Annotated[
        Path | None, typer.Option("--output", help="Write output to this path.")
    ] = None,
) -> None:
    """Sample a curve at uniformly spaced parameter values."""
    curve = BezierCurve(resolve_control_points(points))
    rows = _rows(UniformSampler(count).sample(curve))
    renderers = {"table": render_table, "csv": render_csv, "json": render_json}
    try:
        text = renderers[output_format](rows)
    except KeyError as exc:
        raise BezierKitError(
            f"unsupported output format '{output_format}'; choose table, csv, or json"
        ) from exc
    if output is None:
        typer.echo(text)
    else:
        output.write_text(text, encoding="utf-8")
