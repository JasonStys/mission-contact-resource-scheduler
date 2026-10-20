# CI and release verification record

By Jason Stys. Observed 2026-10-20; no simulated remote successes. The local measured baseline and test strategy are in [VALIDATION](../VALIDATION.md).

## First published source baseline

Commit: `89ac297f7f83c9b964d7f01a6b88a5fb19d014b3`.

- [Validation run 39512063030](https://github.com/JasonStys/mission-contact-resource-scheduler/actions/runs/39512063030): **success**, all eight jobs. Linux Python 3.12/3.14, Windows/macOS Python 3.14; Linux browser job; Linux, Windows and macOS actual frozen executable/package jobs.
- [CodeQL run 39512062967](https://github.com/JasonStys/mission-contact-resource-scheduler/actions/runs/39512062967): **success**, Python and JavaScript/TypeScript security-and-quality analysis. Zero open code-scanning alerts on review.
- Python source baseline: 542 tests, 99.32% branch-inclusive coverage. Browser baseline: 21 acceptance checks (seven per engine); TypeScript unit baseline: 12 tests. Strict types/lint/format, exact-line inventory, deterministic contracts, dependency audits and actual packaged CLI/API/assets smoke passed in their applicable jobs.

## Final review and release gate

Final review additionally escaped numeric API fields before HTML insertion and added a hostile-response regression. Local browser suite then passed **24 checks** (eight each in Chromium, Firefox and WebKit), preserving existing download/accessibility/keyboard assertions. The scheduling model, deterministic hashes and Python test results are unchanged.

This report intentionally cites a completed earlier source baseline rather than claiming its own future commit already passed. Publication requires a **new successful Validation and CodeQL run on the exact final source SHA**, enforced by `tools/prepare_release.py`; release notes link those final runs. The manual Portable release workflow repeats three native builds/smokes and uploads ZIP/checksum pairs to a draft for review. Successful preparation alone is not a successful release; all three builds/assets and downloaded hashes must be checked before publishing.

## Storage policy

Initial account billing: 0.5 GB used / 0.5 GB included (100%). This repo's live Actions artifact bytes and cache entries were both zero after its first successful workflows. Existing user runs/artifacts/caches were not deleted. These workflows upload no Actions artifacts/caches; native downloadable bundles use separate release assets, not Actions storage. The account-wide live inventory and accumulated billing are distinct measures.
