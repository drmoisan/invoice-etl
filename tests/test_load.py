"""Tests for the load stage."""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock, patch

from invoice_etl.load.db_loader import load_invoice
from invoice_etl.models.invoice import Invoice


def _make_invoice(**kwargs: object) -> Invoice:
    defaults: dict[str, object] = {
        "invoice_number": "INV-TEST-001",
        "total_amount": Decimal("100.00"),
    }
    defaults.update(kwargs)
    return Invoice(**defaults)  # type: ignore[arg-type]


def test_load_returns_invoice_id() -> None:
    mock_engine = MagicMock()
    mock_conn = MagicMock()
    mock_result = MagicMock()
    mock_result.fetchone.return_value = (42,)
    mock_conn.execute.return_value = mock_result
    mock_engine.begin.return_value.__enter__ = lambda s: mock_conn
    mock_engine.begin.return_value.__exit__ = MagicMock(return_value=False)

    invoice_id = load_invoice(_make_invoice(), engine=mock_engine)
    assert invoice_id == 42


def test_load_returns_minus_one_on_duplicate() -> None:
    mock_engine = MagicMock()
    mock_conn = MagicMock()
    mock_result = MagicMock()
    mock_result.fetchone.return_value = None  # ON CONFLICT DO NOTHING
    mock_conn.execute.return_value = mock_result
    mock_engine.begin.return_value.__enter__ = lambda s: mock_conn
    mock_engine.begin.return_value.__exit__ = MagicMock(return_value=False)

    invoice_id = load_invoice(_make_invoice(), engine=mock_engine)
    assert invoice_id == -1
