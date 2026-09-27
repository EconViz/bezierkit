from __future__ import annotations

import csv
import io
import json
from collections.abc import Sequence
from typing import Any

from rich.console import Console
from rich.table import Table

Rows = Sequence[dict[str, Any]]


def render_json(rows: Rows) -> str:
    return json.dumps(list(rows), ensure_ascii=False, separators=(",", ":"))


def render_csv(rows: Rows) -> str:
    if not rows:
        return ""
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().rstrip("\n")


def render_table(rows: Rows) -> str:
    if not rows:
        return ""
    table = Table(show_header=True)
    for heading in rows[0]:
        table.add_column(heading)
    for row in rows:
        table.add_row(*(str(row[heading]) for heading in rows[0]))
    console = Console(record=True, force_terminal=False, color_system=None, width=120)
    with console.capture() as capture:
        console.print(table)
    return capture.get().rstrip("\n")
