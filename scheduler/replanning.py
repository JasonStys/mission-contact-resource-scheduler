"""Station-loss contingency comparisons by Jason Stys.

Function: station_outages. Variables: original immutable case, full-horizon outage and plan deltas.
Uses the existing exact solver; never dispatches contacts. Definition lines: docs/CODE_INDEX.md.
"""

from dataclasses import replace
from typing import Any

from scheduler.model import STATIONS, Case
from scheduler.solver import solve


def station_outages(
    case: Case, guard: int, policy: int, baseline: dict[str, Any]
) -> list[dict[str, Any]]:
    """Reoptimize each single-station full-window loss, preserving budgets and other blackouts.

    Remove all candidate options at the lost station, equivalent to a full-horizon blackout.
    This preserves even six-block imported cases without expanding their input cap. This
    maximizes the existing utility objective, not minimum plan changes.
    Changes can therefore include contacts away from the failed station due to shared budgets.
    """
    comparisons = []
    before = set(baseline["selected"])
    for station in STATIONS:
        disrupted = replace(
            case,
            options=tuple(option for option in case.options if option.station != station),
        )
        exact, greedy = solve(disrupted, guard, policy)
        after = set(exact["selected"])
        comparisons.append(
            {
                "station": station,
                "outage": {"start": 0, "end": case.horizon},
                "exact": exact,
                "greedy": greedy,
                "retained": sorted(before & after),
                "removed": sorted(before - after),
                "added": sorted(after - before),
                "utility_loss": baseline["utility"] - exact["utility"],
                "fulfilled_delta": exact["fulfilled"] - baseline["fulfilled"],
                "energy_delta": exact["energy"] - baseline["energy"],
                "directly_blocked": [
                    {"id": option.id, "reasons": ["station-blackout"]}
                    for option in sorted(case.options, key=lambda item: item.id)
                    if option.id in before and option.station == station
                ],
                "request_changes": [
                    {
                        "request": request.id,
                        "before": next(
                            (
                                o.id
                                for o in case.options
                                if o.request == request.id and o.id in before
                            ),
                            None,
                        ),
                        "after": next(
                            (
                                o.id
                                for o in case.options
                                if o.request == request.id and o.id in after
                            ),
                            None,
                        ),
                    }
                    for request in sorted(case.requests, key=lambda item: item.id)
                    if {o.id for o in case.options if o.request == request.id and o.id in before}
                    != {o.id for o in case.options if o.request == request.id and o.id in after}
                ],
            }
        )
    return comparisons
