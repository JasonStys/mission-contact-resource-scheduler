"""Strict input, canonical provenance and finite control tests by Jason Stys.

Functions: test contracts for hostile/ambiguous JSON and bounded schema mutation.
Variables: temporary files, input dictionaries and rejected values; docs/CODE_INDEX.md.
"""

import json
from dataclasses import replace

import pytest

from scheduler.engine import Settings, build_import, build_run, fixture, run_id
from scheduler.model import MAX_BYTES, case_data, load_case, parse_case


@pytest.mark.parametrize(
    "key,value",
    [
        ("guard", True),
        ("guard", 1.0),
        ("guard", -1),
        ("policy", 2),
        ("energy_cap", 0),
        ("station_budget", 80),
        ("scenario", []),
        ("scenario", "unknown"),
    ],
)
def test_settings_reject(key, value):
    """Finite settings fail closed instead of coercing values or unreviewed scenarios."""
    with pytest.raises(ValueError):
        Settings(**{key: value})


@pytest.mark.parametrize(
    "collection,field,value",
    [
        ("requests", "id", "=FORMULA"),
        ("requests", "spacecraft", "OTHER"),
        ("requests", "band", "L"),
        ("requests", "priority", True),
        ("requests", "units", 0),
        ("requests", "release", -1),
        ("requests", "deadline", 0),
        ("options", "id", "<script>"),
        ("options", "request", "MISSING"),
        ("options", "station", "OTHER"),
        ("options", "start", 10.5),
        ("options", "end", 0),
        ("options", "energy", 0),
        ("options", "rate", 5),
    ],
)
def test_scalar_rejection(collection, field, value):
    """Every bounded request/option field has a negative schema fixture."""
    data = case_data(fixture(Settings()))
    data[collection][0][field] = value
    with pytest.raises(ValueError):
        parse_case(data)


@pytest.mark.parametrize(
    "kind",
    [
        "horizon",
        "bool-horizon",
        "empty",
        "duplicate-request",
        "duplicate-option",
        "too-many-options",
        "too-many-requests",
        "too-many-blackouts",
        "alternatives",
        "bad-budget",
        "bad-energy",
        "unknown-key",
        "missing-key",
        "not-list",
        "bad-blackout",
        "time-order",
    ],
)
def test_shape_and_cardinality(kind):
    """Limits bound exact search; malformed cases never get silently truncated or deduplicated."""
    data = case_data(fixture(Settings()))
    match kind:
        case "horizon":
            data["horizon"] = 121
        case "bool-horizon":
            data["horizon"] = True
        case "empty":
            data["requests"] = []
        case "duplicate-request":
            data["requests"][1]["id"] = "R01"
        case "duplicate-option":
            data["options"][1]["id"] = "A1"
        case "too-many-options":
            data["options"] *= 2
        case "too-many-requests":
            data["requests"] *= 2
        case "too-many-blackouts":
            data["blackouts"] = [{}] * 7
        case "alternatives":
            data["options"][2]["request"] = "R01"
        case "bad-budget":
            data["station_budgets"]["ALPHA"] = False
        case "bad-energy":
            data["energy_budgets"]["SC-A"] = 81
        case "unknown-key":
            data["unknown"] = 1
        case "missing-key":
            del data["requests"][0]["units"]
        case "not-list":
            data["options"] = {}
        case "bad-blackout":
            data["blackouts"] = [{"station": "ALPHA", "start": 10, "end": 10}]
        case "time-order":
            data["requests"][0]["release"] = 40
    with pytest.raises(ValueError):
        parse_case(data)


def test_programmatic_immutable_shape():
    """Dataclass callers cannot bypass tuple, record type or budget validation."""
    case = fixture(Settings())
    for changes in (
        {"options": []},
        {"requests": ("bad",)},
        {"station_budgets": (1, 2)},
        {"blackouts": ("bad",)},
    ):
        with pytest.raises(ValueError):
            replace(case, **changes)


@pytest.mark.parametrize(
    "raw",
    [
        b'{"x":1,"x":2}',
        b'{"x":{"y":1,"y":2}}',
        b'{"x":NaN}',
        b'{"x":Infinity}',
        b"\xff",
        b"[1",
        b"[" * 1500,
        b"a" * (MAX_BYTES + 1),
        b"null",
    ],
    ids=[
        "duplicate",
        "nested-duplicate",
        "nan",
        "infinity",
        "encoding",
        "syntax",
        "depth",
        "size",
        "null",
    ],
)
def test_hostile_json(tmp_path, raw):
    """Duplicate keys, constants, deep recursion, invalid encoding, size and shape are rejected."""
    path = tmp_path / "input.json"
    path.write_bytes(raw)
    with pytest.raises(ValueError):
        load_case(path)


def test_roundtrip_and_import_parameters(tmp_path):
    """Local input budgets survive import; unused fixture settings do not alter evidence hashes."""
    case = fixture(Settings(scenario="tight-energy"))
    path = tmp_path / "case.json"
    path.write_text(json.dumps(case_data(case)), encoding="utf-8")
    assert load_case(path) == case
    first = build_import(path, Settings())
    second = build_import(path, Settings(scenario="maintenance", energy_cap=40, station_budget=60))
    assert first == second and first["case"]["energy_budgets"]["SC-B"] == 8
    assert first["settings"] == {"guard": 1, "policy": 1}
    assert len(first["id"]) == 64 and first["id"] == run_id(first)
    assert build_run(Settings())["id"] != build_run(Settings(guard=2))["id"]


def test_no_alternatives_preserved():
    """A valid request with no candidate remains visible and unscheduled in full evidence."""
    case = fixture(Settings())
    data = case_data(replace(case, options=()))
    assert parse_case(data).options == ()
