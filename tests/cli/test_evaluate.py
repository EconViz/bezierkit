import json

from typer.testing import CliRunner

from bezierkit.cli.commands.evaluate import app

runner = CliRunner()


def test_evaluate_line_at_midpoint() -> None:
    result = runner.invoke(
        app,
        ["--points", "0,0", "--points", "4,0", "--t", "0.5"],
    )
    assert result.exit_code == 0
    assert "2.0" in result.stdout


def test_evaluate_derivative_as_json() -> None:
    result = runner.invoke(
        app,
        [
            "--points",
            "0,0",
            "--points",
            "4,2",
            "--t",
            "0",
            "--t",
            "1",
            "--order",
            "1",
            "--json",
        ],
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout) == [
        {"t": 0.0, "value": [4.0, 2.0]},
        {"t": 1.0, "value": [4.0, 2.0]},
    ]


def test_evaluate_invalid_point_exits_nonzero() -> None:
    result = runner.invoke(app, ["--points", "bad", "--points", "1,1", "--t", "0.5"])
    assert result.exit_code == 1
