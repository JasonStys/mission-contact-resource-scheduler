# Documentation refresh — 2026-11-09

By Jason Stys.

This documentation-only edition describes source `4e5c7ecf87d8ac372a3a45cafc9b539a4fc660f3`. It does not change application behavior, accounts, private data, installers or published releases.

## Published editions and completed review

| File                                                 | Bytes | SHA-256                                                            | Reviewed scope                                                                                                                      |
| ---------------------------------------------------- | ----: | ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| [project-guide.docx](project-guide.docx)             | 75458 | `c15c49dfbd42904296ce1d8db7ec231c71d1e941fc7028f23fd4a24085530610` | 4 pages, each viewed individually                                                                                                   |
| [validation-review.docx](validation-review.docx)     | 41883 | `24d72d6f5a06d5d64167e820d7b188ad1db1b0fecced179158ffcdd540d7d377` | 3 pages, each viewed individually                                                                                                   |
| [validation-evidence.xlsx](validation-evidence.xlsx) |  7380 | `e5cd3929e049074c361261063425dd34523020dd83d25d9f55a8b66fd9c0ba6a` | Both tab previews; two actual Excel Tables/autoFilters; four formulas; failure-change/restore recalculation and zero formula errors |

Word review checked plain black titles, readable pagination, whole table rows, source references, practical limits and absence of clipping or overflow. Render receipts were matched to the current DOCX digest before approval. Workbook review inspected both tab previews and actual exported Table/autoFilter elements; recalculated success/failure summaries were compared independently with workflow metadata. Static previews do not draw Excel dropdown arrows; the exported workbook contains the actual filters.

## Evidence and change boundary

- Functional baseline: `4e5c7ecf87d8ac372a3a45cafc9b539a4fc660f3`.
- Workflow observation: `2026-11-10T05:25:40.628667+00:00`; exact run URLs and source identities remain in [publications.json](publications.json).
- Local document-package validation verifies exact copied bytes, Office ZIP integrity, approved page/tab identities and internal documentation links. Repository-specific documentation and source-policy commands are run separately and recorded in the integration handoff.
- Source/index metadata is regenerated using the repository’s existing tools. Existing privacy, security, coverage and workflow gates are retained.
- PR and later main workflows must pass independently. This record does not claim future or unrun integration CI success.

## Interpretation

The Word files document the cited source; dated source reports retain their original execution scope. A passing workflow is distinct from completed analysis with zero findings, and neither establishes production suitability. The Excel source inventory is not a per-test execution report. Checksums identify exact bytes, not a signature or publisher attestation.

Use the [handbook](../handbook.md) to choose usage, design, security and test documentation. Keep editable Markdown and reviewed editions together; do not replace historical measurements with undated claims.
