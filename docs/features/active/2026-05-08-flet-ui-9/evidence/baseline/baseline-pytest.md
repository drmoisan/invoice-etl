# Baseline — Pytest + Coverage

- Timestamp: 2026-05-08T13:21:00Z
- Command: `poetry run pytest --cov=invoice_etl --cov-report=term-missing`
- EXIT_CODE: 0
- Output Summary: 35 passed. Overall coverage: 94%. Module breakdown:
  - invoice_etl/__init__.py: 100%
  - invoice_etl/extract/pdf_extractor.py: 100%
  - invoice_etl/load/db_loader.py: 72%
  - invoice_etl/load/excel_loader.py: 100%
  - invoice_etl/main.py: 97%
  - invoice_etl/models/invoice.py: 100%
  - invoice_etl/transform/invoice_transformer.py: 93%
  - TOTAL: 94% (266 stmts, 16 missed)
