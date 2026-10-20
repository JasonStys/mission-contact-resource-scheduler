# Architecture decisions

By Jason Stys. Status: implemented for a local educational workbench.

```text
Finite browser controls → loopback GET → validated Settings → synthetic Case
CLI local JSON ────────────────────────────────────────────→ strict Case
Case → original exact solver + greedy baseline → audit / explanations
     → canonical evidence → UI, JSON / CSV / HTML / input JSON
CLI explicit --history → parameterized immutable SQLite (100-run cap)
```

## ADR 001 — Small exact model instead of a large dependency stack

The user needs a demonstrable scheduling portfolio, clear trade-offs and trustworthy small-case results. Nine optional requests with two fixed alternatives fit a complete branch-and-bound search. Python integer arithmetic avoids tolerance/rounding ambiguity and the standard library is sufficient for CLI, immutable input records, HTTP, hash, exports and SQL. We chose this deliberately over a general optimizer service, distributed solver or premature C++/Rust layer. The cost is deliberately severe cardinality limits and no operational scale. Raising limits requires fresh complexity/performance evidence, not just editing a constant.

## ADR 002 — Python core, TypeScript browser, SQL history

The Python core has no browser coupling. TypeScript provides strict evidence/DOM contracts, escaping and finite preference validation; Vite emits local static assets with no production runtime framework. Semantic HTML, CSS and SVG provide responsive layout and proportional charts without external fonts, ads, CDN scripts or chart-library bloat. SQL enforces immutable rows in an explicitly chosen local database. These languages have actual responsibilities, not ornamental duplication.

## ADR 003 — One local read-only service

The same handler supports source and frozen desktop builds. Bind only IPv4 loopback; require exact Host and compatible Origin/Sec-Fetch-Site; expose no upload, account, arbitrary filesystem, remote fetch, shell or command endpoint. Build paths are confined even through symlinks. Every API request builds ephemeral synthetic evidence; optional preferences store controls only. CLI imports/history are outside HTTP. The server is **not** Internet-grade, has no authentication/TLS/request quotas and must not be exposed by proxies or tunnels. Local malicious processes and a compromised browser/OS remain outside the protection boundary.

## ADR 004 — Reproducible evidence before persistence

Each run includes complete input, effective settings, plans/totals, final obstacles, request outcomes, resource ledgers, scope and logical clock. Sorted compact UTF-8 JSON excluding `id` produces its SHA-256. No wall clock, machine path, random seed, timings or account identifier enters evidence, so identical inputs/configuration yield identical hashes across supported platforms. Optional history rejects altered hashes, deduplicates, caps at 100 and never deletes/updates rows. Export and history are separate files; no cross-file atomicity is promised.

## ADR 005 — Portable app, no privileged installer

PyInstaller freezes the stdlib service and production UI for each native runner OS/architecture. Users extract the whole directory and launch one executable; it opens a local browser. No global interpreter, auto-updater, registry entry, login, firewall change or elevation is needed. The executable is unsigned and not a mobile app; source UI works in modern browsers, but remote mobile connectivity is intentionally not enabled. Native runner smoke tests check actual bundled resources/API/exports. Tests cannot promise every Linux distribution, macOS release, endpoint-protection policy or device.

## ADR 006 — CI without consuming artifact allowance

Actions storage was full at project start. Validation logs, deterministic committed summaries and release assets supply evidence; no workflow uploads Actions artifacts or caches. Setup-node's implicit cache is explicitly disabled. Source validation covers Linux/Python 3.12 and 3.14, Windows/macOS Python 3.14, three Linux browser engines and three packaged apps. SHA-pinned actions and a version/exact-source gate protect manual draft releases. Release assets are a separate GitHub storage category, not Actions artifacts. No existing user runs/caches are deleted or altered.

## Failure handling

Invalid imports return a controlled CLI error before optimization. Exports refuse overwrite. HTTP emits generic errors, no local paths or stack traces. UI hides stale results after changes or failure, aborts superseded fetches, offers manual retry and keeps preference failure nonfatal. CI rejects benchmark/index drift instead of silently rebaselining it. Releases remain drafts until all native jobs, checksums and reviewed evidence pass; delete/replace is not an automated recovery action.
