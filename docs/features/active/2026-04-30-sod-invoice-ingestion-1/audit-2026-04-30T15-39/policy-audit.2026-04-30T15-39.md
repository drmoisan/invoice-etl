# Policy Compliance Audit: SOD Invoice Ingestion (Issue #1)

---

**Audit Date:** 2026-04-30
**Code Under Test:**
- `src/invoice_etl/models/invoice.py`
- `src/invoice_etl/transform/invoice_transformer.py`
- `src/invoice_etl/load/db_loader.py`
- `docker/init.sql`
- `tests/test_transform.py`
- `tests/test_load.py`

**Coverage Metrics:**

| Language | Files Changed | Tests | Test Result | Baseline Coverage | Post-Change Coverage | New Code Coverage |
|----------|--------------|-------|-------------|-------------------|---------------------|-------------------|
| Python | 4 src files, 2 test files | 20 tests | ❌ 20 pass, 0 fail (pytest ✅; Black ❌) | 70% lines | 82% lines | 93% (invoice_transformer.py) |

### Coverage Evidence Checklist

- Python baseline coverage artifact: `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/baseline/baseline-pytest.md`
- Python post-change coverage artifact: live run `poetry run pytest --cov=invoice_etl --cov-report=term-missing` — 82% as of 2026-04-30T15:39
- TypeScript baseline coverage artifact: N/A - out of scope
- TypeScript post-change coverage artifact: N/A - out of scope
- PowerShell baseline coverage artifact: N/A - out of scope
- PowerShell post-change coverage artifact: N/A - out of scope
- Per-language comparison summary: Python: Baseline 70% → Post-change 82% (+12%). New/changed-code coverage: `invoice_transformer.py` 93% (100/107 stmts); `db_loader.py` 72% (pre-existing gap, new SQL column code covered). See §5.

---

## Executive Summary

This audit evaluated the SOD Invoice Ingestion feature branch against the following policy documents:

**Policy documents evaluated:**
- ❌ `general-code-change.instructions.md` — PARTIAL (Black non-compliance in `db_loader.py`)
- ✅ `general-unit-test.instructions.md` — PASS
- ❌ `python-code-change.instructions.md` — PARTIAL (Black non-compliance)
- ✅ `python-unit-test.instructions.md` — PASS
- ✅ `python-suppressions.instructions.md` — PASS
- ✅ `self-explanatory-code-commenting.instructions.md` — PASS

**Overall compliance status: PARTIAL — remediation required.**

The implementation is substantively correct and well-structured. All 20 tests pass. Ruff, Pyright strict, and pytest pass cleanly. However, `poetry run black --check src tests` exits with code 1 because `db_loader.py` requires Black reformatting of its multi-line `text(...)` call syntax. This is a hard toolchain requirement under the Python code change policy.

Coverage improved from 70% (baseline) to 82% post-change, exceeding the 80% minimum. The `invoice_transformer.py` module reaches 93% on the new SOD parsing logic. The `_get_engine()` coverage gap in `db_loader.py` (72%) is pre-existing and unchanged from baseline.

**Temporary artifacts cleanup:**
- ✅ No temporary scripts were created during development.

---

## 1. General Unit Test Policy Compliance

### 1.1 Core Principles

| Requirement | Status | Evidence |
|------------|--------|----------|
| **Independence** — Tests run in any order | ✅ PASS | All 20 tests use local inline fixtures and `MagicMock` objects. No shared mutable state between tests. Execution order is arbitrary. |
| **Isolation** — Each test targets single behavior | ✅ PASS | Each test function exercises one function or one assertion about a single behavior. Tests for `_parse_sod_header`, `_parse_sod_line_item`, `_merge_truncated_lines`, and `load_invoice` are distinct. |
| **Fast Execution** — Tests complete quickly | ✅ PASS | 20 tests completed in 0.57 seconds. No I/O, no network, no DB. |
| **Determinism** — Consistent results | ✅ PASS | All inputs are inline string literals or `MagicMock` objects. No time-dependent logic, no randomness, no filesystem access. |
| **Readability & Maintainability** — Clear structure | ✅ PASS | Tests follow `test_<subject>_<scenario>` naming. Docstrings are present on SOD-specific tests. Fixtures are defined as module-level constants (`_SOD_HEADER_TEXT`, `_SOD_LINE_ITEM_ROW`). |

### 1.2 Coverage and Scenarios

| Requirement | Status | Evidence |
|------------|--------|----------|
| **Baseline Coverage Documented** | ✅ PASS | Baseline: 70% lines. Command: `poetry run pytest --cov=invoice_etl --cov-report=term-missing`. Timestamp: 2026-04-30T11:34Z. Artifact: `evidence/baseline/baseline-pytest.md`. |
| **No Coverage Regression** | ✅ PASS | Post-change: 82% lines (+12%). `db_loader.py`: 69% → 72% (+3%). `invoice_transformer.py`: 91% → 93% (+2%). No module decreased in coverage. |
| **New Code Coverage ≥90%** | ✅ PASS | `invoice_transformer.py` (primary new code): **93%** (100/107 stmts). `db_loader.py` new SQL columns tested via `test_load_passes_customer_number_to_invoices_insert` and `test_load_passes_new_line_item_fields_to_insert`. `db_loader.py` module total: **72%** (21/29 stmts); uncovered lines 18–24, 34 are pre-existing (`_get_engine()` env-var block, unchanged from baseline). New SQL insert paths are covered. |
| **Comprehensive Coverage** | ✅ PASS | `_parse_sod_header()`: 3 direct tests. `_parse_sod_line_item()`: 2 tests (match + no-match). `_merge_truncated_lines()`: 2 tests. `_transform_sod_pages()` (via `transform_pages`): 2 integration tests. `load_invoice()` with new fields: 2 tests. |
| **Positive Flows** — Valid inputs | ✅ PASS | `test_sod_line_item_parses_all_nine_fields`, `test_sod_header_parses_invoice_number`, `test_sod_header_parses_customer_number`, `test_sod_header_parses_invoice_date`, `test_load_passes_customer_number_to_invoices_insert`, `test_load_passes_new_line_item_fields_to_insert`. |
| **Negative Flows** — Invalid inputs | ✅ PASS | `test_sod_line_item_returns_none_for_non_matching_line` (header row returns None). `test_load_returns_minus_one_on_duplicate` (ON CONFLICT path). |
| **Edge Cases** — Boundary conditions | ✅ PASS | `test_merge_truncated_lines_merges_split_row` (truncated row at page boundary). `test_merge_truncated_lines_preserves_complete_rows` (complete rows unmodified). `test_transform_pages_non_sod_format_is_unchanged` (generic path regression). |
| **Error Handling** — Error paths | ✅ PASS | `_parse_sod_line_item` returns `None` for non-matching lines (validated by test). `_parse_decimal` returns `None` on `InvalidOperation` (covered by existing usage paths). |
| **Concurrency** — If applicable | N/A | No concurrent behavior in scope. |
| **State Transitions** — If applicable | N/A | No stateful components introduced. |

### 1.2.1 Per-Language Coverage Comparison

- Python: Baseline: 70% lines -> Post-change: 82% lines. Change: +12% lines. New/changed-code coverage: 93%. Disposition: PASS. Evidence: `evidence/baseline/baseline-pytest.md`; live run 2026-04-30T15:39.
- TypeScript: N/A - out of scope.
- PowerShell: N/A - out of scope.

### 1.3 Test Structure and Diagnostics

| Requirement | Status | Evidence |
|------------|--------|----------|
| **Clear Failure Messages** | ✅ PASS | Assertions use `assert li is not None`, `assert li.item == "01553"`, `assert mock_conn.execute.call_args_list[0].args[1]["customer_number"] == "081997"`. Failures identify field and expected value. |
| **Arrange-Act-Assert Pattern** | ✅ PASS | All tests arrange fixtures/mocks, invoke the function under test, then assert outcomes. No side-effect-heavy setup. |
| **Document Intent** | ✅ PASS | SOD-specific tests carry one-line docstrings stating scenario and expected outcome. Generic path tests follow self-documenting names. |

### 1.4 External Dependencies and Environment

| Requirement | Status | Evidence |
|------------|--------|----------|
| **Avoid External Dependencies** | ✅ PASS | No database connections, filesystem reads, network calls, or subprocesses in tests. `load_invoice` DB calls are fully mocked. |
| **Use Mocks/Stubs** | ✅ PASS | `test_load.py` uses `MagicMock` for `Engine`, `Connection`, and `Result`. Mock engine is injected via the `engine` parameter, not patched globally. |
| **Environment Stability** | ✅ PASS | No environment variables required. No temporary files created or read. No global state mutation. |

### 1.5 Policy Audit Requirement

| Requirement | Status | Evidence |
|------------|--------|----------|
| **Pre-submission Review** | ✅ PASS | This document constitutes the required policy review for this feature branch. |

---

## 2. General Code Change Policy Compliance

### 2.1 Before Making Changes

| Requirement | Status | Evidence |
|------------|--------|----------|
| **Clarify the objective** | ✅ PASS | Feature tracked in `issue.md` (Issue #1). Objective: add SOD invoice parsing and persist new fields. |
| **Read existing change plans** | ✅ PASS | `plan.2026-04-30T11-01.md` present in feature folder. |
| **Document the plan** | ✅ PASS | `plan.2026-04-30T11-01.md` and `spec.md` document the implementation approach. |

### 2.2 Design Principles

| Requirement | Status | Evidence |
|------------|--------|----------|
| **Simplicity first** | ✅ PASS | SOD parsing uses regex and string splitting directly. No unnecessary abstraction layers. |
| **Reusability** | ✅ PASS | `_parse_decimal` is a shared helper used across multiple parsers. `_parse_sod_header`, `_merge_truncated_lines`, and `_parse_sod_line_item` are focused single-responsibility helpers. |
| **Extensibility** | ✅ PASS | `transform_pages()` uses format detection to dispatch to `_transform_sod_pages()`. New formats can be added by extending the dispatch logic without changing the public signature. |
| **Separation of concerns** | ✅ PASS | `invoice_transformer.py` is pure parsing logic with no I/O. `db_loader.py` handles all persistence. `models/invoice.py` defines data contracts. |

### 2.3 Classes, Functions, and APIs

| Requirement | Status | Evidence |
|------------|--------|----------|
| **Classes for domain concepts** | ✅ PASS | `LineItem` and `Invoice` are Pydantic `BaseModel` classes carrying domain data and validation. |
| **Functions for small pure helpers** | ✅ PASS | `_parse_sod_header`, `_parse_sod_line_item`, `_merge_truncated_lines`, `_parse_decimal` are all stateless pure functions. |
| **Interfaces and contracts** | ✅ PASS | `_SodHeader` TypedDict provides a typed return contract for `_parse_sod_header`. |

### 2.4 Error Handling, Logging, and Contracts

| Requirement | Status | Evidence |
|------------|--------|----------|
| **Fail fast and explicitly** | ✅ PASS | `_parse_sod_line_item` returns `None` for non-matching lines. `_parse_decimal` returns `None` on parse failure. Both callers propagate `None` safely. |
| **Logging** | ✅ PASS | `db_loader.py` logs at `WARNING` for duplicates and `INFO` for successful loads. `logger = logging.getLogger(__name__)` used. |
| **Contracts / invariants** | ✅ PASS | `_SodHeader` TypedDict enforces return structure. Pydantic models validate field types at instantiation. |

### 2.5 Module and File Structure

| Requirement | Status | Evidence |
|------------|--------|----------|
| **Cohesive modules** | ✅ PASS | Each module has a single clear purpose. `invoice_transformer.py` handles parsing; `db_loader.py` handles persistence; `invoice.py` defines models. |
| **File line limits (≤500 lines)** | ✅ PASS | `invoice_transformer.py`: ~340 lines. `db_loader.py`: ~80 lines. `invoice.py`: ~100 lines. `tests/test_transform.py`: ~160 lines. `tests/test_load.py`: ~80 lines. All within limit. |
| **Public vs internal** | ✅ PASS | Only `transform_pages()` and `load_invoice()` are public. All SOD helpers are `_`-prefixed private functions. |
| **Imports / dependencies** | ✅ PASS | No new third-party dependencies introduced. All imports are from stdlib, pydantic, and sqlalchemy (existing deps). |

### 2.6 Naming, Docs, and Comments

| Requirement | Status | Evidence |
|------------|--------|----------|
| **Descriptive naming** | ✅ PASS | `_parse_sod_header`, `_merge_truncated_lines`, `_parse_sod_line_item`, `_transform_sod_pages` are all clearly named by what they do. Regex constants follow `_SOD_<FIELD>_RE` pattern. |
| **Docstrings on public classes/methods** | ✅ PASS | Every function and class has a complete docstring including Args, Returns, and behavior description. `_SodHeader` TypedDict has field-level documentation. See §3.2 for Python-specific detail. |
| **Intent-level comments** | ✅ PASS | Inline comments explain: regex group semantics in `_SOD_LINE_ITEM_RE`, branching logic in `_merge_truncated_lines`, and parsing strategy in `_parse_sod_header`. |

### 2.7 Performance, I/O, and Dependencies

| Requirement | Status | Evidence |
|------------|--------|----------|
| **Performance** | ✅ PASS | Parsing is single-pass per page. No nested quadratic loops over large data. |
| **I/O boundaries** | ✅ PASS | Parsing logic (`invoice_transformer.py`) is pure — no disk/network/DB access. All I/O is in `db_loader.py` and `pdf_extractor.py`. |
| **Dependencies** | ✅ PASS | No new third-party packages introduced. Existing stdlib (`re`, `datetime`, `decimal`) and project deps only. |

### 2.8 After Making Changes — Toolchain

| Step | Status | Command | Evidence |
|------|--------|---------|----------|
| **Black formatting** | ❌ FAIL | `poetry run black --check src tests` | Exit code 1. `db_loader.py` would be reformatted. Black requires `text(\n    """..."""\n)` wrapping for multi-line string args. See §7 for diff. |
| **Ruff linting** | ✅ PASS | `poetry run ruff check src tests` | Exit code 0. All checks passed. |
| **Pyright type check** | ✅ PASS | `poetry run pyright` | Exit code 0. 0 errors, 0 warnings, 0 informations. |
| **pytest** | ✅ PASS | `poetry run pytest --cov=invoice_etl --cov-report=term-missing` | Exit code 0. 20/20 passed. 82% coverage. |

---

## 3. Language-Specific Code Change Policy Compliance (Python)

### 3.1 Tooling and Baseline

| Requirement | Status | Evidence |
|------------|--------|----------|
| **Black** — All code formatted | ❌ FAIL | `poetry run black --check src tests` exits 1. `db_loader.py` requires reformatting. Two `text("""...""")` call sites need Black's wrapping convention applied. Diff documented in §7. |
| **Ruff** — No lint errors | ✅ PASS | `poetry run ruff check src tests` exits 0. |
| **Pyright** — No type errors | ✅ PASS | `poetry run pyright` exits 0. 0 errors, 0 warnings. |

### 3.2 Python Design and Typing

| Requirement | Status | Evidence |
|------------|--------|----------|
| **Strong typing by default** | ✅ PASS | All functions annotated with parameter types and return types. `_SodHeader` TypedDict used for structured return value. `list[str]`, `list[LineItem]`, `Decimal | None` used throughout. |
| **Dataclasses and value objects** | ✅ PASS | `LineItem` and `Invoice` are Pydantic `BaseModel` instances. `_SodHeader` is a `TypedDict` for typed dict returns — appropriate choice for a private helper return structure. |
| **Protocols and ABCs** | N/A | No new protocol surface required. Single implementation for each new function. |
| **Utility code** | ✅ PASS | Helper functions are module-level rather than static-method classes. |

### 3.3 Suppression Compliance

| Requirement | Status | Evidence |
|------------|--------|----------|
| **`# type: ignore` suppressions authorized** | ✅ PASS | Three `# type: ignore[reportPrivateUsage]` suppressions in `tests/test_transform.py` for `_merge_truncated_lines`, `_parse_sod_header`, `_parse_sod_line_item`. Each carries a justification comment: `# plan requires testing private SOD helpers directly`. Per repo memory, `reportPrivateUsage` suppression with justification comment is the pre-authorized pattern for testing private helpers under Pyright strict mode. |
| **No unauthorized `# noqa` suppressions** | ✅ PASS | No `# noqa` suppressions present in changed files. |

---

## 4. Language-Specific Unit Test Policy Compliance (Python)

| Requirement | Status | Evidence |
|------------|--------|----------|
| **Pytest as test runner** | ✅ PASS | `pytest` used exclusively. `pyproject.toml` configures `testpaths = ["tests"]`. |
| **Focused unit tests** | ✅ PASS | Each test function exercises a single function or a single behavior within that function. |
| **Mocking used sparingly** | ✅ PASS | `MagicMock` used only for `Engine`/`Connection`/`Result` in `test_load.py`. All transform tests use real code paths with inline fixtures. |
| **Test organization mirrors production code** | ✅ PASS | `tests/test_transform.py` tests `invoice_transformer.py`. `tests/test_load.py` tests `db_loader.py`. |
| **Fixtures narrow in scope** | ✅ PASS | No `pytest.fixture` functions introduced. Module-level constants serve as shared fixture data. |
| **Descriptive test names** | ✅ PASS | `test_sod_header_parses_invoice_number`, `test_sod_line_item_parses_all_nine_fields`, `test_merge_truncated_lines_merges_split_row`, etc. |

---

## 5. Test Coverage Detail

| Module | Baseline | Post-Change | Delta | Uncovered Lines | Pre-existing? |
|--------|---------|------------|-------|-----------------|---------------|
| `invoice_etl/__init__.py` | 100% | 100% | 0% | none | — |
| `invoice_etl/extract/pdf_extractor.py` | 100% | 100% | 0% | none | — |
| `invoice_etl/load/db_loader.py` | 69% | 72% | +3% | 18–24, 34 | ✅ Yes (baseline had same lines) |
| `invoice_etl/main.py` | 0% | 0% | 0% | 3–43 | ✅ Yes |
| `invoice_etl/models/invoice.py` | 100% | 100% | 0% | none | — |
| `invoice_etl/transform/invoice_transformer.py` | 91% | 93% | +2% | 92–93, 144, 156, 198–199, 320 | Partial (new uncovered are minor branches) |
| **TOTAL** | **70%** | **82%** | **+12%** | | |

**Coverage threshold policy:** Repository-wide ≥ 80% — **MET** (82%).

**New-code coverage note:**
- `invoice_transformer.py` new SOD parsing logic: 93% statement coverage. PASS for ≥90% new code target.
- `db_loader.py` new SQL columns: The new `customer_number` and five `line_items` columns are exercised by `test_load_passes_customer_number_to_invoices_insert` and `test_load_passes_new_line_item_fields_to_insert`. The module-level 72% gap is attributable entirely to the pre-existing `_get_engine()` body (lines 18–24) and the `if engine is None: engine = _get_engine()` branch (line 34), both untouched by this PR.

---

## 6. Test Execution Metrics

| Metric | Value |
|--------|-------|
| Test runner | pytest 8.4.2 |
| Tests collected | 20 |
| Tests passed | 20 |
| Tests failed | 0 |
| Execution time | 0.57 seconds |
| Coverage source | `invoice_etl` |
| Total line coverage | 82% |
| Command | `poetry run pytest --cov=invoice_etl --cov-report=term-missing` |
| Run timestamp | 2026-04-30T15:39Z |

---

## 7. Code Quality Checks

### Black Formatting — FAIL

```
Command: poetry run black --check src tests
Exit code: 1
File: src/invoice_etl/load/db_loader.py

--- src\invoice_etl\load\db_loader.py   2026-04-30 15:38:09.566604+00:00
+++ src\invoice_etl\load\db_loader.py   2026-04-30 15:39:24.099123+00:00
@@ -33,11 +33,12 @@
     with engine.begin() as conn:
         result = conn.execute(
-            text("""
+            text(
+                """
                 INSERT INTO invoices (
                 ...
-                """),
+                """
+            ),
             invoice.model_dump(exclude={"line_items"}),
         )
         ...
         for item in invoice.line_items:
             conn.execute(
-                text("""
+                text(
+                    """
                     INSERT INTO line_items (
                     ...
-                    """),
+                    """
+                ),
                 {"invoice_id": invoice_id, **item.model_dump()},
             )
```

Both `text("""...""")` call sites in `db_loader.py` must be reformatted. Black requires the triple-quoted string to appear on a new indented line when the call has additional arguments on separate lines.

### Ruff Linting — PASS

```
Command: poetry run ruff check src tests
Exit code: 0
Output: All checks passed!
```

### Pyright Type Check — PASS

```
Command: poetry run pyright
Exit code: 0
Output: 0 errors, 0 warnings, 0 informations
```

---

## 8. Gaps and Exceptions

| # | Gap | Severity | File | Notes |
|---|-----|---------|------|-------|
| 1 | `db_loader.py` fails `black --check` | Blocker | `src/invoice_etl/load/db_loader.py` | Two `text("""...""")` call sites require Black's wrapping style. Fix: `poetry run black src/invoice_etl/load/db_loader.py`. |
| 2 | `_get_engine()` body (lines 18–24) and `engine is None` branch (line 34) untested | Info (pre-existing) | `src/invoice_etl/load/db_loader.py` | Pre-existing gap identical to baseline. Not introduced by this PR. Recommend dedicated test with env-var mocking in a follow-up. |
| 3 | `main.py` at 0% coverage | Info (pre-existing) | `src/invoice_etl/main.py` | Pre-existing gap. Not touched by this PR. |
| 4 | `_PARTIAL_ROW_RE` and `_DATE_IN_LINE_RE` compiled inside `_merge_truncated_lines()` | Nit | `src/invoice_etl/transform/invoice_transformer.py` | Pattern inconsistent with other module-level regexes. Minor inefficiency on repeated calls. Recommend moving to module scope. |
| 5 | `re.MULTILINE` flag on `_SOD_LINE_ITEM_RE` is redundant | Nit | `src/invoice_etl/transform/invoice_transformer.py` | The regex is applied with `re.match()` line-by-line, making `MULTILINE` a no-op. No behavioral impact; recommend removing for clarity. |

---

## 9. Summary of Changes

| File | Change Type | Description |
|------|------------|-------------|
| `src/invoice_etl/models/invoice.py` | Modified | Added `item`, `store_number`, `order_date`, `offer_number`, `unit_of_measure` to `LineItem`; added `customer_number` to `Invoice`. All new fields default to `None` for backward compatibility. |
| `src/invoice_etl/transform/invoice_transformer.py` | Modified | Added `_SodHeader` TypedDict, four private SOD parsing functions (`_parse_sod_header`, `_merge_truncated_lines`, `_parse_sod_line_item`, `_transform_sod_pages`), five SOD-specific regexes, and format-detection dispatch in `transform_pages()`. |
| `src/invoice_etl/load/db_loader.py` | Modified | Updated `invoices` INSERT to include `customer_number`; updated `line_items` INSERT to include `item`, `store_number`, `order_date`, `offer_number`, `unit_of_measure`. |
| `docker/init.sql` | Modified | Added `customer_number TEXT` column to `invoices`; added five new columns to `line_items`. |
| `tests/test_transform.py` | Modified | Added 12 new tests covering SOD header parsing, line-item parsing, truncated-line merging, SOD dispatch, and multi-page accumulation. |
| `tests/test_load.py` | Modified | Added `_make_mock_engine` helper; added two new tests for `customer_number` and new `LineItem` field forwarding in INSERT calls. |

---

## 10. Compliance Verdict

**Overall: PARTIAL — Remediation Required**

| Check | Result |
|-------|--------|
| Black formatting | ❌ FAIL — `db_loader.py` requires Black reformatting |
| Ruff linting | ✅ PASS |
| Pyright strict type check | ✅ PASS |
| pytest (20/20) | ✅ PASS |
| Coverage ≥ 80% repo-wide | ✅ PASS (82%) |
| No coverage regression | ✅ PASS |
| Design principles | ✅ PASS |
| Module structure | ✅ PASS |
| Test policy | ✅ PASS |
| Suppression policy | ✅ PASS |
| Documentation policy | ✅ PASS |

**Remediation scope:** Single file, single command fix. `poetry run black src/invoice_etl/load/db_loader.py` resolves the blocker. See `remediation-inputs.2026-04-30T15-39.md`.

---

## Appendix A: Test Inventory

### test_transform.py (16 tests)

| Test | Target | Scenario |
|------|--------|----------|
| `test_transform_parses_invoice_number` | `transform_pages` | Generic path: parses invoice number from labeled field |
| `test_transform_parses_total` | `transform_pages` | Generic path: parses total amount |
| `test_transform_unknown_invoice_number` | `transform_pages` | Generic path: falls back to UNKNOWN |
| `test_transform_sets_source_file` | `transform_pages` | Generic path: source_file set on returned Invoice |
| `test_sod_header_parses_invoice_number` | `_parse_sod_header` | SOD: extracts invoice number from labeled header |
| `test_sod_header_parses_customer_number` | `_parse_sod_header` | SOD: extracts customer account number |
| `test_sod_header_parses_invoice_date` | `_parse_sod_header` | SOD: converts MM/DD/YYYY to datetime.date |
| `test_sod_line_item_parses_all_nine_fields` | `_parse_sod_line_item` | SOD: populates all 9 LineItem fields from one row |
| `test_sod_line_item_returns_none_for_non_matching_line` | `_parse_sod_line_item` | SOD: returns None for header row |
| `test_merge_truncated_lines_merges_split_row` | `_merge_truncated_lines` | SOD: joins partial row with continuation line |
| `test_merge_truncated_lines_preserves_complete_rows` | `_merge_truncated_lines` | SOD: complete rows left unmodified |
| `test_transform_pages_sod_dispatches_and_sets_header_fields` | `transform_pages` | SOD dispatch: invoice_number and customer_number correct |
| `test_transform_pages_sod_accumulates_line_items_across_two_pages` | `transform_pages` | SOD multi-page: 2 pages produce 2 line items |
| `test_transform_pages_non_sod_format_is_unchanged` | `transform_pages` | Regression: generic path unchanged post-SOD-dispatch |

### test_load.py (4 tests + 2 pre-existing)

| Test | Target | Scenario |
|------|--------|----------|
| `test_load_returns_invoice_id` | `load_invoice` | Happy path returns invoice id (pre-existing) |
| `test_load_returns_minus_one_on_duplicate` | `load_invoice` | ON CONFLICT returns -1 (pre-existing) |
| `test_load_passes_customer_number_to_invoices_insert` | `load_invoice` | New: customer_number forwarded to invoices INSERT |
| `test_load_passes_new_line_item_fields_to_insert` | `load_invoice` | New: all four new LineItem fields forwarded to line_items INSERT |

---

## Appendix B: Toolchain Commands Reference

| Step | Command | Exit Code |
|------|---------|-----------|
| Formatting check | `poetry run black --check src tests` | 1 (FAIL) |
| Lint check | `poetry run ruff check src tests` | 0 (PASS) |
| Type check | `poetry run pyright` | 0 (PASS) |
| Test + coverage | `poetry run pytest --cov=invoice_etl --cov-report=term-missing` | 0 (PASS) |
| Coverage threshold | `poetry run coverage report --fail-under=70` | 0 (PASS, threshold 70%) |
