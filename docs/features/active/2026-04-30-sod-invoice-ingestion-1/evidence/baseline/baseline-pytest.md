# Baseline — Pytest + Coverage

Timestamp: 2026-04-30T11:34:00Z
Command: poetry run pytest --cov=invoice_etl --cov-report=term-missing
EXIT_CODE: 0

Output Summary:
- 8 tests collected, 8 passed, 0 failed.
- Total coverage for `invoice_etl`: 70%
- Per-module coverage:
  - `invoice_etl/__init__.py`: 100%
  - `invoice_etl/extract/pdf_extractor.py`: 100%
  - `invoice_etl/load/db_loader.py`: 69% (missing lines 18-24, 34, 65)
  - `invoice_etl/main.py`: 0%
  - `invoice_etl/models/invoice.py`: 100%
  - `invoice_etl/transform/invoice_transformer.py`: 91% (missing lines 26-27, 44)
