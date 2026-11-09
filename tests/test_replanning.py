"""Independent contingency oracles by Jason Stys.

Functions: test_*; variables: station outages, exhaustive subset ranks and immutable base cases.
The existing exhaustive oracle never calls production constraints. Lines: docs/CODE_INDEX.md.
"""

from dataclasses import replace

import pytest
from test_solver import oracle

from scheduler.engine import Settings, build_run, fixture, run_id
from scheduler.model import STATIONS, Blackout
from scheduler.replanning import station_outages
from scheduler.solver import solve


@pytest.mark.parametrize(
    "scenario", ["nominal", "greedy-trap", "unreachable-window", "maintenance"]
)
@pytest.mark.parametrize("guard,policy", [(0, 0), (1, 1), (2, 1)])
def test_outage_optimum_matches_independent_subset_oracle(scenario, guard, policy):
    """Check all objective ties as well as retained/removed/added partition and immutability."""
    settings = Settings(scenario=scenario, guard=guard, policy=policy)
    case = fixture(settings)
    before = repr(case)
    baseline, _ = solve(case, guard, policy)
    for result in station_outages(case, guard, policy, baseline):
        disrupted = replace(
            case,
            blackouts=tuple(b for b in case.blackouts if b.station != result["station"])
            + (Blackout(result["station"], 0, 120),),
        )
        plan = result["exact"]
        assert (
            -plan["utility"],
            plan["energy"],
            plan["reserved"],
            tuple(plan["selected"]),
        ) == oracle(disrupted, guard, policy)
        assert plan["violations"] == []
        assert result["utility_loss"] >= 0
        assert set(result["retained"]) | set(result["removed"]) == set(baseline["selected"])
        assert set(result["retained"]) | set(result["added"]) == set(plan["selected"])
        assert all("station-blackout" in item["reasons"] for item in result["directly_blocked"])
    assert repr(case) == before


def test_no_options_and_full_blackout_input_cap():
    """An unavailable network remains empty; six original blocks do not overflow the case cap."""
    case = fixture(Settings())
    case = replace(
        case,
        options=(),
        blackouts=tuple(Blackout("ALPHA", tick, tick + 1) for tick in (1, 3, 5, 7, 9, 11)),
    )
    result = station_outages(case, 1, 1, solve(case, 1, 1)[0])
    assert len(result) == 3
    assert all(item["exact"]["selected"] == item["request_changes"] == [] for item in result)
    run = build_run(Settings(scenario="unreachable-window"))
    assert run["id"] == run_id(run)
    assert all(item["utility_loss"] == 0 for item in run["outage_comparisons"])


def test_six_blocks_on_other_station_preserve_original_constraints():
    """A station absent from six imported blocks can still fail without overflowing the schema."""
    case = replace(
        fixture(Settings()),
        blackouts=tuple(Blackout("ALPHA", tick, tick + 1) for tick in (1, 3, 5, 7, 9, 11)),
    )
    baseline = solve(case, 1, 1)[0]
    result = station_outages(case, 1, 1, baseline)
    for station, comparison in zip(STATIONS, result, strict=True):
        disrupted = replace(case, options=tuple(o for o in case.options if o.station != station))
        optimum = oracle(disrupted, 1, 1)
        assert comparison["exact"]["selected"] == list(optimum[3])
