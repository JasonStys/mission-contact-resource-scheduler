"""Strict finite planning inputs by Jason Stys.

Classes: Request, Option, Blackout, Case. Functions validate integers, schemas and JSON.
Variables: station/spacecraft allowlists, resource budgets, fixed logical horizon.
Exact definitions, fields and parameters: docs/CODE_INDEX.md.
"""

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

STATIONS = ("ALPHA", "BRAVO", "CHARLIE")
SPACECRAFT = ("SC-A", "SC-B", "SC-C")
BANDS = {"ALPHA": ("S", "X"), "BRAVO": ("X",), "CHARLIE": ("S",)}
HORIZON = 120
MAX_BYTES = 65_536


def integer(value: Any, minimum: int, maximum: int) -> bool:
    """Accept actual bounded integers, not booleans, floats or numeric strings."""
    return type(value) is int and minimum <= value <= maximum


def identifier(value: Any) -> bool:
    """Allow CSV/HTML-safe bounded labels, never expressions or free-form imported text."""
    return isinstance(value, str) and re.fullmatch(r"[A-Z][A-Z0-9-]{0,15}", value) is not None


@dataclass(frozen=True, slots=True)
class Request:
    """Optional all-or-nothing delivery; units/priority define utility, not mission importance."""

    id: str
    spacecraft: str
    band: str
    priority: int
    units: int
    release: int
    deadline: int


@dataclass(frozen=True, slots=True)
class Option:
    """Fixed alternative window; rate is capacity per tick, energy a synthetic budget charge."""

    id: str
    request: str
    station: str
    start: int
    end: int
    energy: int
    rate: int


@dataclass(frozen=True, slots=True)
class Blackout:
    """Station unavailability over a half-open interval, including reserved guard occupancy."""

    station: str
    start: int
    end: int


@dataclass(frozen=True, slots=True)
class Case:
    """Immutable bounded case; budgets follow the fixed station and spacecraft tuple order."""

    horizon: int
    requests: tuple[Request, ...]
    options: tuple[Option, ...]
    blackouts: tuple[Blackout, ...]
    station_budgets: tuple[int, ...]
    energy_budgets: tuple[int, ...]

    def __post_init__(self) -> None:
        """Enforce shape, references, cardinalities and ranges even for programmatic callers."""
        if type(self.horizon) is not int or self.horizon != HORIZON:
            raise ValueError("Horizon must be 120 logical ticks")
        for values, maximum, item_type in (
            (self.requests, 9, Request),
            (self.options, 18, Option),
            (self.blackouts, 6, Blackout),
        ):
            if (
                type(values) is not tuple
                or len(values) > maximum
                or any(type(item) is not item_type for item in values)
            ):
                raise ValueError("Invalid bounded case collection")
        if not self.requests:
            raise ValueError("At least one request is required")
        for budgets in (self.station_budgets, self.energy_budgets):
            if (
                type(budgets) is not tuple
                or len(budgets) != 3
                or not all(integer(value, 1, 80) for value in budgets)
            ):
                raise ValueError("Three integer resource budgets in 1..80 are required")
        request_ids = [request.id for request in self.requests]
        option_ids = [option.id for option in self.options]
        if not all(identifier(value) for value in request_ids + option_ids):
            raise ValueError("Invalid identifier")
        if len(set(request_ids)) != len(request_ids) or len(set(option_ids)) != len(option_ids):
            raise ValueError("Duplicate identifier")
        for request in self.requests:
            if (
                request.spacecraft not in SPACECRAFT
                or request.band not in ("S", "X")
                or not integer(request.priority, 1, 20)
                or not integer(request.units, 1, 40)
                or not integer(request.release, 0, 119)
                or not integer(request.deadline, 1, 120)
                or request.release >= request.deadline
            ):
                raise ValueError("Invalid request")
        for option in self.options:
            if (
                option.request not in request_ids
                or option.station not in STATIONS
                or not integer(option.start, 0, 119)
                or not integer(option.end, 1, 120)
                or option.start >= option.end
                or not integer(option.energy, 1, 40)
                or not integer(option.rate, 1, 4)
            ):
                raise ValueError("Invalid candidate window")
        if any(sum(option.request == rid for option in self.options) > 2 for rid in request_ids):
            raise ValueError("At most two alternatives per request")
        for blackout in self.blackouts:
            if (
                blackout.station not in STATIONS
                or not integer(blackout.start, 0, 119)
                or not integer(blackout.end, 1, 120)
                or blackout.start >= blackout.end
            ):
                raise ValueError("Invalid blackout")


def case_data(case: Case) -> dict[str, Any]:
    """Serialize the complete input, including explicit named resource budgets."""
    return {
        "horizon": case.horizon,
        "requests": [asdict(item) for item in case.requests],
        "options": [asdict(item) for item in case.options],
        "blackouts": [asdict(item) for item in case.blackouts],
        "station_budgets": dict(zip(STATIONS, case.station_budgets, strict=True)),
        "energy_budgets": dict(zip(SPACECRAFT, case.energy_budgets, strict=True)),
    }


def exact_object(value: Any, keys: set[str]) -> dict[str, Any]:
    """Reject unknown/missing fields; no silently discarded imported information."""
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError("Unexpected JSON object fields")
    return value


def parse_case(value: Any) -> Case:
    """Parse a strict JSON object; Case validates every scalar and resource reference."""
    obj = exact_object(
        value, {"horizon", "requests", "options", "blackouts", "station_budgets", "energy_budgets"}
    )
    collections: dict[str, list[dict[str, Any]]] = {}
    for key, cls, limit in (
        ("requests", Request, 9),
        ("options", Option, 18),
        ("blackouts", Blackout, 6),
    ):
        items = obj[key]
        if not isinstance(items, list) or len(items) > limit:
            raise ValueError("Invalid JSON array")
        collections[key] = [exact_object(item, set(cls.__dataclass_fields__)) for item in items]
    station = exact_object(obj["station_budgets"], set(STATIONS))
    energy = exact_object(obj["energy_budgets"], set(SPACECRAFT))
    return Case(
        obj["horizon"],
        tuple(Request(**item) for item in collections["requests"]),
        tuple(Option(**item) for item in collections["options"]),
        tuple(Blackout(**item) for item in collections["blackouts"]),
        tuple(station[name] for name in STATIONS),
        tuple(energy[name] for name in SPACECRAFT),
    )


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject duplicate JSON keys at every depth instead of accepting last-wins ambiguity."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    """Refuse JSON NaN/Infinity extensions."""
    raise ValueError("Non-finite JSON constant")


def load_case(path: Path) -> Case:
    """Read at most 64 KiB from an explicit local file; never fetch remote data."""
    with path.open("rb") as source:
        raw = source.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("Case exceeds 64 KiB")
    try:
        return parse_case(
            json.loads(raw, object_pairs_hook=unique_object, parse_constant=reject_constant)
        )
    except (RecursionError, UnicodeError, TypeError) as error:
        raise ValueError("Invalid JSON planning case") from error
