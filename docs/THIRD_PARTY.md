# Dependencies, notices and research

By Jason Stys. Project code and synthetic examples: MIT ([LICENSE](../LICENSE)).

## Runtime and portable distribution

- Source Python service: CPython standard library only. CPython and bundled standard-library license notices are in [licenses/PYTHON.txt](../licenses/PYTHON.txt), included with each portable bundle. Runtime extension-library notices supplied by CPython accompany its license text; no external Python application dependency is required.
- Browser production output is compiled original TypeScript/CSS/HTML/SVG with Vite; no browser framework, chart library, remote font or AI service is embedded. Build-tool runtimes are not shipped as a Node install.
- PyInstaller (GPL with its distributed bootloader exception) creates the native bundles. Its locked distribution `COPYING.txt`, containing the exception, is copied to `licenses/pyinstaller` inside the bundle. This permits distribution of original application code under its own license; it is not a claim that PyInstaller itself is MIT.
- PyInstaller may include OS-dependent support from its locked build graph. Development tools remain governed by their upstream licenses; `requirements-dev.lock` and `package-lock.json` identify exact distributions and integrity hashes. No operating system, browser or proprietary driver is redistributed.

## Development-only tooling

Python: pytest/pytest-cov/coverage, Hypothesis, Ruff, mypy, pip-audit and PyInstaller with their pinned transitive graph. Browser: TypeScript, Vite, Vitest, Playwright, axe-core and Prettier. Tool notices are available in installed distribution metadata/node_modules licenses; these directories are ignored, not committed. GitHub Actions uses pinned official checkout/setup tools and CodeQL; CodeQL's service licensing/usage conditions are separate from this project's MIT source. Locked versions are a reproducibility aid, not permission to ignore future advisories.

`npm audit` and `pip-audit` query current advisory services during verification. Their reports are time-specific and cannot guarantee unknown vulnerabilities absent. Runtime uses none of those services. Generated screenshots depict this application's synthetic data and contain no third-party artwork or private records.

## Research references (accessed 2026-10-20)

- NASA NTRS, [Scheduling NASA’s Deep Space Network: Priorities, Preferences, and Optimization](https://ntrs.nasa.gov/citations/20220001560), published 2020-10-21: concepts of competing priorities/preferences and oversubscribed shared communication resources.
- Google OR-Tools, [Job shop scheduling](https://developers.google.com/optimization/scheduling/job_shop): interval and resource-exclusivity concepts, alternative future implementation direction.

No external solver/library implementation, mission dataset or NASA scheduling code is incorporated. Research motivates the educational problem only. No NASA, government, military, contractor or other affiliation, validation, endorsement or certification is implied.
