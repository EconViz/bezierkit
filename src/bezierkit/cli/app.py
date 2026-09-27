from __future__ import annotations

from typing import Annotated, Any

import click
import typer
from typer.core import TyperGroup

from bezierkit.cli.commands.construct import app as construct_app
from bezierkit.cli.commands.evaluate import app as evaluate_app
from bezierkit.cli.commands.sample import app as sample_app
from bezierkit.core.errors import BezierKitError


class BezierKitGroup(TyperGroup):
    """Root command group with consistent user-facing error handling."""

    def invoke(self, ctx: click.Context) -> Any:
        try:
            return super().invoke(ctx)
        except (click.ClickException, click.Abort, click.exceptions.Exit, typer.Exit):
            raise
        except BezierKitError as exc:
            if ctx.params.get("debug", False):
                raise
            typer.echo(f"Error: {exc}", err=True)
            raise click.exceptions.Exit(1) from None
        except Exception:
            if ctx.params.get("debug", False):
                raise
            typer.echo("Error: unexpected failure (run with --debug for traceback)", err=True)
            raise click.exceptions.Exit(1) from None


app = typer.Typer(
    name="bezierkit",
    help="A small mathematical toolkit for Bézier curves.",
    cls=BezierKitGroup,
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
    app()
