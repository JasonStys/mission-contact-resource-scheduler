"""Independent exhaustive oracle, grid and constraint tests by Jason Stys.

Functions: oracle, case helpers and test contracts. Variables: subsets, intervals,
random bounded cases and objective tuples. Definition lines: docs/CODE_INDEX.md.
The oracle deliberately does not call production blockers, audit or rank.
"""

from dataclasses import replace
from itertools import combinations, product

import pytest
from hypothesis import given
from hypothesis import settings as hypothesis_settings
from hypothesis import strategies as st

from scheduler.engine import CHOICES, SCENARIOS, Settings, build_run, fixture
from scheduler.model import BANDS, SPACECRAFT, STATIONS, Blackout, Case, Option, Request
from scheduler.solver import audit, blockers, overlap, solve


def oracle(case, guard, policy):
    """Enumerate every subset and independently check all constraints and objective ties."""
    requests = {item.id: item for item in case.requests}
    best = (0, 0, 0, ())
    for mask in range(1 << len(case.options)):
        chosen = [item for index, item in enumerate(case.options) if mask & (1 << index)]
        if len({item.request for item in chosen}) < len(chosen):
            continue
        valid = True
        for item in chosen:
            req = requests[item.request]
            if not (
                0 <= item.start - guard < item.end + guard <= case.horizon
                and req.release <= item.start < item.end <= req.deadline
                and req.units <= (item.end - item.start) * item.rate
                and req.band in BANDS[item.station]
            ):
                valid = False
            for block in case.blackouts:
                if block.station == item.station and max(block.start, item.start - guard) < min(
                    block.end, item.end + guard
                ):
                    valid = False
        for left, right in combinations(chosen, 2):
            if left.station == right.station and max(left.start - guard, right.start - guard) < min(
                left.end + guard, right.end + guard
            ):
                valid = False
            if requests[left.request].spacecraft == requests[right.request].spacecraft and max(
                left.start, right.start
            ) < min(left.end, right.end):
                valid = False
        for index, station in enumerate(STATIONS):
            if (
                sum(item.end - item.start + 2 * guard for item in chosen if item.station == station)
                > case.station_budgets[index]
            ):
                valid = False
        for index, spacecraft in enumerate(SPACECRAFT):
            if (
                sum(
                    item.energy
                    for item in chosen
                    if requests[item.request].spacecraft == spacecraft
                )
                > case.energy_budgets[index]
            ):
                valid = False
        if valid:
            score = (
                -sum(
                    requests[item.request].units
                    * (requests[item.request].priority if policy else 1)
                    for item in chosen
                ),
                sum(item.energy for item in chosen),
                sum(item.end - item.start + 2 * guard for item in chosen),
                tuple(sorted(item.id for item in chosen)),
            )
            best = min(best, score)
    return best


@pytest.mark.parametrize("values", list(product(SCENARIOS, *CHOICES.values())))
def test_all_finite_settings(values):
    """Every supported fixture/configuration is deterministic, feasible and no worse than greedy."""
    scenario, guard, energy_cap, station_budget, policy = values
    run = build_run(Settings(scenario, guard, energy_cap, station_budget, policy))
    assert run == build_run(Settings(scenario, guard, energy_cap, station_budget, policy))
    assert run["exact"]["violations"] == run["greedy"]["violations"] == []
    assert run["delta"] >= 0 and run["exact"]["status"] == "OPTIMAL"
    assert run["exact"]["gap"] == 0
    assert run["exact"]["visited_nodes"] <= 29524
    assert all(
        item["used"] <= item["budget"] for item in run["station_usage"] + run["energy_usage"]
    )
    for item in run["candidates"]:
        if not item["selected"]:
            assert item["reasons"], "Positive-value unused option must have a final-plan obstacle"


@given(
    st.lists(
        st.tuples(
            st.integers(0, 100),
            st.integers(1, 15),
            st.integers(1, 12),
            st.integers(1, 10),
            st.integers(0, 2),
            st.integers(0, 2),
        ),
        min_size=1,
        max_size=8,
    ),
    st.integers(0, 2),
    st.integers(0, 1),
)
@hypothesis_settings(max_examples=100, deadline=None, derandomize=True)
def test_generated_cases_against_independent_oracle(rows, guard, policy):
    """Random small cases compare the entire optimum, not just feasibility or utility."""
    requests = tuple(
        Request(f"R{i}", SPACECRAFT[sc], "X", priority, 3, 0, 120)
        for i, (_, _, _, priority, sc, _) in enumerate(rows)
    )
    options = tuple(
        Option(f"O{i}", f"R{i}", STATIONS[station], start, start + duration, energy, 1)
        for i, (start, duration, energy, _, _, station) in enumerate(rows)
    )
    case = Case(120, requests, options, (Blackout("BRAVO", 50, 55),), (35, 30, 25), (18, 16, 20))
    result, _ = solve(case, guard, policy)
    assert (
        -result["utility"],
        result["energy"],
        result["reserved"],
        tuple(result["selected"]),
    ) == oracle(case, guard, policy)


@pytest.mark.parametrize("guard,policy", list(product(range(3), range(2))))
def test_alternatives_ties_and_permutation(guard, policy):
    """Multiple alternatives are solved exhaustively and lexical ties do not depend on input order."""
    base = fixture(Settings(scenario="greedy-trap"))
    case = replace(base, options=base.options + (Option("A0", "R01", "BRAVO", 10, 30, 10, 1),))
    exact, _ = solve(case, guard, policy)
    assert (
        -exact["utility"],
        exact["energy"],
        exact["reserved"],
        tuple(exact["selected"]),
    ) == oracle(case, guard, policy)
    assert solve(
        replace(
            case, options=tuple(reversed(case.options)), requests=tuple(reversed(case.requests))
        ),
        guard,
        policy,
    ) == solve(case, guard, policy)


def small_case():
    """Two different spacecraft share a station with exactly touching guarded boundaries."""
    return Case(
        120,
        (Request("R1", "SC-A", "X", 2, 4, 0, 120), Request("R2", "SC-B", "X", 2, 4, 0, 120)),
        (Option("A", "R1", "ALPHA", 10, 20, 4, 1), Option("B", "R2", "ALPHA", 22, 32, 4, 1)),
        (),
        (24, 24, 24),
        (12, 12, 12),
    )


def test_guard_boundary_and_budgets():
    """Endpoint contact is permitted; additional guard consumes time and creates a conflict."""
    case = small_case()
    assert not overlap(0, 10, 10, 20)
    assert solve(case, 1, 1)[0]["selected"] == ["A", "B"]
    assert solve(case, 2, 1)[0]["fulfilled"] == 1
    assert "station-budget" in blockers(
        replace(case, station_budgets=(23, 24, 24)), case.options[1], (case.options[0],), 1
    )
    assert "station-blackout" in blockers(
        replace(case, blackouts=(Blackout("ALPHA", 20, 22),)), case.options[0], (), 1
    )


@pytest.mark.parametrize(
    "change,guard,reason",
    [
        ({"start": 0}, 1, "guard-outside-horizon"),
        ({"start": 118, "end": 120}, 1, "guard-outside-horizon"),
        ({"end": 12}, 0, "insufficient-capacity"),
        ({"station": "CHARLIE"}, 0, "incompatible-band"),
        ({"energy": 13}, 0, "spacecraft-energy-budget"),
    ],
)
def test_intrinsic_reasons(change, guard, reason):
    """Each intrinsic eligibility rule has a focused negative boundary fixture."""
    case = small_case()
    option = replace(case.options[0], **change)
    assert reason in blockers(case, option, (), guard)


def test_spacecraft_and_request_conflicts():
    """Different ground stations cannot contact the same spacecraft at overlapping times."""
    case = small_case()
    option = replace(case.options[1], station="BRAVO", start=15, end=25)
    changed = replace(
        case,
        requests=(case.requests[0], replace(case.requests[1], spacecraft="SC-A")),
        options=(case.options[0], option),
    )
    assert "spacecraft-conflict" in blockers(changed, option, (case.options[0],), 0)
    assert "request-already-selected" in blockers(case, case.options[0], (case.options[0],), 0)
    assert "duplicate-option" in audit(case, (case.options[0], case.options[0]), 0)
    assert "unknown-option" in audit(case, (replace(option, id="NO"),), 0)


def test_empty_and_impossible_cases():
    """Empty is a feasible allocation, not a claim that every optional request is satisfiable."""
    assert build_run(Settings(scenario="unreachable-window"))["exact"]["fulfilled"] == 0
    run = build_run(Settings(scenario="impossible-deadline"))
    assert run["requests"][-1]["selected"] is None
    assert all(
        "request-time-window" in item["reasons"]
        for item in run["candidates"]
        if item["request"] == "R08"
    )
    empty = replace(small_case(), options=())
    assert solve(empty, 1, 1)[0]["utility"] == 0


def test_greedy_trap():
    """Two compatible short contacts beat the long highest-value contact, 120 versus 100."""
    run = build_run(Settings(scenario="greedy-trap"))
    assert run["exact"]["selected"] == ["B1", "C1"]
    assert (run["exact"]["utility"], run["greedy"]["utility"], run["delta"]) == (120, 100, 20)


def test_objective_tie_breakers():
    """Equal utility prioritizes energy, then occupied ticks, then lexical IDs; skip pruning is strict."""
    case = replace(
        small_case(),
        requests=small_case().requests[:1],
        options=(
            Option("Z", "R1", "BRAVO", 10, 25, 3, 1),
            Option("A", "R1", "ALPHA", 10, 20, 3, 1),
        ),
    )
    assert solve(case, 1, 1)[0]["selected"] == ["A"]
    assert solve(
        replace(case, options=(replace(case.options[0], energy=2), case.options[1])), 1, 1
    )[0]["selected"] == ["Z"]
    assert solve(replace(case, options=(replace(case.options[0], end=20), case.options[1])), 1, 1)[
        0
    ]["selected"] == ["A"]
