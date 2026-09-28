import subprocess
import sys

from typer.testing import CliRunner

from bezierkit.cli.app import app

runner = CliRunner()


def test_root_help_lists_public_commands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert all(command in result.stdout for command in ["evaluate", "sample", "construct"])


def test_module_cli_error_is_clean_without_external_click() -> None:
    script = """
import sys

class BlockExternalClick:
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'click' or fullname.startswith('click.'):
            raise ModuleNotFoundError('external click blocked')
        return None

sys.meta_path.insert(0, BlockExternalClick())
from bezierkit.cli.app import main
sys.argv = ['bezierkit', 'evaluate', '--points', 'bad', '--points', '1,1', '--t', '0.5']
main()
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "Error: invalid point" in result.stderr
    assert "Traceback" not in result.stderr


def test_framework_usage_error_is_preserved() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "bezierkit.cli",
            "evaluate",
            "--points",
            "0,0",
            "--points",
            "1,1",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "Missing option" in result.stderr
    assert "unexpected failure" not in result.stderr


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
