# Invoice ETL

Python ETL pipeline that extracts transaction data from customer invoices (PDF), transforms it
into standardised master data fields, and loads it into a PostgreSQL database running in Docker.

## Prerequisites

| Tool                    | Version |
| ----------------------- | ------- |
| Python                  | 3.12+   |
| Poetry                  | 1.8+    |
| Docker & Docker Compose | v2+     |

## Quick start

```bash
# 1. Install dependencies
poetry install

# 2. Copy and review environment variables
cp .env.example .env   # edit values if needed

# 3. Start PostgreSQL
docker compose up -d

# 4. Run the pipeline against one or more PDFs

# Load into PostgreSQL (default)
poetry run invoice-etl path/to/invoice.pdf

# Export to Excel instead (no database required)
poetry run invoice-etl --output excel path/to/invoice.pdf
```

## Project structure

```
invoice-etl/
├── src/invoice_etl/
│   ├── extract/          # PDF text extraction (pdfplumber)
│   ├── transform/        # Raw text → Pydantic Invoice models
│   ├── load/             # db_loader.py (PostgreSQL) + excel_loader.py (.xlsx)
│   ├── models/           # Pydantic v2 data models
│   └── main.py           # CLI entry point (--output db|excel)
├── tests/                # pytest unit tests
├── docker/
│   └── init.sql          # PostgreSQL schema initialisation
├── docker-compose.yml
├── pyproject.toml        # Poetry + Black + Ruff + Pyright config
└── .env.example
```

## Development

```bash
# Format
poetry run black src tests

# Lint
poetry run ruff check src tests

# Type-check
poetry run pyright

# Test with coverage
poetry run pytest
```

## Environment variables

| Variable            | Default      | Description       |
| ------------------- | ------------ | ----------------- |
| `POSTGRES_HOST`     | `localhost`  | Database host     |
| `POSTGRES_PORT`     | `5432`       | Database port     |
| `POSTGRES_USER`     | `etl`        | Database user     |
| `POSTGRES_PASSWORD` | _(required)_ | Database password |
| `POSTGRES_DB`       | `invoices`   | Database name     |
