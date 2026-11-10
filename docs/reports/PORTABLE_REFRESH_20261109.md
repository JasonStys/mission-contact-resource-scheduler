# Portable release refresh validation — 2026-11-09

By Jason Stys. Version 1.1.0 prepares independently validated station-loss replanning, retained/removed contacts and per-request service explanations.

## Recorded checks

Windows/Python3.14.6:645 Python tests passed with99.37% combined coverage (unchanged90% gate),12 TypeScript tests and27 real source Chromium/Firefox/WebKit journeys passed. Ruff, strict mypy and production build passed. All16 reviewed exact/greedy/delta outcomes remain unchanged; independent restoration of only the previous product-version field reproduced all16 old evidence hashes before the version-bound golden IDs were refreshed.

The actual Windows archive was inspected and extracted into a fresh temporary directory. Its executable ran from an unrelated working directory, preserved every previous native smoke contract, served only its owned loopback URL, matched package/version/instance identity, delivered actual compiled assets and completed the new real Chromium workflow/export. Local archive SHA-256: `a5a15436755b9c2497d40ce008b5aa4b97ac4f8ca871a52e78c48d9ee4411ef7`. This development archive honestly records dirty-source metadata; it is local acceptance evidence rather than a published clean-source release.

The original seventy release/archive/runtime tests use independent GitHub metadata fixtures and actual small archive bytes. They reject wrong source/version/repository, running/failed/incomplete/ambiguous workflow histories, existing draft/tag/public release, asset/checksum/metadata mismatch, link/path escape and corrupt frozen identity. Release guards remain active under optimized Python. No GitHub writes occur in these tests. Existing coverage, native/oracle, security and browser gates remain unchanged.

## Reproduce and limits

Use exact development locks and target native toolchains. Run the repository's full coverage suite, deterministic benchmark, strict lint/types/index/format checks, TypeScript tests/build and three-engine source browser suite, then `python tools/package_app.py`. The last command launches the real extracted application and its new feature in Chromium; it needs Node/Playwright only as build-time acceptance tools. Ordinary users need neither Python nor Node.

Finite offline invented contact candidates and units, not real station/radio scheduling. Station-loss replanning optimizes the existing objective; it does not promise minimum plan changes or operational availability.

Local native acceptance covers Windows only. Linux/macOS executable, links, ABI and UI still require real native CI. These unsigned portable folders are not installers or clean-machine installation proof. Native tests bypass the default OS browser opener, whose frozen POSIX inherited-library behavior remains a manual desktop check. No accounts, previous releases or user histories are changed. No push, dispatch, tag or release mutation was performed by this local work. The coordinator must review clean exact-source main checks, all three native jobs and all six uploaded assets/checksum digests before publishing.

## Authenticated draft lookup correction

The hosted application/UI checks passed before upload exposed an API-contract error: GitHub's releases-by-tag endpoint returns published releases and can return404 for an untagged draft. Preparation and upload now use a complete authenticated release listing (100 entries per page, at most three pages), require a unique exact tag and reread its numeric release ID. They validate list/detail identity and same-repository API/upload/assets URLs; upload additionally requires the exact source and non-prerelease draft state. A full cap, duplicated or swapped identity, lost access, malformed metadata,404 or network error cannot authorize absence or a write.

All19 independent real-shape API contract tests pass in the complete recorded suite. Existing archive/checksum/source/collision/non-clobber guards remain active; no application acceptance, coverage, security or native-OS job was removed or skipped. The previous actual extracted Windows workflow and separate three-engine source journeys remain recorded above; this follow-up changes release metadata acquisition, not the application feature or its numerical kernel. No live upload, draft mutation, push or workflow dispatch was performed by this local correction.
