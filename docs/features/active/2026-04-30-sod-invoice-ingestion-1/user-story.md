# `2026-04-30-sod-invoice-ingestion` — User Story

- Issue: #1
- Owner: drmoisan
- Status: Draft
- Last Updated: 2026-04-30T11-01

## Story Statement

- As a data engineer running the invoice ETL pipeline, I want the pipeline to extract and persist Item codes, Store Numbers, Order Dates, Offer Numbers, Units of Measure, and Customer Numbers from SOD invoices, so that the database contains a complete and accurate record of every line-item field for audit and downstream processing.
- As a downstream analytics consumer querying the invoice database, I want all SOD line-item and header fields stored in structured columns with correct types, so that I can reconcile store-level order quantities, offer usage, and unit pricing without reprocessing the original PDF files.

## Problem / Why

The existing ETL pipeline extracts a generic set of invoice fields (invoice number, dates, totals, basic line item description/qty/price). The sample document `artifacts/SOD00093649.pdf` is a 40-page HEB Store Order Deal invoice with a fixed-width columnar line-item format that includes domain-specific fields not currently modelled: Item code, Store Number, Order Date, Offer Number, and Unit of Measure. Additionally, Customer Number is present in the invoice header but not extracted or stored. Without this work the pipeline silently discards these fields, making the stored data incomplete for downstream reconciliation.


## Personas & Scenarios

- **Persona: Data Engineer (pipeline operator)**
  - A developer responsible for running and maintaining the invoice ETL pipeline against supplier PDF documents.
  - Cares about: data completeness, parser correctness, maintainability, and the ability to re-run the pipeline on future SOD PDFs without code changes.
  - Constraints: must not introduce new third-party dependencies; must preserve existing test coverage; cannot change the `pdf_extractor` interface or the `transform_pages()` public signature.
  - Goals: extend the pipeline so that `transform_pages()` correctly handles the SOD fixed-width columnar format and `load_invoice()` persists all 9 line-item fields and `customer_number`.
  - Frustrations: the current pipeline silently discards domain-specific fields, making it impossible to verify that stored data matches the source document.

- **Persona: Downstream Analytics Consumer**
  - An analyst or downstream system querying the `invoices` and `line_items` tables to support vendor reconciliation, store-level reporting, or ERP integration.
  - Cares about: structured, queryable data per store, per offer, and per item code; `order_date` typed as `DATE` to enable range filtering.
  - Constraints: cannot access the original PDFs; depends entirely on the structured relational data in the PostgreSQL database.
  - Goals: join `line_items` on `store_number`, aggregate by `offer_number`, and validate quantities and amounts against vendor deal records.
  - Frustrations: without `store_number`, `order_date`, and `offer_number` in the database, per-store reconciliation requires manual PDF re-reading.

- **Scenario: SOD Invoice Ingestion End-to-End**
  - The data engineer receives `SOD00093649.pdf`, a 40-page HEB Store Order Deal invoice.
  - They invoke the pipeline with the PDF path as input.
  - `pdf_extractor.extract_text_from_pdf()` returns a 40-element list of page text strings via `pdfplumber`.
  - `transform_pages()` detects `"Customer Number:"` in the combined text and dispatches to `_transform_sod_pages()`.
  - `_parse_sod_header()` extracts `invoice_number="SOD00093649"`, `invoice_date=date(2026, 3, 16)`, `customer_number="081997"`, and `customer_name` from page 1 text.
  - For each page, `_merge_truncated_lines()` repairs rows split at page boundaries, then `_parse_sod_line_item()` converts each complete row into a `LineItem` with all 9 fields populated.
  - `transform_pages()` returns an `Invoice` with all header fields populated and `line_items` containing one entry per row across all 40 pages.
  - `load_invoice()` inserts the invoice record (including `customer_number`) and all line item records (including the 5 new columns) into PostgreSQL.
  - The analytics consumer queries `SELECT store_number, offer_number, SUM(quantity) FROM line_items WHERE invoice_id = <id> GROUP BY store_number, offer_number` and verifies the totals against the source PDF.


## Acceptance Criteria

- [x] `LineItem` model includes: `item`, `store_number`, `order_date`, `offer_number`, `unit_of_measure` fields with correct types.
- [x] `Invoice` model includes: `customer_number` field.
- [x] `transform_pages()` correctly parses line items from `SOD00093649.pdf` text, returning all per-row fields.
- [x] `load_invoice()` persists the new `LineItem` and `Invoice` fields to the database.
- [x] `docker/init.sql` schema includes updated `line_items` and `invoices` column definitions.
- [x] All existing tests continue to pass (zero regressions).
- [x] New unit tests cover the SOD transformer with ≥ 80% branch coverage on the new parser logic.
- [x] Full toolchain (Black + Ruff + Pyright strict + pytest) passes without errors.


## Non-Goals

- Parsing invoice formats other than the SOD (HEB Store Order Deal) template. The existing generic parsing path is unchanged.
- Extracting or storing per-page sequence counters from SOD line item rows. The counter is consumed by the regex and discarded.
- Using `pdfplumber.extract_tables()`. The implementation uses `extract_text()` output exclusively.
- Introducing a database migration framework. Schema changes are applied by modifying `docker/init.sql` directly.
- Modifying the CLI interface or adding new entry points. `main.py` and its flags remain unchanged.
- Extracting vendor name or vendor address from the SOD header. The SOD format does not present vendor fields in a reliably parseable form.
- Storing raw PDF text in the database.
- Supporting partial or incremental loads. The existing `ON CONFLICT (invoice_number) DO NOTHING` deduplication strategy is unchanged.
