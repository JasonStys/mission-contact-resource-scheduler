"""Portable deterministic scheduler contracts and descriptive timing by Jason Stys.

Functions: snapshot, main. Variables: scenario/policy grid, evidence hashes and timings.
Reviewed JSON changes require --write; timings are informational, never a flaky CI gate.
Exact definition locations: docs/CODE_INDEX.md.
"""

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scheduler.engine import SCENARIOS, Settings, build_run  # noqa: E402


def snapshot() -> str:
    """Pin all eight fixture defaults under both objectives, including complete evidence hashes."""
    rows = []
    for scenario in SCENARIOS:
        for policy in (0, 1):
            run = build_run(Settings(scenario=scenario, policy=policy))
            rows.append(
                {
                    "scenario": scenario,
                    "policy": policy,
                    "id": run["id"],
                    "exact": run["exact"],
                    "greedy": run["greedy"],
                    "delta": run["delta"],
                }
            )
    return (
        json.dumps(
            {
                "description": "Synthetic fixed-candidate planning contracts by Jason Stys; not flight performance",
                "cases": rows,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def main() -> int:
    """Fail on deterministic drift; explicitly write reviewed contracts and an editable example."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    path = ROOT / "docs/reports/benchmark.json"
    content = snapshot()
    example = json.dumps(build_run(Settings())["case"], indent=2, sort_keys=True) + "\n"
    for destination, value in ((path, content), (ROOT / "examples/nominal.json", example)):
        if args.write:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(value, encoding="utf-8", newline="\n")
        elif not destination.is_file() or destination.read_text(encoding="utf-8") != value:
            raise SystemExit("Contract drift: review model changes before --write")
    timings = []
    for _ in range(20):
        start = time.perf_counter()
        build_run(Settings(scenario="urgent-insertion"))
        timings.append((time.perf_counter() - start) * 1000)
    print(
        f"16 deterministic contracts passed; uncached urgent-case median {statistics.median(timings):.3f} ms (descriptive only)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
