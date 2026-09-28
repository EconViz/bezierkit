from __future__ import annotations

import sys
from typing import Annotated

import typer

from bezierkit.cli.commands.construct import app as construct_app
from bezierkit.cli.commands.evaluate import app as evaluate_app
from bezierkit.cli.commands.sample import app as sample_app
from bezierkit.core.errors import BezierKitError

app = typer.Typer(
    name="bezierkit",
    help="A small mathematical toolkit for Bézier curves.",
    no_args_is_help=True,
    add_completion=False,
)


@app.callback()
def root(
    debug: Annotated[
        bool, typer.Option("--debug", help="Show Python tracebacks for command failures.")
    ] = False,
) -> None:
    """Evaluate, sample, and construct Bézier curves."""


app.add_typer(evaluate_app, name="evaluate")
app.add_typer(sample_app, name="sample")
app.add_typer(construct_app, name="construct")


def main() -> None:
    try:
        app()
    except BezierKitError as exc:
        if "--debug" in sys.argv:
            raise
        typer.echo(f"Error: {exc}", err=True)
        raise SystemExit(1) from None
    except Exception:
        if "--debug" in sys.argv:
            raise
        typer.echo("Error: unexpected failure (run with --debug for traceback)", err=True)
        raise SystemExit(1) from None
