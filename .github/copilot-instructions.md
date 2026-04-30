# Invoice ETL — Copilot Instructions

## Project Overview

Python ETL pipeline that extracts transaction data from customer invoices (PDF), transforms
it into standardised master data fields, and loads it into a PostgreSQL database running in Docker.

## Stack

- **Python**: 3.12+
- **Dependency management**: Poetry
- **Formatter**: Black
- **Linter**: Ruff
- **Type checker**: Pyright
- **Database**: PostgreSQL 16 (Docker)
- **ORM / DB access**: SQLAlchemy 2.x + psycopg2-binary
- **PDF extraction**: pdfplumber
- **Data modelling**: Pydantic v2
- **Testing**: pytest + pytest-cov

## Conventions

- All source code lives under `src/invoice_etl/`.
- ETL stages are separated into `extract/`, `transform/`, and `load/` sub-packages.
- Pydantic models live in `models/`.
- Use type annotations everywhere; Pyright strict mode is enabled.
- Format with Black (line length 100). Ruff enforces PEP8 + import ordering.
- Environment variables are loaded from `.env` via `python-dotenv`; never hard-code secrets.
- Database migrations are handled with plain SQL init scripts in `docker/`.

## Completed Steps

- [x] copilot-instructions.md created
