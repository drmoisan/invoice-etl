"""Tests for the load stage."""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock

from invoice_etl.load.db_loader import load_invoice
from invoice_etl.models.invoice import Invoice, LineItem


def _make_invoice(**kwargs: object) -> Invoice:
    defaults: dict[str, object] = {
        "invoice_number": "INV-TEST-001",
        "total_amount": Decimal("100.00"),
    }
    defaults.update(kwargs)
    return Invoice(**defaults)  # type: ignore[arg-type]


def _make_mock_engine(invoice_id: int | None = 42) -> tuple[MagicMock, MagicMock]:
    """Return a (mock_engine, mock_conn) pair configured with the given invoice id.

    When ``invoice_id`` is ``None``, simulates an ON CONFLICT DO NOTHING result.
    """
    mock_engine = MagicMock()
    mock_conn = MagicMock()
    mock_result = MagicMock()
    mock_result.fetchone.return_value = (invoice_id,) if invoice_id is not None else None
    mock_conn.execute.return_value = mock_result
    mock_engine.begin.return_value.__enter__.return_value = mock_conn
    return mock_engine, mock_conn


def test_load_returns_invoice_id() -> None:
    mock_engine, _ = _make_mock_engine(invoice_id=42)
    invoice_id = load_invoice(_make_invoice(), engine=mock_engine)
    assert invoice_id == 42


def test_load_returns_minus_one_on_duplicate() -> None:
    mock_engine, _ = _make_mock_engine(invoice_id=None)
    invoice_id = load_invoice(_make_invoice(), engine=mock_engine)
    assert invoice_id == -1


def test_load_passes_customer_number_to_invoices_insert() -> None:
    """load_invoice forwards customer_number to the invoices INSERT parameter dict."""
    mock_engine, mock_conn = _make_mock_engine(invoice_id=42)
    invoice = _make_invoice(customer_number="081997")
    load_invoice(invoice, engine=mock_engine)
    # The first execute call is the invoices INSERT; its parameter dict is args[1].
    assert mock_conn.execute.call_args_list[0].args[1]["customer_number"] == "081997"


def test_load_passes_new_line_item_fields_to_insert() -> None:
    """load_invoice forwards the four new LineItem fields to the line_items INSERT."""
    mock_engine, mock_conn = _make_mock_engine(invoice_id=42)
    line_item = LineItem(
        item="01553",
        store_number="00562",
        offer_number="545039",
        unit_of_measure="EA",
    )
    invoice = _make_invoice(line_items=[line_item])
    load_invoice(invoice, engine=mock_engine)
    # The second execute call is the line_items INSERT; verify the parameter dict.
    line_item_params: dict[str, object] = mock_conn.execute.call_args_list[1].args[1]
    assert line_item_params["item"] == "01553"
    assert line_item_params["store_number"] == "00562"
    assert line_item_params["offer_number"] == "545039"
    assert line_item_params["unit_of_measure"] == "EA"
