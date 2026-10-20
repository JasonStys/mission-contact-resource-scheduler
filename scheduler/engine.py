"""Reviewed synthetic scenarios and canonical experiment evidence by Jason Stys.

Settings exposes finite guard/budget/objective parameters. Functions build fixtures,
evaluate exact and baseline plans, import local JSON and expose a public catalog.
Variable locations: docs/CODE_INDEX.md. No live mission inputs or commands.
"""

import hashlib
import json
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any

from scheduler.model import (
    SPACECRAFT,
    STATIONS,
    Blackout,
    Case,
    Option,
    Request,
    case_data,
    load_case,
)
from scheduler.solver import blockers, solve

CHOICES = {
    "guard": (0, 1, 2),
    "energy_cap": (12, 24, 40),
    "station_budget": (24, 36, 60),
    "policy": (0, 1),
}
SCENARIOS = {
    "nominal": "Shared ground network",
    "station-outage": "BRAVO unavailable",
    "maintenance": "Two maintenance blocks",
    "tight-energy": "SC-B energy constrained",
    "urgent-insertion": "Late high-value request",
    "impossible-deadline": "A request cannot fit its deadline",
    "greedy-trap": "One long contact or two short contacts",
    "unreachable-window": "All stations unavailable",
}


@dataclass(frozen=True, slots=True)
class Settings:
    """Finite configuration; imported cases retain their own budgets and ignore fixture selectors."""

    scenario: str = "nominal"
    guard: int = 1
    energy_cap: int = 24
    station_budget: int = 36
    policy: int = 1

    def __post_init__(self) -> None:
        """Reject unreviewed variants, bools and parameters outside the published finite grid."""
        if not isinstance(self.scenario, str) or self.scenario not in SCENARIOS:
            raise ValueError("Unknown scenario")
        for key, values in CHOICES.items():
            value = getattr(self, key)
            if type(value) is not int or value not in values:
                raise ValueError("Unsupported setting")


def fixture(settings: Settings) -> Case:
    """Construct invented fixed windows and optional scenario perturbations, never ephemerides."""
    requests = tuple(
        Request(*values)
        for values in (
            ("R01", "SC-A", "X", 10, 10, 0, 36),
            ("R02", "SC-B", "X", 10, 6, 0, 24),
            ("R03", "SC-C", "X", 10, 6, 18, 40),
            ("R04", "SC-A", "S", 6, 8, 36, 70),
            ("R05", "SC-B", "S", 7, 12, 42, 88),
            ("R06", "SC-C", "X", 5, 8, 50, 92),
            ("R07", "SC-A", "X", 8, 10, 76, 112),
            ("R08", "SC-B", "S", 4, 8, 84, 118),
        )
    )
    options = tuple(
        Option(*values)
        for values in (
            ("A1", "R01", "ALPHA", 10, 30, 10, 1),
            ("A2", "R01", "BRAVO", 12, 32, 12, 1),
            ("B1", "R02", "ALPHA", 10, 18, 4, 1),
            ("B2", "R02", "BRAVO", 8, 16, 5, 1),
            ("C1", "R03", "ALPHA", 22, 30, 4, 1),
            ("C2", "R03", "BRAVO", 24, 32, 5, 1),
            ("D1", "R04", "CHARLIE", 40, 52, 7, 1),
            ("D2", "R04", "ALPHA", 38, 50, 8, 1),
            ("E1", "R05", "CHARLIE", 58, 74, 10, 1),
            ("E2", "R05", "ALPHA", 56, 72, 10, 1),
            ("F1", "R06", "BRAVO", 62, 74, 6, 1),
            ("F2", "R06", "ALPHA", 74, 86, 6, 1),
            ("G1", "R07", "BRAVO", 90, 104, 8, 1),
            ("G2", "R07", "ALPHA", 88, 102, 8, 1),
            ("H1", "R08", "CHARLIE", 94, 106, 6, 1),
            ("H2", "R08", "ALPHA", 100, 112, 6, 1),
        )
    )
    blackouts: tuple[Blackout, ...] = ()
    energy = (settings.energy_cap,) * 3
    match settings.scenario:
        case "station-outage":
            blackouts = (Blackout("BRAVO", 0, 120),)
        case "maintenance":
            blackouts = (Blackout("ALPHA", 18, 42), Blackout("CHARLIE", 56, 78))
        case "tight-energy":
            energy = (settings.energy_cap, 8, settings.energy_cap)
        case "urgent-insertion":
            requests += (Request("R09", "SC-C", "X", 12, 10, 48, 68),)
            options += (
                Option("I1", "R09", "BRAVO", 50, 62, 8, 1),
                Option("I2", "R09", "ALPHA", 52, 64, 8, 1),
            )
        case "impossible-deadline":
            requests = tuple(
                replace(item, deadline=85) if item.id == "R08" else item for item in requests
            )
        case "greedy-trap":
            requests = requests[:3]
            options = tuple(item for item in options if item.id in ("A1", "B1", "C1"))
        case "unreachable-window":
            blackouts = tuple(Blackout(name, 0, 120) for name in STATIONS)
    return Case(120, requests, options, blackouts, (settings.station_budget,) * 3, energy)


def canonical(data: dict[str, Any]) -> bytes:
    """Stable UTF-8 JSON for reproducible evidence identifiers and immutable history."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def run_id(data: dict[str, Any]) -> str:
    """Hash all evidence except its self-referential identifier."""
    return hashlib.sha256(
        canonical({key: item for key, item in data.items() if key != "id"})
    ).hexdigest()


def evaluate(case: Case, settings: Settings, source: str) -> dict[str, Any]:
    """Compute plans, inspect final obstacles, budgets and provenance, then content-address output."""
    exact, greedy = solve(case, settings.guard, settings.policy)
    chosen = tuple(item for item in case.options if item.id in exact["selected"])
    requests = {request.id: request for request in case.requests}
    candidates = []
    for item in sorted(case.options, key=lambda item: item.id):
        candidates.append(
            {
                **asdict(item),
                "spacecraft": requests[item.request].spacecraft,
                "selected": item.id in exact["selected"],
                "baseline": item.id in greedy["selected"],
                "reasons": []
                if item.id in exact["selected"]
                else blockers(case, item, chosen, settings.guard),
            }
        )
    configuration = (
        {"guard": settings.guard, "policy": settings.policy}
        if source == "local-json"
        else asdict(settings)
    )
    result: dict[str, Any] = {
        "version": "1.0.0",
        "scenario": source,
        "settings": configuration,
        "case": case_data(case),
        "exact": exact,
        "greedy": greedy,
        "delta": exact["utility"] - greedy["utility"],
        "candidates": candidates,
        "requests": [
            {
                **asdict(request),
                "selected": next((item.id for item in chosen if item.request == request.id), None),
                "alternatives": [item.id for item in case.options if item.request == request.id],
            }
            for request in sorted(case.requests, key=lambda item: item.id)
        ],
        "station_usage": [
            {
                "name": name,
                "used": sum(
                    item.end - item.start + 2 * settings.guard
                    for item in chosen
                    if item.station == name
                ),
                "budget": case.station_budgets[index],
            }
            for index, name in enumerate(STATIONS)
        ],
        "energy_usage": [
            {
                "name": name,
                "used": sum(
                    item.energy for item in chosen if requests[item.request].spacecraft == name
                ),
                "budget": case.energy_budgets[index],
            }
            for index, name in enumerate(SPACECRAFT)
        ],
        "provenance": {
            "author": "Jason Stys",
            "clock": "logical ticks",
            "source": "synthetic fixture" if source != "local-json" else "explicit local JSON",
            "scope": "Offline finite-candidate educational allocation; no operational assurance",
            "units": "invented data and energy units",
            "external_connections": False,
        },
    }
    result["id"] = run_id(result)
    return result


def build_run(settings: Settings) -> dict[str, Any]:
    """Evaluate a reviewed synthetic scenario without filesystem or network I/O."""
    return evaluate(fixture(settings), settings, settings.scenario)


def build_import(path: Path, settings: Settings) -> dict[str, Any]:
    """CLI-only import; guard/policy apply, imported budgets remain authoritative."""
    return evaluate(load_case(path), settings, "local-json")


def catalog() -> dict[str, Any]:
    """Expose finite scenario names, controls and defaults to the browser."""
    return {
        "scenarios": SCENARIOS,
        "choices": CHOICES,
        "defaults": asdict(Settings()),
        "stations": STATIONS,
        "spacecraft": SPACECRAFT,
    }
