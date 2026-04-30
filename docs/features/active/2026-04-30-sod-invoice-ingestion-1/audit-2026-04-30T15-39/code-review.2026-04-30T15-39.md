# Code Review: SOD Invoice Ingestion (Issue #1)

---

**Review Date:** 2026-04-30
**Reviewer:** GitHub Copilot (feature_code_review_agent)
**Feature Folder:** `docs/features/active/2026-04-30-sod-invoice-ingestion-1`
**Base Branch:** `main`
**Head Branch:** `feature/sod-invoice-ingestion-1`
**Review Type:** Initial review

---

## Executive Summary

This review covers six changed files: `models/invoice.py`, `transform/invoice_transformer.py`, `load/db_loader.py`, `docker/init.sql`, `tests/test_transform.py`, and `tests/test_load.py`. The implementation extends the existing ETL pipeline with SOD invoice format support. The scope is moderate: one new TypedDict, four new private functions, five new regexes, updated SQL, and updated DB schema.

The implementation is well-structured and clean overall. Pydantic models are correctly typed and backward-compatible. The SOD parsing logic is organized into focused private helpers with thorough docstrings and intent-level inline comments. Pyright strict passes cleanly. All 20 tests pass.

One blocker exists: `db_loader.py` fails `poetry run black --check`. Two `text("""...""")` call sites require Black's wrapping reformatting. This must be fixed before merge. Two nit-level observations are documented for the next iteration.

**Top 3 risks:**
1. `db_loader.py` fails Black formatting check — the only hard blocker. Resolution is a single `black` invocation.
2. `_PARTIAL_ROW_RE` and `_DATE_IN_LINE_RE` are recompiled on every call to `_merge_truncated_lines()`. On high-volume invocations this could be a performance concern, though at current scale it is negligible.
3. The customer-name fallback heuristic (all-caps lines) in `_parse_sod_header` has limited test coverage and could produce incorrect results on pages with all-caps non-name content (e.g., column headers). This is a known approximation documented in the spec as acceptable.

**PR readiness recommendation:** **Needs Revision** — one blocker (Black formatting on `db_loader.py`) must be resolved before merge. All other checks pass.

---

## Findings Table

| Severity | File | Location | Finding | Recommendation | Rationale | Evidence |
|---|---|---|---|---|---|---|
| Blocker | `src/invoice_etl/load/db_loader.py` | Lines 35–56, 62–76 | `poetry run black --check` exits 1. Two `text("""...""")` call sites are not Black-compliant. Black requires the triple-quoted string to appear on a new indented line when additional arguments follow. | Run `poetry run black src/invoice_etl/load/db_loader.py` to auto-apply the required formatting. | The Python code change policy requires all code to pass Black without exception. The CI toolchain check will fail until this is resolved. | `poetry run black --check src tests` exit code 1; diff output in `policy-audit.2026-04-30T15-39.md §7`. |
| Nit | `src/invoice_etl/transform/invoice_transformer.py` | `_merge_truncated_lines()` body | `_PARTIAL_ROW_RE` and `_DATE_IN_LINE_RE` are compiled inside the function body on every call, inconsistent with the module-level regex pattern used for all other regexes in this file. | Move `_PARTIAL_ROW_RE` and `_DATE_IN_LINE_RE` to module scope alongside the other SOD-format regexes. | Compiling inside a function body is technically valid but inconsistent with the established pattern; module-level placement improves readability and avoids repeated compilation. | Code inspection: `invoice_transformer.py` lines ~175–178 vs module-level regex block starting at line ~42. |
| Nit | `src/invoice_etl/transform/invoice_transformer.py` | `_SOD_LINE_ITEM_RE` declaration | `re.MULTILINE` is applied to `_SOD_LINE_ITEM_RE`, but the regex is matched via `re.match()` on individual pre-split lines in `_parse_sod_line_item`. `MULTILINE` changes `^`/`$` anchor semantics for multi-line strings — it has no effect when the input is a single line. | Remove `re.MULTILINE` from `_SOD_LINE_ITEM_RE` to make the intent explicit and eliminate potential confusion for future maintainers. | A redundant flag does not affect behavior, but it implies the regex operates across line boundaries when it does not, which could mislead a reader or cause confusion if the calling code changes. | Code inspection: `_SOD_LINE_ITEM_RE` definition (line ~65) and usage in `_parse_sod_line_item` (line ~222). |

---

## Implementation Audit

### Python implementation audit

#### What changed well

- **Backward-compatible model extension**: All five new `LineItem` fields and the new `Invoice.customer_number` field default to `None`. Existing callers that do not supply the new fields continue to produce valid model instances without modification. This is the correct approach per the spec's backward-compatibility requirement.

- **Typed SOD header return**: `_SodHeader` TypedDict provides a strongly typed return contract for `_parse_sod_header`. This avoids stringly-typed dict access and gives Pyright full visibility over return fields. The choice of `TypedDict` over a dataclass is appropriate here — the struct is used only as a private helper return type with no methods.

- **Focused, single-responsibility helpers**: `_parse_sod_header`, `_merge_truncated_lines`, `_parse_sod_line_item`, and `_transform_sod_pages` each perform exactly one conceptual task. The separation matches the spec's explicit API definitions and makes the code easy to test in isolation.

- **Format detection via `transform_pages()`**: The SOD dispatch is implemented as a single string search (`"Customer Number:"` present in combined page text), keeping the public API unchanged and making the detection logic immediately readable.

- **Docstrings and inline comments**: Every private helper carries a full docstring (purpose, args, returns). The `_SOD_LINE_ITEM_RE` regex block includes a numbered comment explaining each of the nine capture groups. The `_parse_sod_header` header-extraction steps each carry a comment explaining the strategy and fallback logic. This level of documentation is appropriate and policy-compliant.

#### Typing and API notes

- All public and private functions are fully typed. No `Any` usage. No untyped library access.
- `_SodHeader` TypedDict is private (`_` prefix) and correctly scoped.
- `transform_pages()` public signature is unchanged (`pages: list[str], source_file: str | None = None) -> Invoice`). No breaking change.
- `load_invoice()` public signature is unchanged. The `invoice.model_dump(exclude={"line_items"})` call correctly serializes all Invoice fields to the INSERT parameter dict, which now includes `customer_number` automatically as a result of the model extension — a clean, low-maintenance approach.
- Pyright strict: 0 errors, 0 warnings. Confirmed via `poetry run pyright` (exit 0).

#### Error handling and logging

- `_parse_decimal` returns `None` on `InvalidOperation` — not re-raised. The caller (`_parse_sod_line_item`) propagates `None` fields to the `LineItem`, which accepts `Decimal | None`. This is the appropriate handling for malformed numeric data in a parsing context.
- `_parse_sod_line_item` returns `None` for non-matching lines. The caller (`_transform_sod_pages`) silently skips `None` results. This matches the spec contract: "headers, blank lines, total rows, and unresolvable truncated rows are silently skipped."
- `load_invoice` logs at `WARNING` on duplicate invoice and `INFO` on successful load. Appropriate levels.
- One edge case not tested: `_parse_sod_header` invoked with a page containing `TOTAL:` — the `_SOD_TOTAL_RE` path is not exercised by any current test fixture. This is a minor gap; no behavioral risk is implied, but the path is untested.
