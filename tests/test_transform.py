"""Tests for the transform stage."""

from __future__ import annotations

import datetime
from decimal import Decimal

from invoice_etl.transform.invoice_transformer import (
    _merge_truncated_lines,  # type: ignore[reportPrivateUsage]  # plan requires testing private SOD helpers directly
    _parse_sod_header,  # type: ignore[reportPrivateUsage]  # plan requires testing private SOD helpers directly
    _parse_sod_line_item,  # type: ignore[reportPrivateUsage]  # plan requires testing private SOD helpers directly
    transform_pages,
)

# ---------------------------------------------------------------------------
# Shared SOD test fixtures (inline literals, no file I/O)
# ---------------------------------------------------------------------------

_SOD_HEADER_TEXT = (
    "Invoice Number: SODTEST1001\n"
    "Invoice Date: 03/16/2026\n"
    "Customer Number: 900123\n"
    "ANON MARKET COMPANY"
)

_SOD_LINE_ITEM_ROW = "5 01553 SAMPLE CRISPY BITES 00562 03/13/2026 545039 1 EA 9.9900 9.99"
_SOD_LINE_ITEM_ROW_2 = "6 60461 SAMPLE MINI BITES 20 OZ 00052 03/08/2026 545038 1 EA 9.9800 9.98"

# ---------------------------------------------------------------------------
# Existing generic-path tests (must remain unchanged)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# SOD header parsing tests
# ---------------------------------------------------------------------------


def test_sod_header_parses_invoice_number() -> None:
    """_parse_sod_header returns the correct invoice number from labeled field."""
    result = _parse_sod_header(_SOD_HEADER_TEXT)
    assert result["invoice_number"] == "SODTEST1001"


def test_sod_header_parses_customer_number() -> None:
    """_parse_sod_header returns the correct customer account number."""
    result = _parse_sod_header(_SOD_HEADER_TEXT)
    assert result["customer_number"] == "900123"


def test_sod_header_parses_invoice_date() -> None:
    """_parse_sod_header converts MM/DD/YYYY to datetime.date correctly."""
    result = _parse_sod_header(_SOD_HEADER_TEXT)
    assert result["invoice_date"] == datetime.date(2026, 3, 16)


# ---------------------------------------------------------------------------
# SOD line-item parsing tests
# ---------------------------------------------------------------------------


def test_sod_line_item_parses_all_nine_fields() -> None:
    """_parse_sod_line_item populates all nine LineItem fields from a complete row."""
    li = _parse_sod_line_item(_SOD_LINE_ITEM_ROW)
    assert li is not None
    assert li.item == "01553"
    assert li.description is not None and "SAMPLE CRISPY BITES" in li.description
    assert li.store_number == "00562"
    assert li.order_date == datetime.date(2026, 3, 13)
    assert li.offer_number == "545039"
    assert li.quantity == Decimal("1")
    assert li.unit_of_measure == "EA"
    assert li.unit_price == Decimal("9.9900")
    assert li.line_total == Decimal("9.99")


def test_sod_line_item_returns_none_for_non_matching_line() -> None:
    """_parse_sod_line_item returns None for a header row that has no numeric prefix."""
    result = _parse_sod_line_item(
        "Item  Description  Store No  Str Ord Dt  Offer#  Qty  UOM  Unit Price  Amount"
    )
    assert result is None


# ---------------------------------------------------------------------------
# Truncated-line merging tests
# ---------------------------------------------------------------------------


def test_merge_truncated_lines_merges_split_row() -> None:
    """_merge_truncated_lines joins a partial row with its continuation line."""
    result = _merge_truncated_lines(
        ["5 01553 ABC ABCDEFG ABCD", "KEN 00562 03/13/2026 545039 1 EA 9.9900 9.99"]
    )
    assert len(result) == 1
    assert "01553" in result[0]
    assert "00562" in result[0]


def test_merge_truncated_lines_preserves_complete_rows() -> None:
    """_merge_truncated_lines leaves complete rows (with a date) unmodified."""
    result = _merge_truncated_lines([_SOD_LINE_ITEM_ROW, _SOD_LINE_ITEM_ROW_2])
    assert len(result) == 2
    assert result[0] == _SOD_LINE_ITEM_ROW
    assert result[1] == _SOD_LINE_ITEM_ROW_2


# ---------------------------------------------------------------------------
# Full SOD dispatch tests via transform_pages()
# ---------------------------------------------------------------------------


def test_transform_pages_sod_dispatches_and_sets_header_fields() -> None:
    """transform_pages dispatches to the SOD path and populates invoice header fields."""
    invoice = transform_pages([_SOD_HEADER_TEXT])
    assert invoice.invoice_number == "SODTEST1001"
    assert invoice.customer_number == "900123"


def test_transform_pages_sod_accumulates_line_items_across_two_pages() -> None:
    """transform_pages accumulates line items from multiple SOD pages."""
    page1 = _SOD_HEADER_TEXT + "\n" + _SOD_LINE_ITEM_ROW
    page2 = _SOD_LINE_ITEM_ROW_2
    invoice = transform_pages([page1, page2])
    assert len(invoice.line_items) == 2


def test_transform_pages_non_sod_format_is_unchanged() -> None:
    """transform_pages follows the generic path for non-SOD inputs without regression."""
    invoice = transform_pages(["Invoice No. INV-2024-001\nTotal: 1,200.00"])
    assert invoice.invoice_number == "INV-2024-001"
    assert invoice.customer_number is None
