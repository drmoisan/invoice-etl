# 2026-04-30-sod-invoice-ingestion — Spec

- **Issue:** #1
- **Parent (optional):** none
- **Owner:** drmoisan
- **Last Updated:** 2026-04-30T11-01
- **Status:** Draft
- **Version:** 0.1

## Overview

The existing ETL pipeline extracts a generic set of invoice fields (invoice number, dates, totals, basic line item description/qty/price). The sample document `artifacts/SOD00093649.pdf` is a 40-page HEB Store Order Deal invoice with a fixed-width columnar line-item format that includes domain-specific fields not currently modelled: Item code, Store Number, Order Date, Offer Number, and Unit of Measure. Additionally, Customer Number is present in the invoice header but not extracted or stored. Without this work the pipeline silently discards these fields, making the stored data incomplete for downstream reconciliation.


## Behavior

- Parse header fields from the SOD invoice format: Invoice Number, Invoice Date, Customer Name, Customer Number.
- Parse every line item row across all 40 pages with the following columns: Item (item code), Description, Store Number, Store Order Date, Offer Number, Quantity, Unit of Measure (UOM), Unit Price, Amount.
- Extend the `LineItem` Pydantic model to carry the new line-item fields.
- Extend the `Invoice` Pydantic model to carry `customer_number`.
- Update `docker/init.sql` (schema migration): add new columns to `line_items`; add `customer_number` to `invoices`.
- Update `db_loader.py` to persist all new fields.
- Update `invoice_transformer.py` with a SOD-format parser that handles the multi-page, fixed-width line-item layout produced by pdfplumber text extraction.
- All changes must pass the full toolchain: Black → Ruff → Pyright strict → pytest ≥ 70% coverage.


## Inputs / Outputs

- Inputs (CLI flags, files, env vars)
- Outputs (artifacts, logs, telemetry)
- Config keys and defaults:
- Versioning or backward-compatibility constraints:

## API / CLI Surface

List commands, flags, request/response shapes, and examples.
- Example invocations with expected outputs (concise):
- Contracts and validation rules:

## Data & State

Data flow, storage, or state changes introduced by this feature.
- Data transformations and invariants:
- Caching or persistence details:
- Migration or backfill requirements (if any):

## Constraints & Risks

- The line-item rows are fused into a single table cell by pdfplumber (not split into individual columns). The parser must use regex or positional splitting on the extracted text string.
- Page continuation: header fields repeat on every page; line items accumulate across all 40 pages. The parser must deduplicate header reads and concatenate line items.
- Existing `Invoice`/`LineItem` models are referenced by existing tests. Any schema change must be backward-compatible or all affected tests updated.
- `docker/init.sql` is a fresh-init script (no migration framework). If a live database exists, manual column addition is required.
- No new third-party dependencies should be introduced.


## Implementation Strategy

- Implementation scope (what changes, not sequencing):
- New classes/functions/commands to add or update:
- Dependency changes (new/removed packages) and rationale:
- Logging/telemetry additions and locations:
- Rollout plan (feature flags, staged deploys, fallback path):

## Definition of Done

- [ ] Acceptance criteria documented and mapped to tests or demos
- [ ] Behavior matches acceptance criteria in all documented environments
- [ ] Tests updated/added (unit/integration as applicable)
- [ ] Edge cases and error handling covered by tests
- [ ] Docs updated (README, docs/features/active/... links)
- [ ] Telemetry/logging added or updated (if applicable)
- [ ] Toolchain pass completed (format → lint → type-check → test)

## Seeded Test Conditions (from potential)
- [ ] Unit test: parse a representative 3-line SOD text block and assert all 9 fields per row.
- [ ] Unit test: header extraction returns correct Invoice Number, Invoice Date, Customer Number, Customer Name from SOD page 1 text.
- [ ] Unit test: multi-page accumulation — two pages of line items produce correct combined count.
- [ ] Unit test: `load_invoice()` with new fields calls execute with correct parameters.
- [ ] Edge case: last row on a page truncated mid-text (observed in PDF: "501553 RGF POPCORN CHIC") — parser handles gracefully.
