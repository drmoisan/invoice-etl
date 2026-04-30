# `2026-04-30-sod-invoice-ingestion` — User Story

- Issue: #1
- Owner: drmoisan
- Status: Draft
- Last Updated: 2026-04-30T11-01

## Story Statement

- As a ..., I want ..., so that ...
- As a ..., I want ..., so that ...

## Problem / Why

The existing ETL pipeline extracts a generic set of invoice fields (invoice number, dates, totals, basic line item description/qty/price). The sample document `artifacts/SOD00093649.pdf` is a 40-page HEB Store Order Deal invoice with a fixed-width columnar line-item format that includes domain-specific fields not currently modelled: Item code, Store Number, Order Date, Offer Number, and Unit of Measure. Additionally, Customer Number is present in the invoice header but not extracted or stored. Without this work the pipeline silently discards these fields, making the stored data incomplete for downstream reconciliation.


## Personas & Scenarios

- Persona: ...
  - who the user is
  - what they care about
  - their constraints
  - their goals and frustrations
  - their context and motivations
- Scenario: ...
  - A concrete, step-by-step narrative that describes how a user accomplishes a goal in a real-world context using the system.
  - who is acting?
  - what triggered the action?
  - what steps do they take?
  - what obstacles or decisions occur?
  - what outcome do they expect?


## Acceptance Criteria

- [ ] `LineItem` model includes: `item`, `store_number`, `order_date`, `offer_number`, `unit_of_measure` fields with correct types.
- [ ] `Invoice` model includes: `customer_number` field.
- [ ] `transform_pages()` correctly parses line items from `SOD00093649.pdf` text, returning all per-row fields.
- [ ] `load_invoice()` persists the new `LineItem` and `Invoice` fields to the database.
- [ ] `docker/init.sql` schema includes updated `line_items` and `invoices` column definitions.
- [ ] All existing tests continue to pass (zero regressions).
- [ ] New unit tests cover the SOD transformer with ≥ 80% branch coverage on the new parser logic.
- [ ] Full toolchain (Black + Ruff + Pyright strict + pytest) passes without errors.


## Non-Goals

Call out what is explicitly excluded from this feature.
