# Release and rollback procedure

By Jason Stys. Release workflow produces **drafts**, not automatic public binaries.

## Gates before shipping

- Review scope, model assumptions, import limits, license notices, dependency audit results and local screenshots.
- Run Python tests/coverage, lint/format/types, benchmark and inventory drift checks; run TypeScript unit/build/format/audit and three-browser acceptance.
- Run `python tools/package_app.py` locally. It builds a native directory bundle, executes actual frozen CLI/API/HTML smoke tests, ZIPs the entire directory and emits a SHA-256 file.
- Push reviewed source to main and require **Validation and CodeQL success on that exact SHA**. Inspect code-scanning findings, not just job status. Do not disable checks to unblock a release.
- Check Actions billing allowance and live artifact inventory before workflows. This repository deliberately uploads no Actions artifacts or caches; never delete user runs/caches without fresh authorization.

## Manual native release

Dispatch `Portable release` on main with a new digits.digits.digits version. The prepare script validates the string and queries the exact source SHA's Validation/CodeQL runs. Both must have succeeded; it creates a new draft at that SHA. Three native runner jobs build from hashed/pinned tooling, run the real executable smoke and upload only their platform ZIP/checksum pair directly to the draft. Existing assets are not overwritten. Actions artifacts/cache storage is not used.

Review all jobs and six assets, verify downloaded SHA-256 digests, extract into a new user-owned directory and smoke the Windows executable. Linux/macOS executable smoke is run natively by CI. Do not claim local execution on a platform not actually available. Review release notes, unsigned limitations, supported architecture, exact source/check links and checksum manifest, then publish the draft. A failed platform leaves a draft and must be investigated; it is not a partially successful release.

Expected initial runner architectures are Linux x86_64, Windows AMD64 and macOS ARM64; release filenames report the **actual** native build architecture. Do not run an incompatible binary or disable OS protections. The three native builds are not mobile applications, universal Linux distribution packages or byte-for-byte reproducible builds. Source remains available on supported Python/Node runtimes.

## Rollback and maintenance

There is no auto-updater, system service, database migration or global install. Stop the process, retain local exports/history privately, and select a previous verified release/source tag in a separate directory. Never replace a running bundle in place, silently rewrite a published asset/tag, delete user's history or rebaseline deterministic contracts solely to hide a regression. Report defects through the project's issue/contact channels without sensitive files.

Dependency upgrades require hash-lock regeneration/review, all gates and a new version. Any model/output change requires reviewing deterministic hashes and documenting semantic differences. Exact-line indexes must be regenerated after formatted code changes. Future scale/real operations integration is a separate design/review scope, not an incremental deployment setting.
