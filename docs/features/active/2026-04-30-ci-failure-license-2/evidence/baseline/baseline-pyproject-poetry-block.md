[tool.poetry] block from pyproject.toml as of 2026-04-30 (no `license =` line present):

[tool.poetry]
name = "invoice-etl"
version = "0.1.0"
description = "ETL pipeline for extracting transaction data from customer invoice PDFs into PostgreSQL."
authors = []
readme = "README.md"
packages = [{ include = "invoice_etl", from = "src" }]
