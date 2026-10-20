# User guide

By Jason Stys. No account, network ground system, paid API or administrator privileges required.

## Launch the desktop bundle

1. Obtain the ZIP for your exact OS/architecture and its `.sha256` file from the repository's Releases page.
2. Verify the ZIP before extracting. Windows PowerShell: `Get-FileHash -Algorithm SHA256 .\mission-contact-resource-scheduler-windows-amd64.zip`. Linux: `sha256sum -c <checksum-file>`. macOS: `shasum -a 256 <zip>`. Compare the full digest, not just the first characters.
3. Extract the entire ZIP to a folder you own. Keep the executable and `_internal` resources together.
4. Launch `MissionContactScheduler.exe` on Windows or `MissionContactScheduler` on the supplied Linux/macOS architecture. If the terminal download lost its executable bit, `chmod +x MissionContactScheduler` is sufficient on that **known verified file**, not a system-wide change.
5. The console prints a `http://127.0.0.1:<ephemeral-port>/` URL and opens your default browser. If the browser does not open, copy that URL. Keep the console running; use Ctrl-C to stop.

The bundles are unsigned/not notarized. Do not disable antivirus, remove quarantine, bypass SmartScreen/Gatekeeper/browser warnings, run as administrator or change firewall settings. Use source after review if your policy blocks unsigned apps. No installer, login, auto-updater or mobile binary is supplied. Browser layout is responsive, but the service intentionally does not expose remote/mobile access.

## Work through a case

1. Choose a scenario and finite resource/guard/objective controls. The default uses priority × data. Changing controls hides prior evidence until solved; this prevents stale-download confusion.
2. Solve allocation. The top cards always summarize the **exact** plan, with utility difference from the greedy baseline and constraint audit.
3. In the timeline, switch exact/greedy and optionally filter spacecraft. The filter affects only the drawing, not complete-plan totals or downloads. Colored bars are transmissions; lighter outer bars are reserved station guards; gray rectangles are blackouts. The horizontal axis is logical time, not UTC.
4. Choose a candidate in the inspector. It shows transmission/reservation/required window, capacity, band, energy and baseline membership. For unselected candidates, read final-plan obstacles, which are not a unique causal explanation or minimal conflict set.
5. Read station and energy usage bars for the exact plan. The request table includes every request even if unscheduled or without alternatives. On a narrow screen, tab to the labeled scrollable table and use arrow keys to scroll.
6. Download full JSON for complete evidence, candidate-only CSV, the inert HTML report or editable input JSON. Downloading does not save a history or upload data anywhere.

The greedy-trap default gives exact 120 vs greedy 100. In throughput mode its exact choice is different because the primary utility definition changes; this is expected, not nondeterminism. In all-stations-unavailable, empty is optimal: no contacts, eight unscheduled requests, zero constraint violations.

## Local JSON and history

Use the source CLI or executable from a terminal, with the same subcommands:

```text
MissionContactScheduler export --scenario nominal --format input --output my-case.json
MissionContactScheduler export --input my-case.json --guard 1 --policy 1 --format json --output review.json --history history.sqlite3
```

On Windows use `MissionContactScheduler.exe`; PowerShell needs `.\MissionContactScheduler.exe` for an executable in the current folder. In source substitute `python -m scheduler` for the executable. [API](API.md) describes strict input ranges and [examples/nominal.json](../examples/nominal.json) is editable. Imported budgets remain authoritative; only guard/policy are used from controls. Use synthetic cases only, not operational/sensitive mission data.

Output files must not already exist. History is opt-in, local, unencrypted, immutable through this app and limited to 100 distinct hashes. Choose a new path when full; the app never deletes old evidence. History and export are separate file operations. A history insert may succeed even if the subsequent export cannot be written. Keep private output outside your Git checkout. Nothing appears in the browser history API because none exists.

## Preferences and help

“Remember these controls” is off by default. Opting in stores only five controls in browser localStorage at this origin; unchecking removes them. No case, report, password or personal information is stored. A blocked storage API does not prevent planning. Different ports are different browser origins, so an ephemeral relaunch may not find prior preferences.

No contacts or outputs means check the chosen scenario and inspector, not a failed solver. An API failure hides old results and offers manual retry; ensure the console still runs. Port conflict: omit `--port` for an ephemeral port. Missing assets: rebuild with `npm ci` and `npm run build`, or re-extract the whole verified bundle. Invalid JSON: use exact keys and actual integers, check duplicate keys and the 64 KiB limit. Slow/unbounded model needs are outside this lab; do not simply increase limits.

Field guide is embedded in the UI. Detailed model, assumptions and evidence live in [MODEL](MODEL.md) and [VALIDATION](VALIDATION.md). Questions/non-sensitive bugs: [Jason Stys on GitHub](https://github.com/JasonStys) or [repository issues](https://github.com/JasonStys/mission-contact-resource-scheduler/issues). Do not attach private local paths, tokens or real mission data.
