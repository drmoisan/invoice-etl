# ci-failure-license (Issue #2)

- Date captured: 2026-04-30
- Author: Dan Moisan
- Status: Promoted -> docs/features/active/ci-failure-license/ (Issue #2)

> Automation note: Keep the section headings below unchanged; the promotion tooling maps each of them into the GitHub bug issue template.

- Issue: #2
- Issue URL: https://github.com/drmoisan/invoice-etl/issues/2
- Last Updated: 2026-04-30
- Work Mode: minor-audit

## Summary

CI run #2 on the `main` branch failed in the **Documentation Validation** job because the repository had no `LICENSE` file. The `docs-validation` workflow step `Check for LICENSE file` exited with code 1.

## Environment

- OS/version: ubuntu-latest (GitHub Actions runner)
- Python version: N/A (failure occurred before Python steps)
- Command/flags used: `if [ ! -f LICENSE ]; then echo "ERROR: LICENSE file is missing"; exit 1; fi`
- Data source or fixture: N/A

## Steps to Reproduce

1. Push any commit to the `main` branch without a `LICENSE` file present in the repository root.
2. Observe the **Documentation Validation** job in the CI workflow (`.github/workflows/ci.yml`).
3. Step 4 "Check for LICENSE file" exits with code 1.

## Expected Behavior

The `Check for LICENSE file` step passes because a `LICENSE` file exists in the repository root, and the **Documentation Validation** job completes successfully.

## Actual Behavior

The step reported the following error and the job concluded as `failure`:

```
ERROR: LICENSE file is missing
```

CI run #2 (run ID `25172228504`, commit `(chore): recommended extensions`, branch `main`, 2026-04-30T14:50:35Z) failed. The **Documentation Validation** job and the **Build Package** job both concluded as `failure`.

## Logs / Screenshots

- [x] Attached minimal logs or screenshot
- Snippet:
  ```
  Run if [ ! -f LICENSE ]; then
    echo "ERROR: LICENSE file is missing"
    exit 1
  fi
  ERROR: LICENSE file is missing
  Error: Process completed with exit code 1.
  ```

## Impact / Severity

- [x] Blocker
- [ ] High
- [ ] Medium
- [ ] Low

Every push to `main` fails CI until a `LICENSE` file is present. Merging any branch into `main` is blocked.

## Suspected Cause / Notes

The `docs-validation` job in `.github/workflows/ci.yml` requires a `LICENSE` file at the repository root. No `LICENSE` file was ever committed to the repository, and `pyproject.toml` had no `license` field either.

Relevant file: `.github/workflows/ci.yml`, job `docs-validation`, step "Check for LICENSE file".

## Proposed Fix / Validation Ideas

- [x] Unit coverage areas — No unit test required; this is a repository artifact check.
- [x] Integration scenario to retest — Push a commit after adding `LICENSE`; confirm the **Documentation Validation** job passes.
- [x] Manual verification steps:
  1. Add an MIT `LICENSE` file to the repository root.
  2. Add `license = "MIT"` to the `[tool.poetry]` section of `pyproject.toml`.
  3. Commit and push; verify CI run passes the `Check for LICENSE file` step.

**Status**: Fix applied on 2026-04-30. `LICENSE` (MIT, 2026 Dan Moisan) created and `license = "MIT"` added to `pyproject.toml`. Awaiting CI confirmation on next push.
## Acceptance Criteria

- [x] AC-1: `LICENSE` file exists at the repository root and contains MIT license text with copyright year 2026 and holder "Dan Moisan"; verified by `cat LICENSE | grep -q 'MIT License'` exiting with code 0.
- [x] AC-2: `pyproject.toml` `[tool.poetry]` section contains `license = "MIT"`; verified by `grep -n 'license = "MIT"' pyproject.toml` exiting with code 0.
- [x] AC-3: CI step logic `if [ ! -f LICENSE ]; then echo "ERROR: LICENSE file is missing"; exit 1; fi` exits with code 0 when run from the repository root.
- [x] AC-4: `poetry check` exits with code 0 after the `pyproject.toml` change.
- [x] AC-5: Python toolchain — `poetry run black --check src tests`, `poetry run ruff check src tests`, `poetry run pyright`, and `poetry run pytest --cov=invoice_etl --cov-report=term-missing` — all exit with code 0 in a single uninterrupted pass, and coverage meets the `--fail-under=70` threshold.
## Next Step

- [ ] Promote to GitHub issue (bug-report template)
- [x] Move to active fix folder / branch