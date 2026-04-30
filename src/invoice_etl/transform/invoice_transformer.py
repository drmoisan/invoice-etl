"""Transform raw extracted text into validated Invoice models."""

from __future__ import annotations

import logging
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

from invoice_etl.models.invoice import Invoice, LineItem

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Simple regex-based field parsers — replace with ML/template logic as needed
# ---------------------------------------------------------------------------

_INVOICE_NUMBER_RE = re.compile(r"(?i)invoice\s*[#no.:]+\s*([A-Z0-9\-]+)")
_DATE_RE = re.compile(r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})")
_AMOUNT_RE = re.compile(r"(?i)(subtotal|tax|total)[^\d]*([\d,]+\.\d{2})")
_CURRENCY_RE = re.compile(r"\b(USD|EUR|CAD|GBP)\b")


def _parse_decimal(value: str) -> Decimal | None:
    try:
        return Decimal(value.replace(",", ""))
    except InvalidOperation:
        return None


def transform_pages(pages: list[str], source_file: str | None = None) -> Invoice:
    """Parse *pages* (raw text per page) into an :class:`~invoice_etl.models.invoice.Invoice`.

    This implementation uses simple regex heuristics.  Extend or replace the
    individual ``_parse_*`` helpers for layout-specific templates.
    """
    full_text = "\n".join(pages)

    invoice_number = "UNKNOWN"
    if m := _INVOICE_NUMBER_RE.search(full_text):
        invoice_number = m.group(1).strip()

    currency: str | None = None
    if m := _CURRENCY_RE.search(full_text):
        currency = m.group(1)

    amounts: dict[str, Decimal] = {}
    for m in _AMOUNT_RE.finditer(full_text):
        label = m.group(1).lower()
        value = _parse_decimal(m.group(2))
        if value is not None:
            amounts[label] = value

    invoice = Invoice(
        invoice_number=invoice_number,
        currency=currency,
        subtotal=amounts.get("subtotal"),
        tax_amount=amounts.get("tax"),
        total_amount=amounts.get("total"),
        source_file=source_file,
    )
    logger.debug("Transformed invoice %s", invoice.invoice_number)
    return invoice
