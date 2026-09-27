import json
import subprocess
import sys
from pathlib import Path

from typer.testing import CliRunner

from bezierkit.cli.commands.sample import app

runner = CliRunner()


def test_sample_csv_has_header_and_requested_rows() -> None:
    result = runner.invoke(
        app,
        ["--points", "0,0", "--points", "2,2", "--count", "3", "--format", "csv"],
    )
    assert result.exit_code == 0
    assert result.stdout.splitlines() == ["t,x,y", "0.0,0.0,0.0", "0.5,1.0,1.0", "1.0,2.0,2.0"]


def test_sample_json_and_output_file(tmp_path: Path) -> None:
    output = tmp_path / "sample.json"
    result = runner.invoke(
        app,
        [
            "--points",
            "0,0",
            "--points",
            "2,2",
            "--count",
            "2",
            "--format",
            "json",
            "--output",
            str(output),
        ],
    )
    assert result.exit_code == 0
    assert result.stdout == ""
    assert json.loads(output.read_text()) == [
        {"t": 0.0, "x": 0.0, "y": 0.0},
        {"t": 1.0, "x": 2.0, "y": 2.0},
    ]


def test_sample_rejects_unknown_format() -> None:
    result = runner.invoke(
        app,
        ["--points", "0,0", "--points", "1,1", "--format", "yaml"],
    )
    assert result.exit_code == 1


def test_module_cli_rejects_non_finite_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "bezierkit.cli",
            "sample",
            "--points",
            "nan,0",
            "--points",
            "1,1",
            "--count",
            "2",
            "--format",
            "json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "NaN" not in result.stdout
