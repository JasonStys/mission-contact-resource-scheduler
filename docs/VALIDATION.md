# Validation evidence and strategy

By Jason Stys. Local baseline: 2026-10-20 on Windows x64, CPython 3.14.6 and Node 24.18.1. This report distinguishes observed results from scope limitations and future CI results.

## Observed local baseline

| Gate                                       | Observed result                                                                                                                                                       |
| ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Python integration/model/solver suite      | 542 passed; 99.32% branch-inclusive coverage of `scheduler` (minimum gate 90%)                                                                                        |
| Finite scenario grid                       | All 432 combinations deterministic, feasible, exact utility ≥ greedy, budgets respected; included above                                                               |
| Independent oracle                         | 100 deterministic Hypothesis-generated small cases plus six alternative/permutation cases and objective tie fixtures; full objective tuple compared, not just utility |
| Deterministic contracts                    | 16 fixture/objective evidence hashes and summaries match reviewed JSON                                                                                                |
| TypeScript unit tests                      | 12 passed: finite preferences, malformed input, escaping, SVG/guard/filter contracts                                                                                  |
| Ruff / strict mypy / production TypeScript | Passed locally                                                                                                                                                        |
| Dependency audits                          | npm: 0 reported vulnerabilities; pip-audit: no known vulnerabilities at check time                                                                                    |

The uncached urgent-insertion benchmark measured approximately 1.66 ms median over 20 local runs during development. This is descriptive machine-specific wall time, **not** a CI performance threshold, latency guarantee or comparison with a production scheduler. Deterministic contracts deliberately exclude timing. [reports/benchmark.json](reports/benchmark.json) is reviewed reproducible output, not a fabricated historical report.

Browser and portable-release results are recorded after their actual verification; see [reports/ci-baseline.md](reports/ci-baseline.md) and exact workflow/release links. A badge alone is not evidence that every feature or environment is supported.

All 21 local browser acceptance checks passed (seven each in Chromium, Firefox and WebKit), including actual downloads, mobile axe scans and keyboard access. The actual local Windows frozen executable also passed CLI JSON export, production HTML/assets, health and greedy-trap API smoke tests.

## Layered checks

1. **Schema/bounds:** all integer/ID/resource/time constraints, exact object keys, references, cardinalities, unknowns, duplicate JSON keys at all depths, NaN/Infinity, oversized input, nesting/UTF-8 errors, no-alternative requests, imported authoritative budgets and hash invariance under unused fixture settings.
2. **Scheduling:** independent subset enumeration checks hard constraints and the complete four-level optimum. Production audit does not serve as its own oracle. Fixed tests target half-open endpoints, guard/blackout boundaries, resource exhaustion, same-spacecraft different-station overlaps, duplicate request/option selection, lexical ties, insufficient capacity, incompatible bands, impossible deadlines, alternative ordering and empty allocation semantics.
3. **Properties:** all 432 fixture settings repeat identically and beat/match greedy on utility. Every positive-value unselected candidate has a final-plan obstacle. Resource usage never exceeds budgets; full evidence hashes change with meaningful inputs.
4. **I/O:** actual loopback sockets—not mocked route calls—exercise successes, path/encoding/traversal confinement, rebinding/origin/site protection, duplicate/excessive/unknown queries, fixed download names, methods, generic resource failures and oversized targets. CLI export refuses overwrite and handles local filesystem/database errors. SQL tests check parameters, immutable update behavior, idempotence, altered hashes and cap without pruning.
5. **UI:** production handler/build, Chromium/Firefox/WebKit, greedy/exact comparison, guards/filter, outaged station, impossible deadline, empty plan, all four actual downloads, API failure/retry, opt-in preferences, 390-pixel viewport, keyboard scrolling/focus and axe WCAG-tag scans. Automated scans are not a comprehensive manual accessibility audit or certification.
6. **Distribution:** actual frozen executable exports JSON and serves real web assets/health/greedy-trap API before the native ZIP is produced. Release CI repeats this independently on three OS runners. Each release ZIP has a SHA-256 manifest. Downloaded release assets are verified again before publication.

## Development findings and fixes

- The initial download test used an exact accessible name without the visible down-arrow suffix; corrected the locator, retaining actual download/content assertions. This was a test mismatch, not a broken download.
- The mobile request table was horizontally scrollable but not keyboard-focusable. Axe reproduced a serious keyboard-access finding. The actual UI was fixed with a labeled focusable region and a focused arrow-key regression check; no axe rule was disabled.
- Windows pytest-generated temporary names were too long when raw 64 KiB malformed data became a parameter ID. Short semantic test IDs fix the test harness without reducing payload/edge-case coverage.
- Strict warning policy detected deprecated iterable parametrization; materialized the six combinations instead of filtering the warning.
- A redundant development CSS import was rejected by Vite; removed it. All styling remains local, with no remote fonts/imports.

The debugging skill guided reproduction, isolation, root-cause fixes and regression assertions. Production constraints, oracle checks and security gates were not loosened to make tests pass.

## CI and storage

`validate.yml` has eight jobs: four Python/OS configurations, one three-engine browser job, and three native packaging/smoke jobs. `codeql.yml` checks Python and JavaScript/TypeScript. `release.yml` checks exact-source successful workflows before creating a draft, then builds/smokes/uploads three native bundles. Workflow action versions are SHA-pinned; dependency locks include hashes/integrity.

Storage checked before implementation: billing showed 0.5 GB / 0.5 GB, 100%. REST live artifact inventory was 58,024,434 bytes across 85 repositories; separate caches 14,697,246,742 bytes. Live inventory and accumulated billing are different measures, not contradictory quota estimates. This repo uploads no Actions artifacts/caches. Existing runs, latest artifacts and caches were left untouched. Release assets are a separate category. Reports contain only public synthetic/code evidence, no private billing credentials.

## Limits

No orbital/contact prediction, radio physics, real-time telemetry, command delivery, fairness/mandatory tasks, continuous-time optimization, uncertainty, light-time, production-scale workload, network hosting, mobile native bundle, signed/notarized executable, penetration test or operational certification was validated. Cross-platform CI and browser tests do not prove every OS/browser version or assistive technology. A full green test suite is evidence for this finite model, not permission to use it for actual mission operations.
