# Remediation Inputs: SOD Invoice Ingestion (Issue #1)

**Timestamp:** 2026-04-30T15-39
**Source audit:** `policy-audit.2026-04-30T15-39.md`
**Source code review:** `code-review.2026-04-30T15-39.md`
**Source feature audit:** `feature-audit.2026-04-30T15-39.md`
**Feature folder:** `docs/features/active/2026-04-30-sod-invoice-ingestion-1`

---

## Required Fixes

### Fix 1 — BLOCKER: Apply Black formatting to `db_loader.py`

**File:** `src/invoice_etl/load/db_loader.py`
**Policy violated:** `python-code-change.instructions.md §1` — All Python code must be formatted with Black.
**Symptom:** `poetry run black --check src tests` exits 1. Two `text("""...""")` call sites need Black's multi-line-string-arg wrapping applied.

**Exact command to fix:**
```
poetry run black src/invoice_etl/load/db_loader.py
```

**Expected behavior after fix:** Black reformats the two `text(...)` call sites so that each triple-quoted SQL string starts on a new indented line and the closing `"""` appears before the `)`. Running `poetry run black --check src tests` must then exit 0.

**Verification command:**
```
poetry run black --check src tests
```
Expected exit code: 0.

**Note:** The fix is non-functional — it changes whitespace only. No logic changes are required.

---

### Fix 2 — Nit (optional, low priority): Move regexes out of `_merge_truncated_lines()`

**File:** `src/invoice_etl/transform/invoice_transformer.py`
**Finding:** `_PARTIAL_ROW_RE` and `_DATE_IN_LINE_RE` are compiled inside `_merge_truncated_lines()` on every call, inconsistent with the module-level regex pattern used for all other SOD regexes.
**Action:** Move both patterns to module scope alongside the other `_SOD_*_RE` constants.

**Verification command:**
```
poetry run pyright && poetry run pytest --cov=invoice_etl --cov-report=term-missing
```

---

### Fix 3 — Nit (optional, low priority): Remove redundant `re.MULTILINE` from `_SOD_LINE_ITEM_RE`

**File:** `src/invoice_etl/transform/invoice_transformer.py`
**Finding:** `re.MULTILINE` is applied to `_SOD_LINE_ITEM_RE` but the regex is matched via `re.match()` on individual pre-split lines. The flag has no effect.
**Action:** Remove `re.MULTILINE` from the `_SOD_LINE_ITEM_RE` declaration.

**Verification command:**
```
poetry run pytest tests/test_transform.py
```

---

## Do Not Do

- Do not modify any test assertions or expected values.
- Do not change any SQL strings beyond what Black's reformatting produces.
- Do not alter the `_SOD_LINE_ITEM_RE` regex pattern itself — only remove the `re.MULTILINE` flag if Fix 3 is applied.
- Do not introduce new dependencies or new public functions.
- Do not weaken type annotations or add `# type: ignore` suppressions.
- Do not change coverage thresholds in `pyproject.toml`.
- Do not modify policy documents under `.github/instructions/`.

---

## Required Toolchain Pass After Remediation

Run the full toolchain in this exact order and confirm all four steps exit 0 before marking remediation complete:

1. `poetry run black --check src tests` (must exit 0)
2. `poetry run ruff check src tests` (must exit 0)
3. `poetry run pyright` (must exit 0)
4. `poetry run pytest --cov=invoice_etl --cov-report=term-missing` (must exit 0, ≥ 82% coverage)

---

## Acceptance Criteria Re-verification After Remediation

After Fix 1 is applied and the full toolchain passes:
- AC #8 (`Full toolchain passes without errors`) must be re-evaluated as PASS in `feature-audit.2026-04-30T15-39.md`.
- The overall feature readiness verdict must be updated from NEEDS REVISION to PASS.
