# Remediation QC — Pytest

Timestamp: 2026-04-30T15:39:00Z
Command: poetry run pytest --cov=invoice_etl --cov-report=term-missing
EXIT_CODE: 0

## Output Summary

20 tests collected, 20 passed, 0 failed.
Total coverage: 82%.

Module coverage breakdown:
- invoice_etl/__init__.py: 100%
- invoice_etl/extract/__init__.py: 100%
- invoice_etl/extract/pdf_extractor.py: 100%
- invoice_etl/load/__init__.py: 100%
- invoice_etl/load/db_loader.py: 72% (missing lines 18-24, 34)
- invoice_etl/main.py: 0% (missing lines 3-43)
- invoice_etl/models/__init__.py: 100%
- invoice_etl/models/invoice.py: 100%
- invoice_etl/transform/__init__.py: 100%
- invoice_etl/transform/invoice_transformer.py: 93% (missing lines 99-100, 151, 163, 201-202, 324)

Coverage threshold met: 82% ≥ 70% required minimum.
