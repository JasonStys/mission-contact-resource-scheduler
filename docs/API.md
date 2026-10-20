# Input, HTTP and evidence contracts

By Jason Stys. Version 1.0.0. This interface is for the local educational application only.

## Strict local case

[examples/nominal.json](../examples/nominal.json) is the complete editable schema. Exact top-level fields:

```json
{
  "horizon": 120,
  "requests": [
    {
      "id": "R1",
      "spacecraft": "SC-A",
      "band": "X",
      "priority": 2,
      "units": 4,
      "release": 0,
      "deadline": 120
    }
  ],
  "options": [
    {
      "id": "A",
      "request": "R1",
      "station": "ALPHA",
      "start": 10,
      "end": 20,
      "energy": 4,
      "rate": 1
    }
  ],
  "blackouts": [],
  "station_budgets": { "ALPHA": 24, "BRAVO": 24, "CHARLIE": 24 },
  "energy_budgets": { "SC-A": 12, "SC-B": 12, "SC-C": 12 }
}
```

Unknown/missing fields, duplicate keys at any depth, booleans masquerading as integers, floats/strings, NaN/Infinity, excessive nesting, invalid labels/references/intervals, resource count mismatch or cardinality violations fail closed. The parser reads at most 65,537 bytes to enforce a 65,536-byte cap. Structural validity is distinct from eligibility: a structurally valid candidate with insufficient capacity, incompatible band, bad release/deadline fit or blocked time stays visible with a reason; it is not silently removed from the report. Invalid schema does not yield a partial run.

Local imports are **CLI only**, not browser uploads. They must fit the finite model and are not arbitrary ephemerides or real operations data. Guard and policy apply; named budgets come from the imported case. The scenario/common-cap/common-budget CLI arguments are fixture selectors, ignored and omitted from effective imported settings. Use only synthetic non-sensitive inputs for this lab.

## Read-only HTTP

All routes require exact `Host: 127.0.0.1:<port>`. Origin must be absent or exactly `http://127.0.0.1:<port>`; cross-site Fetch Metadata is rejected. No CORS. GET only; mutation methods and HEAD return 405. Query length is at most 1024 characters and at most eight fields; duplicate/unknown fields fail.

| Route                       | Contract                                                                                |
| --------------------------- | --------------------------------------------------------------------------------------- |
| `/api/health`               | Fixed status/mode; no query                                                             |
| `/api/catalog`              | Scenario labels, finite choices, defaults and resource names; no query                  |
| `/api/run`                  | Complete evidence JSON; optional finite settings below; no `format`                     |
| `/api/report`               | Same settings plus `format=json\|csv\|html\|input`; attachment with fixed safe filename |
| `/`, `/assets/<built-name>` | Exact built HTML or confined JS/CSS/SVG/ICO files; no arbitrary paths/query             |

Settings: scenario in the eight documented names; guard 0/1/2; energy_cap 12/24/40; station_budget 24/36/60; policy 0/1. Defaults: nominal, 1, 24, 36, 1. Integer query strings are parsed then checked. No live resource state, source paths, uploads, local history or import is exposed. A port conflict is an error, never permission to bind a public interface.

Statuses: 200 valid; 400 unsupported parameters/format; 403 rejected Host/origin/site; 404 missing/disallowed asset; 405 unsupported method; 414 oversized target; 500 unavailable local resource. Failures include restrictive headers and generic messages. CSP permits only same-origin script/style/connect, forbids frames/objects/forms and external content; no unsafe-inline or eval. Referrer, MIME, frame, cache and sensor-permission policies are set too.

## Evidence and exports

`id` is SHA-256 over sorted compact UTF-8 JSON of all fields except `id` (`allow_nan=False`). Report fields:

- `version`, `scenario` (or local-json), effective `settings`, full `case`, `provenance`.
- `exact` / `greedy`: sorted selected IDs, utility, energy, reserved ticks, complete data units, fulfilled count and audit violations. Exact additionally reports completed-search status, visited/pruned nodes, feasible candidate count, terminal upper bound and zero gap.
- `delta`: exact utility minus greedy utility (not a percentage improvement or runtime claim).
- `candidates`: full options, spacecraft, exact/baseline membership and final-plan reasons.
- `requests`: every optional request, selected option/null and all alternatives, including none.
- `station_usage` / `energy_usage`: exact allocation usage/budgets, unaffected by UI chart filter or baseline switch.

Full JSON is authoritative for complete evidence; CSV is a candidate-only view and cannot represent a request that has no candidates. HTML contains the complete escaped JSON report, no script or dynamic content. Input JSON is the original case only and can be reimported; reimport changes provenance to local-json, so its evidence SHA differs from the fixture run even when the allocations agree. Labels and reason codes are controlled, so CSV cannot contain formula-prefixed user text. All four download names are server constants. No evidence is sent to a third-party service.

## Optional history

`--history PATH` creates/uses local SQLite with schema in `scheduler/resources/history.sql`. The application checks the run hash, uses parameterized statements, immediate insert transaction, idempotent same-content ID insertion, collision check, immutable update/delete triggers and 100-run cap. A full database is not pruned: choose a new explicit path. History is plain local data, **not encrypted**; protect it using OS permissions/full-disk encryption. Do not commit it. Schema triggers are integrity guards, not protection from an administrator editing the database. Separate history/export operations are not one atomic transaction.
