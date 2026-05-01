# Baseline — Pytest with Coverage

Timestamp: 2026-04-30T19:52:00Z
Command: `poetry run pytest --cov=invoice_etl --cov-report=term-missing`
EXIT_CODE: 0

## Output Summary

25 passed, 0 failed. Total: 93%

Coverage by module:
- `src/invoice_etl/__init__.py`: 100% (0/0 missing)
- `src/invoice_etl/extract/__init__.py`: 100% (0/0 missing)
- `src/invoice_etl/extract/pdf_extractor.py`: 100% (15/15 statements)
- `src/invoice_etl/load/__init__.py`: 100% (0/0 missing)
- `src/invoice_etl/load/db_loader.py`: 72% (21/29 statements; missing lines 18-24, 34)
- `src/invoice_etl/main.py`: 96% (25/26 statements; missing line 43)
- `src/invoice_etl/models/__init__.py`: 100% (0/0 missing)
- `src/invoice_etl/models/invoice.py`: 100% (52/52 statements)
- `src/invoice_etl/transform/__init__.py`: 100% (0/0 missing)
- `src/invoice_etl/transform/invoice_transformer.py`: 93% (100/107 statements; missing lines 99-100, 151, 163, 201-202, 324)
- **TOTAL: 229 statements, 16 missing — 93% coverage**
