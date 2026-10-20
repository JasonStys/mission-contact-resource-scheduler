"""Deterministic inert exports and explicit local SQL history by Jason Stys.

Functions: export_report, save_history. Variables: bounded case, plans, report rows,
SQLite parameter values. Exact locations: docs/CODE_INDEX.md.
No automatic persistence or public HTTP history/import endpoint.
"""

import csv
import html
import io
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

from scheduler.engine import canonical, run_id


def export_report(run: dict[str, Any], format_name: str) -> tuple[bytes, str]:
    """Export complete JSON/input, candidate CSV or escaped inert HTML; never execute data."""
    if format_name in ("json", "input"):
        data = run["case"] if format_name == "input" else run
        return json.dumps(
            data, indent=2, sort_keys=True, allow_nan=False
        ).encode() + b"\n", "application/json"
    if format_name == "csv":
        buffer = io.StringIO(newline="")
        writer = csv.writer(buffer, lineterminator="\n")
        fields = (
            "id",
            "request",
            "station",
            "spacecraft",
            "start",
            "end",
            "energy",
            "rate",
            "selected",
            "baseline",
        )
        writer.writerow((*fields, "reasons"))
        for item in run["candidates"]:
            writer.writerow((*(item[key] for key in fields), " | ".join(item["reasons"])))
        return buffer.getvalue().encode(), "text/csv"
    if format_name == "html":
        body = html.escape(json.dumps(run, indent=2, sort_keys=True, allow_nan=False))
        return (
            '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Scheduler evidence — Jason Stys</title><h1>Contact planning evidence</h1><p>By Jason Stys. Offline educational allocation, not operational planning.</p><p>Full input, exact and greedy plans, blockers, budgets and provenance follow.</p><pre>'
            + body
            + "</pre></html>"
        ).encode(), "text/html"
    raise ValueError("Unsupported report format")


def save_history(path: Path, run: dict[str, Any]) -> None:
    """Insert immutable content-addressed evidence, idempotently; refuse more than 100 runs."""
    if run.get("id") != run_id(run):
        raise ValueError("Evidence hash does not match its contents")
    schema = Path(__file__).with_name("resources") / "history.sql"
    with closing(sqlite3.connect(path, timeout=5)) as connection, connection:
        connection.executescript(schema.read_text(encoding="utf-8"))
        connection.execute("BEGIN IMMEDIATE")
        previous = connection.execute(
            "SELECT report_json FROM runs WHERE id = ?", (run["id"],)
        ).fetchone()
        encoded = canonical(run).decode()
        if previous:
            if previous[0] != encoded:
                raise ValueError("History identifier collision")
            return
        if connection.execute("SELECT count(*) FROM runs").fetchone()[0] >= 100:
            raise ValueError("History is full; choose a new explicit local database")
        connection.execute(
            "INSERT INTO runs(id, scenario, report_json) VALUES(?, ?, ?)",
            (run["id"], run["scenario"], encoded),
        )
