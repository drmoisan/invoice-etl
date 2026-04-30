# Code Review: SOD Invoice Ingestion (Issue #1)

---

**Review Date:** 2026-04-30
**Reviewer:** GitHub Copilot (feature_code_review_agent)
**Feature Folder:** `docs/features/active/2026-04-30-sod-invoice-ingestion-1`
**Base Branch:** `main`
**Head Branch:** `feature/sod-invoice-ingestion-1`
**Review Type:** Post-remediation re-review

---

## Executive Summary

This post-remediation re-review covers the SOD invoice ingestion feature on `feature/sod-invoice-ingestion-1` (head `0fbc09cb`) relative to `main` (base `2b3192cb`). The feature adds a SOD-format parsing path to the existing invoice ETL pipeline, extending two Pydantic models, adding four private transformer helpers, updating the PostgreSQL schema, and adding 12 new tests.

Evidence reviewed: PR context artifacts (`artifacts/pr_context.summary.txt`, `artifacts/pr_context.appendix.txt`), post-remediation QA gate artifacts under `evidence/qa-gates/`, and direct inspection of the six changed production files and two test files.

**What changed:**
Six production files were modified: `models/invoice.py` (new SOD fields), `transform/invoice_transformer.py` (SOD parse path), `load/db_loader.py` (new INSERT columns + Black formatting fix), `docker/init.sql` (schema columns), `tests/test_transform.py` (12 new tests), `tests/test_load.py` (2 new tests). The temporary `inspect_pdf.py` script was deleted. No new dependencies were introduced.

**Top 3 risks:**
1. The `customer_name` extraction heuristic in `_parse_sod_header` relies on all-caps line detection with a company-suffix regex. If a future SOD invoice vendor uses a name that does not match this heuristic, `customer_name` silently defaults to the last all-caps line — this is a graceful degradation but may produce unexpected values in edge cases.
2. The `_get_engine()` function in `db_loader.py` remains untested (requires live env vars). This is pre-existing and not introduced by this feature; however, it remains a gap in the load layer's test coverage.
3. `main.py` is at 0% coverage. This is pre-existing and out of scope for this feature, but is noted as a future quality gap.

**PR readiness recommendation:** **Go** — all toolchain checks pass, all 8 acceptance criteria are met, no blockers or major findings remain after remediation.

---

## Findings Table

| Severity | File | Location | Finding | Recommendation | Rationale | Evidence |
|---|---|---|---|---|---|---|
| Info | `src/invoice_etl/transform/invoice_transformer.py` | `_parse_sod_header()`, customer_name fallback | The `caps_lines[-1]` fallback for `customer_name` returns the last all-caps line when the company-suffix regex fails. On some SOD pages this may be a total label or section heading rather than the vendor name. | Document the limitation in the function docstring; consider adding a future-work note. | Graceful degradation is acceptable for this feature scope; the field is `None`-tolerant downstream. | Direct code inspection; `spec.md` explicitly excludes vendor name as a non-goal. |
| Info | `src/invoice_etl/load/db_loader.py` | Lines 18–24 (`_get_engine`) | `_get_engine()` is untested (72% module coverage). Lines 18–24 and 34 are not exercised by any test. | Track as a future improvement; add integration tests or env-mocking tests in a follow-on task if DB connectivity testing is required. | Pre-existing gap at baseline (69%); not introduced by this feature. | `evidence/baseline/baseline-pytest.md`, `evidence/qa-gates/remediation-qc-pytest.md` |
| Info | `src/invoice_etl/main.py` | All lines | `main.py` has 0% coverage. | Track as a pre-existing gap. Not in scope for this feature. | Pre-existing at baseline; not modified in this PR. | `evidence/baseline/baseline-pytest.md` |

No Blockers or Major findings.

---

## Implementation Audit

### Python implementation audit

#### What changed well

- The SOD parsing path is cleanly separated from the generic path. `transform_pages()` dispatches on a single string sentinel (`"Customer Number:"`), keeping the detection logic minimal and the existing generic path entirely unchanged.
- The `_SodHeader` TypedDict is a well-chosen internal contract: it provides structural typing for the header return without requiring a full Pydantic model for an internal-only structure.
- Module-level regex constants are grouped, named with the `_SOD_*_RE` convention, and each is annotated with a comment explaining what it matches. This makes future regex changes safe and auditable.
- Post-remediation movement of `_PARTIAL_ROW_RE` and `_DATE_IN_LINE_RE` to module scope is a clear improvement: constants that do not capture closures belong at module scope, and this placement is consistent with the rest of the file.
- Removal of the redundant `re.MULTILINE` flag from `_SOD_LINE_ITEM_RE` is correct. The pattern uses `^` and `$` anchors with `re.match`, so `MULTILINE` had no effect and its removal avoids reader confusion.
- All new Pydantic model fields default to `None`, ensuring that existing callers constructing `LineItem` or `Invoice` without the SOD fields continue to work without modification.
- `docker/init.sql` uses `IF NOT EXISTS` guards consistently, making the schema idempotent for fresh-init scenarios.

#### Typing and API notes

- All function signatures are fully annotated. `_parse_sod_header` returns `_SodHeader` (a `TypedDict`), which Pyright resolves cleanly in strict mode as confirmed by the `0 errors, 0 warnings` result.
- `_parse_sod_line_item` returns `LineItem | None` — appropriate for a partial-match function. Callers filter on `if item is not None:`.
- The `# type: ignore[reportPrivateUsage]` suppressions in `test_transform.py` are correctly scoped and each carries a justification comment, complying with the Python suppressions policy.
- The `transform_pages()` public signature is unchanged: `(pages: list[str], source_file: str | None = None) -> Invoice`. No public API breakage.
- No `Any` is used in any new production code.

#### Error handling and logging

- `_parse_decimal` catches `InvalidOperation` specifically — not a broad `Exception` catch. This is compliant with the error handling policy.
- `logger.warning(...)` is used in `load_invoice()` for the duplicate-invoice skip path. `logger.info(...)` is used for successful loads. Both are appropriate log levels.
- `datetime.datetime.strptime` is allowed to raise `ValueError` on date parse failure. This is intentionally fail-fast: a malformed date in a SOD invoice is an unexpected format change that warrants a visible error rather than silent suppression.
- No `print` statements exist in any production file.
