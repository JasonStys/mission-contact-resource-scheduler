# Model, objective and limits

By Jason Stys. This is resource-allocation mathematics on invented fixed intervals, not orbit/contact prediction, RF analysis, flight software or mission operations.

## Inputs and interpretation

The horizon is `[0,120)` logical ticks. Stations are ALPHA (S/X), BRAVO (X) and CHARLIE (S); spacecraft are SC-A, SC-B and SC-C. Band names are compatibility labels only, not transmission configuration. All labels, windows, budgets, priorities, rates, data and energy values are synthetic.

A request has ID, spacecraft, band, priority 1–20, required data 1–40 units, release and deadline. It is optional and all-or-nothing: select at most one alternative and deliver exactly the required amount; unused link capacity earns nothing. Requests with no alternatives remain unscheduled and visible. There are 1–9 requests, 0–18 options, at most two options per request and 0–6 blackout intervals. There are no mandatory requests, dependencies, fairness constraints, partial deliveries or continuous start-time decisions.

Each option supplies a fixed station, start/end, energy charge 1–40 and capacity rate 1–4. Intervals and blackout bounds are integer ticks within the horizon, with positive length. IDs match `[A-Z][A-Z0-9-]{0,15}` and are unique within requests/options. Resource budgets are positive integers up to 80, one per resource. See [API](API.md) for strict input shape.

## Constraints

For a chosen contact `o` and per-side guard `g`:

1. Station reservation is `[o.start − g, o.end + g)` and must fit within the horizon.
2. Spacecraft transmission is `[o.start, o.end)`, with no spacecraft guard reservation.
3. Transmission must start at/after request release and end at/before deadline.
4. `(end − start) × rate ≥ request.units` and the station must support the request's band.
5. Guarded station intervals must not intersect a station blackout or another chosen reservation at that station.
6. Spacecraft transmission intervals must not overlap, even across different stations.
7. Sum of guarded durations at each station must not exceed its station-time budget.
8. Sum of chosen energy charges per spacecraft must not exceed its energy budget.
9. At most one alternative per request can be selected.

Every interval is **half-open**. `overlap(a,b,c,d)` is `a < d and c < b`; touching endpoints do not conflict. Blackouts do not consume an additional budget charge; they remove available time. Energy is an aggregate accounting charge, not a battery state-of-charge or recharge/thermal model. Station budgets charge all reserved guard ticks. Spacecraft are only exclusive during transmission. No transit, slew, travel, light-time, antenna motion, propagation, uncertainty or frequency tuning is modeled.

All requests are optional. Therefore the empty allocation is always feasible. A fully blocked case yields an **optimal empty plan**, not “the mission is infeasible” or “every request can be fulfilled.”

## Objective and solver proof boundary

Policy 0 utility is complete delivered data. Policy 1 utility is `priority × delivered data`. These integer priorities are user-defined preference weights, not authoritative mission importance. The deterministic objective is:

1. Maximize total utility.
2. Minimize total energy.
3. Minimize total reserved station ticks.
4. Minimize the sorted selected-option ID tuple lexicographically.

The greedy baseline considers intrinsically eligible options by descending utility, then start and ID. It accepts an option only if all hard constraints still hold. It uses the same objective's primary utility and constraints but does not optimize global ties. It is a comparison baseline, not a competitive guarantee.

The exact solver groups options by sorted request ID, removes intrinsically impossible options, then recursively considers each feasible alternative and skipping the request. The initial incumbent is the feasible greedy plan. Its suffix bound sums remaining request utilities, ignoring resource contention; hence it cannot underestimate attainable utility. Pruning uses **strictly smaller** utility bounds, preserving equal-utility energy/time/lexical improvements. No timeout, node cap, stochastic search or “best so far” claim replaces complete search.

At most three branches per request and nine requests imply at most `1+3+…+3^9 = 29,524` visited recursion nodes. A loose runtime bound is `O(3^R × (N+R+B))` plus preprocessing/explanations, with requests `R≤9`, options `N≤18`, blackouts `B≤6`; compatibility checks scan selected contacts. Stack and tuple copies take `O(R²)` space; case/output tables are bounded. These small limits make an original dependency-free solver inspectable, **not scalable to a real ground network**.

After complete search, `status=OPTIMAL`, `upper_bound=utility` and `gap=0` mean the optimum over exactly these candidates/constraints/objective. The bound is a consequence of completed search, not an LP relaxation certificate. The production audit rechecks each selected option against the remainder. Tests additionally use an independent subset-enumeration oracle that does not call production feasibility/ranking helpers. This is engineering evidence, not formal verification.

An unselected option's reasons are intrinsic blockers and/or conflicts against the **final exact allocation**. They can overlap. They are not a minimal unsatisfiable core, counterfactual proof, unique cause, or assertion that the option could never appear in another optimum.

## Reviewed fixture controls

Guard: 0/1/2; common energy cap: 12/24/40; common station budget: 24/36/60; policy: 0/1. Eight scenarios yield 432 combinations. Local imported cases retain their named resource budgets and only use guard/policy; unused fixture controls do not affect imported evidence hashes.

| Scenario            | Deliberate pressure                                                           |
| ------------------- | ----------------------------------------------------------------------------- |
| nominal             | Shared stations, alternative contacts, finite common budgets                  |
| station-outage      | BRAVO unavailable for all 120 ticks                                           |
| maintenance         | ALPHA `[18,42)`, CHARLIE `[56,78)` unavailable                                |
| tight-energy        | SC-B cap reduced to 8 or less than configured common cap                      |
| urgent-insertion    | Ninth optional high-priority request with two alternative windows             |
| impossible-deadline | R08 deadline shortened to 85, leaving neither candidate eligible              |
| greedy-trap         | One 100-utility long contact competes with two compatible 60-utility contacts |
| unreachable-window  | All three stations unavailable; empty allocation is optimal                   |

No fixture uses real mission identity, location, ephemeris or restricted data. Rounding and physical-unit conversions are intentionally absent: every comparison is bounded integer arithmetic.

## Research and extensions

NASA's [Scheduling NASA’s Deep Space Network: Priorities, Preferences, and Optimization](https://ntrs.nasa.gov/citations/20220001560) (publication 2020-10-21) discusses oversubscription and diverse competing priorities/preferences. It motivates showing trade-offs rather than calling one static ranking universally correct. We do **not** reproduce NASA scheduling software or data, nor claim comparability.

Google's [OR-Tools job-shop scheduling documentation](https://developers.google.com/optimization/scheduling/job_shop) explains interval/exclusivity constraints. A mature CP-SAT or mixed-integer formulation is a reasonable future alternative for larger candidate sets, fairness or dependencies; it is **not integrated** here. No external algorithm implementation was copied. References accessed 2026-10-20.
