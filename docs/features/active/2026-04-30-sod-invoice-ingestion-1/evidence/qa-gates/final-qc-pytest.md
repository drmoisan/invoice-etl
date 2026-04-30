# Final QC — Pytest + Coverage

Timestamp: 2026-04-30T11:58:00Z
Command: poetry run pytest --cov=invoice_etl --cov-report=term-missing
EXIT_CODE: 0

Output Summary:
- 20 tests collected, 20 passed, 0 failed.
- Total coverage for `invoice_etl`: 82%
- Per-module coverage:
  - `invoice_etl/__init__.py`: 100%
  - `invoice_etl/extract/pdf_extractor.py`: 100%
  - `invoice_etl/load/db_loader.py`: 72% (missing lines 18-24, 34)
  - `invoice_etl/main.py`: 0%
  - `invoice_etl/models/invoice.py`: 100%
  - `invoice_etl/transform/invoice_transformer.py`: 93% (missing lines 92-93, 144, 156, 198-199, 320)
