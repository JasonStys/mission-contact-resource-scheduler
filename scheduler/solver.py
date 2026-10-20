"""Deterministic greedy and exact branch-and-bound planning by Jason Stys.

Functions: overlap, blockers, audit, summarize, solve. Variables: request lookup,
incumbent plan, suffix utility bounds and visited/pruned search counts.
All limits and objective ties: docs/MODEL.md; exact lines: docs/CODE_INDEX.md.
"""

from typing import Any

from scheduler.model import BANDS, SPACECRAFT, STATIONS, Case, Option, Request


def overlap(start: int, end: int, other_start: int, other_end: int) -> bool:
    """Half-open intervals conflict only on positive-length intersection; touching is safe."""
    return start < other_end and other_start < end


def value(request: Request, policy: int) -> int:
    """Throughput policy 0 uses units; policy 1 weights complete units by priority."""
    return request.units * (request.priority if policy else 1)


def blockers(case: Case, option: Option, selected: tuple[Option, ...], guard: int) -> list[str]:
    """Explain intrinsic and final-plan obstacles; not a minimal unsatisfiable core."""
    requests = {request.id: request for request in case.requests}
    request = requests[option.request]
    start, end = option.start - guard, option.end + guard
    reasons = []
    if start < 0 or end > case.horizon:
        reasons.append("guard-outside-horizon")
    if option.start < request.release or option.end > request.deadline:
        reasons.append("request-time-window")
    if (option.end - option.start) * option.rate < request.units:
        reasons.append("insufficient-capacity")
    if request.band not in BANDS[option.station]:
        reasons.append("incompatible-band")
    if any(
        b.station == option.station and overlap(start, end, b.start, b.end) for b in case.blackouts
    ):
        reasons.append("station-blackout")
    if any(item.request == option.request for item in selected):
        reasons.append("request-already-selected")
    if any(
        item.station == option.station and overlap(start, end, item.start - guard, item.end + guard)
        for item in selected
    ):
        reasons.append("station-guard-conflict")
    if any(
        requests[item.request].spacecraft == request.spacecraft
        and overlap(option.start, option.end, item.start, item.end)
        for item in selected
    ):
        reasons.append("spacecraft-conflict")
    reserved = sum(
        item.end - item.start + 2 * guard for item in selected if item.station == option.station
    )
    if reserved + end - start > case.station_budgets[STATIONS.index(option.station)]:
        reasons.append("station-budget")
    used_energy = sum(
        item.energy for item in selected if requests[item.request].spacecraft == request.spacecraft
    )
    if used_energy + option.energy > case.energy_budgets[SPACECRAFT.index(request.spacecraft)]:
        reasons.append("spacecraft-energy-budget")
    return reasons


def audit(case: Case, selected: tuple[Option, ...], guard: int) -> list[str]:
    """Independently re-evaluate all chosen contacts against the full remaining allocation."""
    issues = []
    if len({item.id for item in selected}) != len(selected):
        issues.append("duplicate-option")
    known = {item.id: item for item in case.options}
    for index, option in enumerate(selected):
        if known.get(option.id) != option:
            issues.append("unknown-option")
            continue
        for reason in blockers(case, option, selected[:index] + selected[index + 1 :], guard):
            issues.append(option.id + ":" + reason)
    return sorted(set(issues))


def rank(
    case: Case, selected: tuple[Option, ...], guard: int, policy: int
) -> tuple[int, int, int, tuple[str, ...]]:
    """Minimize negative utility, then energy, reserved ticks, then sorted candidate IDs."""
    requests = {request.id: request for request in case.requests}
    return (
        -sum(value(requests[item.request], policy) for item in selected),
        sum(item.energy for item in selected),
        sum(item.end - item.start + 2 * guard for item in selected),
        tuple(sorted(item.id for item in selected)),
    )


def summarize(case: Case, selected: tuple[Option, ...], guard: int, policy: int) -> dict[str, Any]:
    """Produce deterministic plan totals; audits remain explicit and separately inspectable."""
    objective = rank(case, selected, guard, policy)
    requests = {request.id: request for request in case.requests}
    return {
        "selected": list(objective[3]),
        "utility": -objective[0],
        "energy": objective[1],
        "reserved": objective[2],
        "units": sum(requests[item.request].units for item in selected),
        "fulfilled": len(selected),
        "violations": audit(case, selected, guard),
    }


def solve(case: Case, guard: int, policy: int) -> tuple[dict[str, Any], dict[str, Any]]:
    """Search all feasible alternatives with an admissible bound; no timeout or early cutoff."""
    requests = {request.id: request for request in case.requests}
    eligible = tuple(
        sorted(
            (item for item in case.options if not blockers(case, item, (), guard)),
            key=lambda item: item.id,
        )
    )
    greedy: tuple[Option, ...] = ()
    for option in sorted(
        eligible, key=lambda item: (-value(requests[item.request], policy), item.start, item.id)
    ):
        if not blockers(case, option, greedy, guard):
            greedy += (option,)
    groups = [
        (request, tuple(item for item in eligible if item.request == request.id))
        for request in sorted(case.requests, key=lambda item: item.id)
    ]
    suffix = [0] * (len(groups) + 1)
    for index in range(len(groups) - 1, -1, -1):
        suffix[index] = suffix[index + 1] + value(groups[index][0], policy)
    best = greedy
    best_rank = rank(case, best, guard, policy)
    visited = 0
    pruned = 0

    def search(index: int, selected: tuple[Option, ...], utility: int) -> None:
        """Branch once per feasible alternative plus skip; suffix is an optimistic utility bound."""
        nonlocal best, best_rank, visited, pruned
        visited += 1
        # Strict inequality preserves improvements on energy/time/lexical tie breakers.
        if utility + suffix[index] < -best_rank[0]:
            pruned += 1
            return
        if index == len(groups):
            candidate_rank = rank(case, selected, guard, policy)
            if candidate_rank < best_rank:
                best, best_rank = selected, candidate_rank
            return
        request, options = groups[index]
        for option in options:
            if not blockers(case, option, selected, guard):
                search(index + 1, selected + (option,), utility + value(request, policy))
        search(index + 1, selected, utility)

    search(0, (), 0)
    exact = summarize(case, best, guard, policy)
    exact.update(
        status="OPTIMAL",
        visited_nodes=visited,
        pruned_nodes=pruned,
        upper_bound=exact["utility"],
        gap=0,
        feasible_candidates=len(eligible),
    )
    return exact, summarize(case, greedy, guard, policy)
