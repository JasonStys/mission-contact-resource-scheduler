# Mission Contact Resource Scheduler handbook

By Jason Stys.

The released 1.1.0 portable scheduler includes station-loss contingency comparisons: inspect retained, removed and replacement contacts, per-request service changes and utility loss, then download complete planning evidence.

The released 1.1.0 portable scheduler includes station-loss contingency comparisons: inspect retained, removed and replacement contacts, per-request service changes and utility loss, then download complete planning evidence.

The existing exact finite-candidate solver and independent exhaustive oracle are preserved. The extracted application proves the hand-checkable 60 + 60 versus 100 greedy trap, a fully lost station and feasible empty service before comparing the actual UI download with its API result. Source-bound native packaging carries the practical replanning workflow into downloads.

## Read the documentation

The [illustrated Windows guide](reports/windows-application-guide.docx) adds actual
installed-app screenshots, a worked scenario, source excerpts and dated acceptance.
Its [review manifest](reports/windows-application-guide.json) identifies the exact
reviewed bytes. Earlier Office editions below retain their historical baselines.

| Edition                                                      | Audience and contents                                                                                              |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| [project-guide.docx](reports/project-guide.docx)             | User and developer guide: purpose, current usage, design, boundaries and source references.                        |
| [validation-review.docx](reports/validation-review.docx)     | Reviewer edition: exact tested baseline, observed workflows, dated local results and remaining limits.             |
| [validation-evidence.xlsx](reports/validation-evidence.xlsx) | Two filterable Excel Tables for observed workflows and test-source inventory, with recalculating outcome formulas. |

The editable Markdown remains the maintenance source. The Word files are readable editions. The workbook is an evidence index rather than a test runner. See [publication identities and review](reports/publications.json) and the [documentation refresh record](reports/documentation-refresh-2026-11-09.md).

## Current usage and help

[README quick start](../README.md) is the entry point. Use the project-specific guides below before changing inputs, operating modes or deployment assumptions.

### Usage and operations

- [RELEASE](RELEASE.md)
- [USER GUIDE](USER_GUIDE.md)
- [releases/v1.1.0](releases/v1.1.0.md)

### Design and contracts

- [API](API.md)
- [ARCHITECTURE](ARCHITECTURE.md)
- [MODEL](MODEL.md)

### Security and validation

- [VALIDATION](VALIDATION.md)

## Historical results and reproduction

The reviewed source is [`4e5c7ecf87d8ac372a3a45cafc9b539a4fc660f3`](https://github.com/JasonStys/mission-contact-resource-scheduler/tree/4e5c7ecf87d8ac372a3a45cafc9b539a4fc660f3). The observed functional workflow baseline is `4e5c7ecf87d8ac372a3a45cafc9b539a4fc660f3`; those observations are recorded at `2026-11-10T05:25:40.628667+00:00`. They do not certify an unrun later revision.

- [Detailed recorded validation](reports/PORTABLE_REFRESH_20261109.md)
- [Current Actions](https://github.com/JasonStys/mission-contact-resource-scheduler/actions) records later integration checks separately.
- Preserve dated measurements and follow the existing testing guide to reproduce them; a test-source inventory alone does not establish execution.

## Practical boundaries

- Invented finite candidates and units; no real radio, ground-station dispatch or operational availability guarantee.
- Replanning optimizes the existing objective; it does not guarantee minimum changes to a previous plan.
- Unsigned desktop portable folders, not system installers or clean-machine proof. Three-OS extracted-native checks drive an owned URL; default OS browser opening remains manual.

## Maintaining these editions

Update the editable usage/design/test documents first. Rebuild and visually review every Word page and workbook tab before replacing an edition; verify the exact binary digests and evidence source in publications.json. Keep account data, logs with secrets, installed-app state and private test stores out of documentation. Source and release assets retain their existing security and licensing boundaries.
