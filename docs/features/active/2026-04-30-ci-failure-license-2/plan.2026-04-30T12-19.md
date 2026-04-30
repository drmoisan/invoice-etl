# 2026-04-30-ci-failure-license (Plan)

- **Issue:** #2
- **Issue URL:** https://github.com/drmoisan/invoice-etl/issues/2
- **Parent (optional):** none
- **Owner:** drmoisan
- **Last Updated:** 2026-04-30T12-32
- **Status:** Completed
- **Work Mode:** minor-audit
- **Version:** 0.1

![Completed](https://img.shields.io/badge/Status-Completed-brightgreen)

---

## Overview

Add a `LICENSE` file (MIT, 2026 Dan Moisan) to the repository root and declare `license = "MIT"` in `pyproject.toml` to resolve the CI run #2 `Documentation Validation` job failure. The CI step `Check for LICENSE file` in `.github/workflows/ci.yml` exits with code 1 when no `LICENSE` file is present.

**Scope:** Repository artifact changes only. No Python source code under `src/` or `tests/` is modified.

**Fail-closed evidence rule:** Baseline and QA artifact tasks are required even for non-code changes. If any required artifact is missing, the audit verdict is BLOCKED, never PASS.

**Evidence accounting rule:** Each evidence-producing task records the exact artifact path. Do not mark any task complete without the artifact present at that path.

---

### Phase 0 — Baseline Capture

- [x] [P0-T1] Verify `docs/features/active/2026-04-30-ci-failure-license-2/issue.md` contains a `## Acceptance Criteria` section by running `grep -c '## Acceptance Criteria' docs/features/active/2026-04-30-ci-failure-license-2/issue.md`; the command must exit with code 0 and output `1`.
  - Acceptance: `grep -c '## Acceptance Criteria' docs/features/active/2026-04-30-ci-failure-license-2/issue.md` exits with code 0 and prints `1`.

- [x] [P0-T2] Read and record policy compliance order by reading `.github/instructions/general-code-change.instructions.md` and `.github/instructions/python-code-change.instructions.md`; write confirmation to `docs/features/active/2026-04-30-ci-failure-license-2/evidence/baseline/phase0-instructions-read.md` using the exact format:
  ```
  Timestamp: <ISO-8601>
  Policy Order:
    1. .github/instructions/general-code-change.instructions.md
    2. .github/instructions/python-code-change.instructions.md
  ```
  - Acceptance: File exists and contains a non-empty `Timestamp:` field and a `Policy Order:` field listing both file paths.

- [x] [P0-T3] Record the current branch and HEAD commit SHA by running `git rev-parse HEAD` and `git branch --show-current`; write both values to `docs/features/active/2026-04-30-ci-failure-license-2/evidence/baseline/baseline-branch.md`.
  - Acceptance: File exists and contains a non-empty commit SHA and branch name.

- [x] [P0-T4] Capture Black baseline by running `poetry run black --check src tests` and writing to `docs/features/active/2026-04-30-ci-failure-license-2/evidence/baseline/baseline-black.md` using the exact format:
  ```
  Timestamp: <ISO-8601>
  Command: poetry run black --check src tests
  EXIT_CODE: <int>
  Output Summary: <first 10 lines of stdout+stderr>
  ```
  - Acceptance: File exists and contains non-empty `Timestamp:`, `Command:`, `EXIT_CODE:`, and `Output Summary:` fields.

- [x] [P0-T5] Capture Ruff baseline by running `poetry run ruff check src tests` and writing to `docs/features/active/2026-04-30-ci-failure-license-2/evidence/baseline/baseline-ruff.md` using the exact format:
  ```
  Timestamp: <ISO-8601>
  Command: poetry run ruff check src tests
  EXIT_CODE: <int>
  Output Summary: <first 10 lines of stdout+stderr>
  ```
  - Acceptance: File exists and contains non-empty `Timestamp:`, `Command:`, `EXIT_CODE:`, and `Output Summary:` fields.

- [x] [P0-T6] Capture Pyright baseline by running `poetry run pyright` and writing to `docs/features/active/2026-04-30-ci-failure-license-2/evidence/baseline/baseline-pyright.md` using the exact format:
  ```
  Timestamp: <ISO-8601>
  Command: poetry run pyright
  EXIT_CODE: <int>
  Output Summary: <first 10 lines of stdout+stderr>
  ```
  - Acceptance: File exists and contains non-empty `Timestamp:`, `Command:`, `EXIT_CODE:`, and `Output Summary:` fields.

- [x] [P0-T7] Capture Pytest baseline by running `poetry run pytest --cov=invoice_etl --cov-report=term-missing` and writing to `docs/features/active/2026-04-30-ci-failure-license-2/evidence/baseline/baseline-pytest.md` using the exact format:
  ```
  Timestamp: <ISO-8601>
  Command: poetry run pytest --cov=invoice_etl --cov-report=term-missing
  EXIT_CODE: <int>
  Output Summary: <first 10 lines of stdout+stderr>
  Coverage: <numeric total-coverage percentage, e.g. "82%">
  ```
  - Acceptance: File exists and contains non-empty `Timestamp:`, `Command:`, `EXIT_CODE:`, `Output Summary:`, and `Coverage:` fields; `Coverage:` value is a numeric percentage string.

- [x] [P0-T8] Verify the `LICENSE` file is absent at the repository root by confirming `LICENSE` does not exist; record the result as a one-line entry in `docs/features/active/2026-04-30-ci-failure-license-2/evidence/baseline/baseline-license-absent.md`.
  - Acceptance: File exists and records that `LICENSE` was not found prior to the fix.

- [x] [P0-T9] Verify the `[tool.poetry]` section of `pyproject.toml` has no `license` field; record the current `[tool.poetry]` block verbatim in `docs/features/active/2026-04-30-ci-failure-license-2/evidence/baseline/baseline-pyproject-poetry-block.md`.
  - Acceptance: File exists and the recorded block contains no `license =` line.

---

### Phase 1 — Handoff: Small-Path Fix

- [x] [P1-T1] Create the file `LICENSE` at the repository root (`c:\Users\DanMoisan\repos\invoice-etl\LICENSE`) with the following exact content (MIT license, year 2026, holder "Dan Moisan"):

  ```
  MIT License

  Copyright (c) 2026 Dan Moisan

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
  ```

  - Acceptance: `LICENSE` exists at the repository root; `cat LICENSE` outputs the MIT license text with copyright holder "Dan Moisan" and year "2026".

- [x] [P1-T2] Add `license = "MIT"` to the `[tool.poetry]` section of `pyproject.toml`, inserted on the line immediately after `readme = "README.md"`. The resulting block must be:

  ```toml
  [tool.poetry]
  name = "invoice-etl"
  version = "0.1.0"
  description = "ETL pipeline for extracting transaction data from customer invoice PDFs into PostgreSQL."
  authors = []
  license = "MIT"
  readme = "README.md"
  packages = [{ include = "invoice_etl", from = "src" }]
  ```

  - Acceptance: `grep -n 'license = "MIT"' pyproject.toml` exits with code 0 and prints a matching line within the `[tool.poetry]` block.

- [x] [P1-T3] Verify the CI `Check for LICENSE file` step logic passes locally by running `if [ ! -f LICENSE ]; then echo "MISSING"; exit 1; fi && echo "PRESENT"` (or PowerShell equivalent: `if (-not (Test-Path LICENSE)) { throw "MISSING" } else { "PRESENT" }`) from the repository root; write the result to `docs/features/active/2026-04-30-ci-failure-license-2/evidence/baseline/verification-license-present.md`.
  - Acceptance: File records `PRESENT` and exit code 0.

- [x] [P1-T4] Verify `poetry check` passes after the `pyproject.toml` change by running `poetry check` and writing the full output (stdout + exit code) to `docs/features/active/2026-04-30-ci-failure-license-2/evidence/baseline/verification-poetry-check.md`.
  - Acceptance: File contains `EXIT_CODE: 0` and output includes `All checks passed` or equivalent success message.

---

### Phase 2 — Final QC Loop

Run the full Python toolchain in order. If any step changes files or fails, fix the issue and restart from the first step. Stop only when all four steps pass in a single uninterrupted pass.

- [x] [P2-T1] Run `poetry run black --check src tests`; write to `docs/features/active/2026-04-30-ci-failure-license-2/evidence/qa-gates/final-qc-black.md` using the exact format:
  ```
  Timestamp: <ISO-8601>
  Command: poetry run black --check src tests
  EXIT_CODE: <int>
  Output Summary: <first 10 lines of stdout+stderr>
  ```
  - Acceptance: File contains non-empty `Timestamp:`, `Command:`, `EXIT_CODE: 0`, and `Output Summary:` fields. If `EXIT_CODE` is non-zero, reformat with `poetry run black src tests` and restart from [P2-T1].

- [x] [P2-T2] Run `poetry run ruff check src tests`; write to `docs/features/active/2026-04-30-ci-failure-license-2/evidence/qa-gates/final-qc-ruff.md` using the exact format:
  ```
  Timestamp: <ISO-8601>
  Command: poetry run ruff check src tests
  EXIT_CODE: <int>
  Output Summary: <first 10 lines of stdout+stderr>
  ```
  - Acceptance: File contains non-empty `Timestamp:`, `Command:`, `EXIT_CODE: 0`, and `Output Summary:` fields. If `EXIT_CODE` is non-zero, fix all reported issues and restart from [P2-T1].

- [x] [P2-T3] Run `poetry run pyright`; write to `docs/features/active/2026-04-30-ci-failure-license-2/evidence/qa-gates/final-qc-pyright.md` using the exact format:
  ```
  Timestamp: <ISO-8601>
  Command: poetry run pyright
  EXIT_CODE: <int>
  Output Summary: <first 10 lines of stdout+stderr>
  ```
  - Acceptance: File contains non-empty `Timestamp:`, `Command:`, `EXIT_CODE: 0`, and `Output Summary:` fields. If `EXIT_CODE` is non-zero, fix all reported type errors and restart from [P2-T1].

- [x] [P2-T4] Run `poetry run pytest --cov=invoice_etl --cov-report=term-missing`; write to `docs/features/active/2026-04-30-ci-failure-license-2/evidence/qa-gates/final-qc-pytest.md` using the exact format:
  ```
  Timestamp: <ISO-8601>
  Command: poetry run pytest --cov=invoice_etl --cov-report=term-missing
  EXIT_CODE: <int>
  Output Summary: <first 10 lines of stdout+stderr>
  Coverage: <numeric total-coverage percentage, e.g. "82%">
  ```
  - Acceptance: File contains non-empty `Timestamp:`, `Command:`, `EXIT_CODE: 0`, `Output Summary:`, and `Coverage:` fields; `Coverage:` is a numeric percentage string. If `EXIT_CODE` is non-zero, fix the failing test and restart from [P2-T1].

- [x] [P2-T5] Run `poetry run coverage report --fail-under=70`; write to `docs/features/active/2026-04-30-ci-failure-license-2/evidence/qa-gates/final-qc-coverage-threshold.md` using the exact format:
  ```
  Timestamp: <ISO-8601>
  Command: poetry run coverage report --fail-under=70
  EXIT_CODE: <int>
  Output Summary: <first 10 lines of stdout+stderr>
  ```
  - Acceptance: File contains non-empty `Timestamp:`, `Command:`, `EXIT_CODE: 0`, and `Output Summary:` fields. If coverage is below 70 %, add tests and restart from [P2-T1].

- [x] [P2-T6] Confirm all four toolchain steps passed in a single uninterrupted pass by verifying the five QA gate artifacts produced in [P2-T1] through [P2-T5] all contain `EXIT_CODE: 0`; record the summary in `docs/features/active/2026-04-30-ci-failure-license-2/evidence/qa-gates/final-qc-summary.md` with the format:

  ```
  Timestamp: <ISO-8601>
  Black:    PASS (EXIT_CODE: 0)
  Ruff:     PASS (EXIT_CODE: 0)
  Pyright:  PASS (EXIT_CODE: 0)
  Pytest:   PASS (EXIT_CODE: 0)
  Coverage: PASS (EXIT_CODE: 0)
  ```

  - Acceptance: `final-qc-summary.md` exists and all five lines show `PASS (EXIT_CODE: 0)`.

- [x] [P2-T7] Confirm no regressions against the Phase 0 baselines by verifying that the Pytest `EXIT_CODE` in `final-qc-pytest.md` equals the `EXIT_CODE` recorded in `baseline-pytest.md`, and that the `Coverage:` value in `final-qc-pytest.md` is greater than or equal to the `Coverage:` value in `baseline-pytest.md`.
  - Acceptance: `baseline-pytest.md` EXIT_CODE equals `final-qc-pytest.md` EXIT_CODE, both are 0, and `final-qc-pytest.md` Coverage percentage is ≥ `baseline-pytest.md` Coverage percentage.
