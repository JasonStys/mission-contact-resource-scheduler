# Security and safe use

By Jason Stys. This project is a local educational synthetic planning tool, **not** a flight/ground command system, production web host, security boundary against the device owner or certified operational scheduler.

## Trust boundaries

| Boundary                | Controls                                                                                                                       | Residual limit                                                                                                     |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| Browser → local service | IPv4 loopback only; exact Host; Origin/Fetch Metadata checks; no CORS; read-only finite GET; strict query limits               | Local malware, browser extensions, OS administrators and same-device clients remain trusted/uncontrolled           |
| URL → filesystem        | Exact index/build-asset routes, no query/path traversal/encoded separators, resolved symlink confinement                       | An attacker who modifies the local build/executable already controls the app                                       |
| Local case → model      | CLI only, 64 KiB cap, strict exact schema, duplicate-safe JSON, fixed resources and cardinalities, no eval/shell/remote fetch  | Not an arbitrary file parser; do not use sensitive/operational data                                                |
| Evidence → UI/export    | Escaped dynamic text/attributes, safe label grammar, numeric fields and fixed reason codes, inert HTML, fixed attachment names | JSON/history are unencrypted local files; protect destinations with OS controls                                    |
| UI → external content   | Restrictive CSP, no inline scripts/eval, no CDN/font/analytics/ad/AI calls, no embeds/forms/remote assets                      | Deliberate external GitHub/profile/help links open only on user action; browser/OS security still matters          |
| History → SQL           | Parameter binding, verified SHA, immediate transaction, immutable triggers, 100-entry cap                                      | Local administrators can alter SQL/files; hashes are integrity checks, not authenticated signatures                |
| Source → release        | Hashed dependency locks, pinned action SHAs, audits, CodeQL, exact-commit checks, native smoke tests and SHA-256               | No reproducible-byte build claim, signing/notarization, zero-vulnerability guarantee or universal OS compatibility |

No account, personal-data collection, telemetry, scraping, listening beyond loopback, live station/spacecraft control, radio tuning, targeting, evasion, exploit or command integration exists. No uploads/imports/history over HTTP. No auto-updater, privileged installer, system setting changes or execution of imported data. The Python HTTP handler is not hardened for public exposure; do not tunnel, proxy or bind it to the Internet. Multiple local clients can consume CPU; no authentication or service-level rate limiter is claimed. Finite model limits bound individual work, not all concurrent work.

All UI requests use the local service. Downloads/persistence are explicit. Optional browser preference stores controls only. Dependency downloads and security audits occur at build/development time, not normal application runtime. ZIP/JSON/SQL files must be handled under the user's ordinary backup/privacy policy. All example data is invented; the repository contains no credentials or private user records.

## Reporting

For non-sensitive defects use [GitHub issues](https://github.com/JasonStys/mission-contact-resource-scheduler/issues), with version, OS and a minimized **synthetic** reproduction. Do not publish credentials, private files, operational data or exploit against a third party. For a sensitive concern use an appropriate private contact channel linked on [Jason Stys's GitHub profile](https://github.com/JasonStys); do not assume a public issue is private. No staffed response-time or guaranteed private advisory channel is promised.

## Validation is not certification

Coverage, tests, scans, checksums and reviews reduce risk but cannot prove all defects absent. Verify the exact release hash and source; do not bypass unsigned-software warnings or disable protections. Version 1.0.0 supports only the documented finite model. Real mission scheduling requires independently validated physical models, authoritative inputs, uncertainty handling, operational review and applicable certification not provided here.
