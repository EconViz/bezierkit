import json

from typer.testing import CliRunner

from bezierkit.cli.commands.construct import app as construct_app
from bezierkit.cli.commands.evaluate import app as evaluate_app
from bezierkit.cli.commands.sample import app as sample_app

runner = CliRunner()


def test_construct_slopes_emits_control_points() -> None:
    result = runner.invoke(
        construct_app,
        ["slopes", "--start", "0,5", "--end", "5,0", "--start-slope", "-2", "--end-slope", "-0.3"],
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["control_points"][0] == [0.0, 5.0]
    assert payload["control_points"][-1] == [5.0, 0.0]
    assert len(payload["control_points"]) == 4


def test_construct_tangent_handle_changes_first_control_point() -> None:
    base = [
        "tangents",
        "--start",
        "0,0",
        "--end",
        "5,3",
        "--start-direction",
        "1,0",
        "--end-direction",
        "0,1",
    ]
    one = json.loads(runner.invoke(construct_app, [*base, "--start-handle", "1"]).stdout)
    two = json.loads(runner.invoke(construct_app, [*base, "--start-handle", "2"]).stdout)
    assert two["control_points"][1][0] == 2 * one["control_points"][1][0]


def test_construct_output_pipes_to_sample_and_evaluate() -> None:
    constructed = runner.invoke(
        construct_app,
        ["slopes", "--start", "0,5", "--end", "5,0", "--start-slope", "-2", "--end-slope", "-0.3"],
    )
    sampled = runner.invoke(
        sample_app,
        ["--count", "3", "--format", "json"],
        input=constructed.stdout,
    )
    evaluated = runner.invoke(evaluate_app, ["--t", "0.5", "--json"], input=constructed.stdout)
    assert sampled.exit_code == 0
    assert evaluated.exit_code == 0
    assert len(json.loads(sampled.stdout)) == 3
    assert json.loads(evaluated.stdout)[0]["t"] == 0.5
