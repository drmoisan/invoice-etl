# Code Review: excel-export-loader (#6)

---

**Review Date:** 2026-04-30
**Reviewer:** feature_code_review_agent
**Feature Folder:** `docs/features/active/2026-04-30-excel-export-loader-6`
**Feature Folder Selection Rule:** Folder suffix matches issue number and branch name `feature/excel-export-loader-6`.
**Base Branch:** `main`
**Head Branch:** `feature/excel-export-loader-6`
**Review Type:** Initial review (small-path reduced audit)

---

## Executive Summary

This review covers the `feature/excel-export-loader-6` branch against `main`. The change introduces `src/invoice_etl/load/excel_loader.py` (82 lines), modifies `src/invoice_etl/main.py` to add an `--output` CLI flag, adds 10 new tests across `tests/test_load.py` and `tests/test_main.py`, and registers `openpyxl ^3.1.5` in `pyproject.toml`. The implementation is minimal and correctly scoped: it does not modify the existing DB loader path or touch any unrelated modules.

All four toolchain gates pass (Black EXIT_CODE 0, Ruff EXIT_CODE 0, Pyright EXIT_CODE 0 with 0 errors, Pytest EXIT_CODE 0 with 35 passed, 94% coverage). The new `excel_loader.py` achieves 100% coverage. Implementation quality is consistent with the established patterns in the codebase.

**What changed:**
One new production module (`excel_loader.py`), one modified module (`main.py`), two modified test files, and one updated `pyproject.toml`. The DB load path is untouched; only an `if output == "excel": / else:` dispatch block was added in `run()`.

**Top 3 risks:**
1. `pr_context` artifacts are stale and reference a different branch; this is an operational artifact gap, not a code defect, but should be resolved before opening the PR.
2. `_make_captured_workbook` replaces `real_wb.save` by direct attribute assignment (`real_wb.save = mock_save`). This works correctly with the current version of `openpyxl` but would silently fail if `openpyxl` changed `Workbook.save` to a non-overridable descriptor. This is a low-probability risk.
3. `excel_loader.py` does not validate that `output_path` has a `.xlsx` extension. Callers could pass a path with an incorrect extension and `openpyxl` would still write valid xlsx bytes to it. This is a minor usability concern with no correctness impact.

**PR readiness recommendation:** **Go** — No blockers or major findings. The change is complete, policy-compliant, and toolchain-clean.

---

## Findings Table

| Severity | File | Location | Finding | Recommendation | Rationale | Evidence |
|---|---|---|---|---|---|---|
| Nit | `tests/test_load.py` | `_make_captured_workbook` | `real_wb.save` replaced by direct attribute assignment rather than `patch.object`. | Consider using `patch.object(real_wb, "save")` as a context manager inside each test for uniformity with the `openpyxl.Workbook` patch already used. | Direct attribute replacement on an instance is not technically prohibited, but `patch.object` is the established project pattern and restores the original on exit. | Direct inspection of `test_load.py` lines 83–90 |
| Nit | `src/invoice_etl/load/excel_loader.py` | `load_invoice_to_excel` | No validation that `output_path.suffix == ".xlsx"`. | No change required; the constraint note in `issue.md` does not mandate validation. Document as a known limitation if the function becomes part of a public API. | Callers could pass an extension-less path; `openpyxl` would still write valid data. No correctness defect. | Inspection of `excel_loader.py` lines 45–82 |
| Info | `artifacts/pr_context.summary.txt` | Entire file | Artifact references `feature/sod-invoice-ingestion-1`, not the current branch. | Run `drm-copilot: Collect PR Context` against `PRBaseBranch=main` before opening the PR. | Stale artifact does not affect code quality but will produce an inaccurate PR description. | `artifacts/pr_context.summary.txt` inspection |

No Blockers or Major findings.

---

## Implementation Audit

### Python implementation audit

#### What changed well

- `excel_loader.py` is clean and focused: module-level column constants separate schema from logic, the single public function has a complete Google-style docstring, and the file is 82 lines well within the 500-line limit.
- `OutputMode = Literal["db", "excel"]` in `main.py` allows Pyright strict mode to enforce exhaustive dispatch without a catch-all branch.
- The `cast(OutputMode, args.output)` call is accompanied by a justifying comment explaining why the cast is safe (`argparse choices` enforcement), satisfying the project suppression policy rationale requirement.
- The `assert ws_header is not None` sanity check for `wb.active` is appropriate per the general code change policy (assertions for internal invariants only). It prevents a spurious `None` branch in Pyright strict mode.

#### Typing and API notes

- All new functions, parameters, return types, module-level constants, and local variables are annotated. Pyright strict mode passes with 0 errors.
- `ws_items: Worksheet = wb.create_sheet(title="LineItems")` correctly narrows the return type from `Any` to `Worksheet` using an explicit annotation rather than a cast, which is the preferred approach.
- `model_dump(exclude={"line_items"})` returns `dict[str, Any]`; calling `.get(col)` on that dict is valid under strict mode because the result type is `Any`. This is acceptable and requires no suppression.

#### Error handling and logging

- `excel_loader.py` logs the output path at `INFO` level after a successful write, consistent with the `db_loader.py` logging pattern.
- No broad-catch exception handling was added. `openpyxl` errors propagate to the caller, which is correct for this I/O boundary module.
- `main.py` retains the existing pattern of logging at `INFO` for both the processing step and the post-load confirmation.

---

## Test Quality Audit

All 10 new tests are function-based `pytest` tests with type annotations and docstrings. No test touches the filesystem.

### Reviewed test and QA artifacts

- `tests/test_load.py` (6 new excel tests) — Covers `load_invoice_to_excel` return value, sheet names, header rows (Invoice and LineItems), data rows (one per line item), and `wb.save` invocation. Uses `patch.object(openpyxl, "Workbook", return_value=real_wb)` so the real workbook is populated and inspected without writing to disk.
- `tests/test_main.py` (4 new tests) — Covers `main()` routing of `--output excel` and `--output db` flags to `run()`, and `run()` dispatch to `load_invoice_to_excel` vs `load_invoice` with mutual-exclusion assertions.
- `evidence/qa-gates/final-qc-pytest.md` — 35 passed, 0 failed, 94% coverage, EXIT_CODE 0.
- `evidence/qa-gates/final-qc-coverage-threshold.md` — 94% ≥ 70% threshold, EXIT_CODE 0.

### Quality assessment prompts

- **Determinism:** No random values, time-dependent assertions, or uncontrolled external I/O. All dependencies are patched or replaced for every test.
- **Isolation:** Each test exercises exactly one observable behavior (one sheet name, one column header cell, one call assertion). There is no shared state between tests.
- **Speed:** 35 tests in 0.77s total. No slow operations.
- **Diagnostics:** `assert ws.cell(row=1, column=1).value == "invoice_number"` and `assert_called_once_with(...)` patterns produce precise, self-describing failure messages that immediately identify any regression.

---

## Security / Correctness Checks

| Check | Status | Evidence |
|---|---|---|
| No secrets in code | ✅ PASS | No credentials, tokens, or environment variable values embedded in any new or modified file. |
| No unsafe subprocess or command construction | ✅ PASS | No `subprocess`, `os.system`, or shell interpolation in any new code. |
| Input validation at boundaries | ✅ PASS | `argparse choices=["db", "excel"]` enforces valid input at the CLI boundary. The `cast` in `main()` is justified by that enforcement. No additional boundary is introduced. |
| Error handling remains explicit | ✅ PASS | No broad-catch blocks added. `excel_loader.py` allows `openpyxl` errors to propagate. |
| Configuration / path handling is safe | ✅ PASS | `output_path` is accepted as a typed `Path` argument and passed directly to `openpyxl`. No string interpolation or shell execution involved. |

---

## Research Log

No external research was required. The `openpyxl` API usage (`Workbook()`, `wb.active`, `wb.create_sheet`, `ws.append`, `wb.save`) is standard and consistent with the library's documented public API. The `issue.md` specified `openpyxl` as the required library.

---

## Verdict

The `feature/excel-export-loader-6` branch delivers a clean, minimal implementation that satisfies all six acceptance criteria. The toolchain is clean across all four gates. No blockers or major findings were identified. The two nit-level findings are not blocking; they reflect patterns that could be improved in a future pass but do not affect correctness or policy compliance.

The change is ready for the normal PR flow. Before opening the PR, the operator should refresh the `artifacts/pr_context` artifacts against `PRBaseBranch=main` to ensure an accurate PR description is generated.
