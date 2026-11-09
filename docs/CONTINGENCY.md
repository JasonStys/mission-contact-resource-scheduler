# Compare station-loss plans

After solving, open **Single-station loss contingency** and expand a station. The workbench solves three independent alternatives: ALPHA, BRAVO or CHARLIE unavailable over `[0, 120)`. These use the current case, including strict CLI imports, with every blackout, budget, request and guard unchanged. A full-window loss removes every candidate option at that station, which is equivalent to a full-horizon blackout without adding a seventh block to a case already at the six-blackout input cap.

Each alternative runs the existing exact branch-and-bound solver and greedy comparison. It lists retained, removed and added contact IDs; before/after request assignments; utility loss; energy and fulfilled-contact changes; and intrinsic reasons for directly blocked original contacts. A contact away from the failed station may change because station occupancy, spacecraft energy and the complete utility objective interact. This is a fresh optimum with the established energy/time/lexical tie breakers, **not** a minimum-change or locked-contact optimizer.

The original exact/greedy timeline still describes the original case. Alternative plans appear in the contingency panel and full JSON/HTML reports, CLI exports and immutable history, all covered by the evidence hash. Expand a result to review unscheduled requests rather than assuming the original service level survives. An empty feasible plan is valid and explicitly reported.

This bounded offline comparison is for planning education, not live mission dispatch, contact prediction or operational assurance. Tests independently enumerate every subset for realistic finite cases, check objective ties, retain original cases unchanged and exercise no-option and fully unavailable networks.
