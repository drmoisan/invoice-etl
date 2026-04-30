# SOD Invoice Ingestion — Remediation Plan

- **Issue:** #1
- **Issue URL:** https://github.com/drmoisan/invoice-etl/issues/1
- **Requirements Source:** `docs/features/active/2026-04-30-sod-invoice-ingestion-1/remediation-inputs.2026-04-30T15-39.md`
- **Parent plan:** `docs/features/active/2026-04-30-sod-invoice-ingestion-1/plan.2026-04-30T11-01.md`
- **Owner:** drmoisan
- **Last Updated:** 2026-04-30T15-39
- **Status:** Ready
- **Version:** 1.0
- **Work Mode:** full-feature

## Overview

Apply `poetry run black` to `src/invoice_etl/load/db_loader.py` to resolve the single formatting blocker identified in `policy-audit.2026-04-30T15-39.md`. Optionally apply two nit-level refactors in `invoice_transformer.py` (move two regexes to module scope; remove redundant `re.MULTILINE`). Run the full toolchain to confirm all four steps pass. No logic changes, no test changes, no schema changes.

## Required References

- Copilot Instructions: [`.github/copilot-instructions.md`](../../../../.github/copilot-instructions.md)
- General Coding Standards: [`.github/instructions/general-code-change.instructions.md`](../../../../.github/instructions/general-code-change.instructions.md)
- General Unit Test Policy: [`.github/instructions/general-unit-test.instructions.md`](../../../../.github/instructions/general-unit-test.instructions.md)
- Python Code Change Policy: [`.github/instructions/python-code-change.instructions.md`](../../../../.github/instructions/python-code-change.instructions.md)
- Python Unit Test Policy: [`.github/instructions/python-unit-test.instructions.md`](../../../../.github/instructions/python-unit-test.instructions.md)
- Python Suppressions Policy: [`.github/instructions/python-suppressions.instructions.md`](../../../../.github/instructions/python-suppressions.instructions.md)
- Self-Explanatory Code Commenting: [`.github/instructions/self-explanatory-code-commenting.instructions.md`](../../../../.github/instructions/self-explanatory-code-commenting.instructions.md)

**All work must comply with these policies. Do not duplicate their content here.**

---

### Phase 0 — Baseline Capture

- [x] [P0-T1] Read all seven required policy documents in mandated order and record evidence at `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/baseline/phase0-remediation-instructions-read.md`.
  - Policy read order: (1) `.github/copilot-instructions.md`, (2) `.github/instructions/general-code-change.instructions.md`, (3) `.github/instructions/general-unit-test.instructions.md`, (4) `.github/instructions/python-code-change.instructions.md`, (5) `.github/instructions/python-unit-test.instructions.md`, (6) `.github/instructions/python-suppressions.instructions.md`, (7) `.github/instructions/self-explanatory-code-commenting.instructions.md`.
  - Acceptance: File exists and contains `Timestamp:`, `Policy Order:`, and explicit list of all seven files read.

- [x] [P0-T2] Capture pre-remediation Black state: run `poetry run black --check src tests` and record artifact at `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/baseline/remediation-baseline-black.md`.
  - Acceptance: File exists, contains `Timestamp:`, `Command: poetry run black --check src tests`, `EXIT_CODE: 1`, `Output Summary:` confirming `db_loader.py` would be reformatted.

- [x] [P0-T3] Capture pre-remediation test state: run `poetry run pytest --cov=invoice_etl --cov-report=term-missing` and record artifact at `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/baseline/remediation-baseline-pytest.md`.
  - Acceptance: File exists, contains `Timestamp:`, `Command:`, `EXIT_CODE: 0`, `Output Summary:` with total coverage percentage.

---

### Phase 1 — Apply Fixes

- [x] [P1-T1] Apply Black formatting to `db_loader.py`: run `poetry run black src/invoice_etl/load/db_loader.py`.
  - Expected change: Two `text("""...""")` call sites are reformatted — the triple-quoted SQL strings are moved to new indented lines per Black's multi-line-arg convention. No logic changes.
  - Acceptance: `poetry run black --check src/invoice_etl/load/db_loader.py` exits 0.

- [x] [P1-T2] (Optional, low priority) Move `_PARTIAL_ROW_RE` and `_DATE_IN_LINE_RE` from inside `_merge_truncated_lines()` to module scope in `invoice_transformer.py`, alongside the other `_SOD_*_RE` constants.
  - Acceptance: Both names appear at module scope. All existing tests pass. `poetry run pyright` exits 0.

- [x] [P1-T3] (Optional, low priority) Remove `re.MULTILINE` flag from `_SOD_LINE_ITEM_RE` declaration in `invoice_transformer.py`.
  - Acceptance: `_SOD_LINE_ITEM_RE` no longer includes `re.MULTILINE`. All existing tests pass.

---

### Phase 2 — Final QC Loop

Run the full toolchain pass in the exact order below. If any step changes files or exits non-zero, restart from step 1.

- [x] [P2-T1] Run `poetry run black --check src tests` and record result at `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/qa-gates/remediation-qc-black.md`.
  - Acceptance: Exit code 0. File contains `Timestamp:`, `Command:`, `EXIT_CODE: 0`, `Output Summary: All files conform to Black formatting.`

- [x] [P2-T2] Run `poetry run ruff check src tests` and record result at `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/qa-gates/remediation-qc-ruff.md`.
  - Acceptance: Exit code 0. File contains `Timestamp:`, `Command:`, `EXIT_CODE: 0`, `Output Summary: All checks passed.`

- [x] [P2-T3] Run `poetry run pyright` and record result at `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/qa-gates/remediation-qc-pyright.md`.
  - Acceptance: Exit code 0. File contains `Timestamp:`, `Command:`, `EXIT_CODE: 0`, `Output Summary: 0 errors, 0 warnings, 0 informations.`

- [x] [P2-T4] Run `poetry run pytest --cov=invoice_etl --cov-report=term-missing` and record result at `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/qa-gates/remediation-qc-pytest.md`.
  - Acceptance: Exit code 0, 20/20 tests pass. Coverage ≥ 82%. File contains `Timestamp:`, `Command:`, `EXIT_CODE: 0`, `Output Summary:` with total coverage headline.

- [x] [P2-T5] Confirm all Phase 2 QC artifacts exist with correct fields and exit codes. If any step fails or changes files, restart the toolchain pass from P2-T1.
  - Acceptance: All four artifacts present. All exit codes 0.

---

### Phase 3 — Review Update

- [x] [P3-T1] Update `feature-audit.2026-04-30T15-39.md`: change AC #8 evaluation from PARTIAL to PASS; update Summary verdict from NEEDS REVISION to PASS; update the AC status summary.
  - Acceptance: `feature-audit.2026-04-30T15-39.md` shows AC #8 as PASS and overall verdict as PASS.

- [x] [P3-T2] Validate all three review artifacts with the MCP validator:
  - `validate_orchestration_artifacts` with `artifact_type: "policy-audit"` for `policy-audit.2026-04-30T15-39.md`.
  - `validate_orchestration_artifacts` with `artifact_type: "code-review"` for `code-review.2026-04-30T15-39.md`.
  - `validate_orchestration_artifacts` with `artifact_type: "feature-audit"` for `feature-audit.2026-04-30T15-39.md`.
  - Acceptance: All three validators return `ok: true`.
