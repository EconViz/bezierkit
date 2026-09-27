from typer.testing import CliRunner

from bezierkit.cli.app import app

runner = CliRunner()


def test_root_help_lists_public_commands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert all(command in result.stdout for command in ["evaluate", "sample", "construct"])


def test_domain_error_is_readable_without_traceback() -> None:
    result = runner.invoke(
        app,
        ["evaluate", "--points", "bad", "--points", "1,1", "--t", "0.5"],
    )
    assert result.exit_code == 1
    assert "Error: invalid point" in result.stderr
    assert "Traceback" not in result.stderr


def test_root_evaluate_and_construct_command_shapes() -> None:
    evaluated = runner.invoke(
        app,
        ["evaluate", "--points", "0,0", "--points", "2,2", "--t", "0.5", "--json"],
    )
    constructed = runner.invoke(app, ["construct", "--help"])
    assert evaluated.exit_code == 0
    assert '"value":[1.0,1.0]' in evaluated.stdout
    assert constructed.exit_code == 0
    assert "slopes" in constructed.stdout and "tangents" in constructed.stdout
