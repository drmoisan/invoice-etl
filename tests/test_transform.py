"""Tests for the transform stage."""

from __future__ import annotations

from decimal import Decimal

from invoice_etl.transform.invoice_transformer import transform_pages


def test_transform_parses_invoice_number() -> None:
    pages = ["Invoice No. INV-2024-001\nTotal: 1,200.00"]
    invoice = transform_pages(pages)
    assert invoice.invoice_number == "INV-2024-001"


def test_transform_parses_total() -> None:
    pages = ["Invoice #42\nTotal 500.00"]
    invoice = transform_pages(pages)
    assert invoice.total_amount == Decimal("500.00")


def test_transform_unknown_invoice_number() -> None:
    pages = ["No structured data here."]
    invoice = transform_pages(pages)
    assert invoice.invoice_number == "UNKNOWN"


def test_transform_sets_source_file() -> None:
    invoice = transform_pages(["Invoice #X"], source_file="/tmp/x.pdf")
    assert invoice.source_file == "/tmp/x.pdf"
