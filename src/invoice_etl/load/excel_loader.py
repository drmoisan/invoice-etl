"""Write validated Invoice models to an Excel (.xlsx) workbook."""

from __future__ import annotations

import logging
from pathlib import Path

import openpyxl
from openpyxl.worksheet.worksheet import Worksheet

from invoice_etl.models.invoice import Invoice

logger = logging.getLogger(__name__)

# Ordered column names for the Invoice header sheet (excludes line_items).
_INVOICE_COLS: list[str] = [
    "invoice_number",
    "invoice_date",
    "due_date",
    "vendor_name",
    "vendor_address",
    "customer_name",
    "customer_address",
    "customer_number",
    "currency",
    "subtotal",
    "tax_amount",
    "total_amount",
    "source_file",
]

# Ordered column names for the LineItems sheet.
_LINE_ITEM_COLS: list[str] = [
    "description",
    "quantity",
    "unit_price",
    "line_total",
    "item",
    "store_number",
    "order_date",
    "offer_number",
    "unit_of_measure",
]


def load_invoice_to_excel(invoice: Invoice, output_path: Path) -> Path:
    """Write *invoice* to a ``.xlsx`` file at *output_path*.

    Creates two sheets:

    - ``Invoice``: one header row followed by one data row of invoice-level fields.
    - ``LineItems``: one header row followed by one data row per line item.

    Args:
        invoice: Validated Invoice model to serialise.
        output_path: Destination ``.xlsx`` file path; created or overwritten.

    Returns:
        The resolved *output_path* after the file has been written.
    """
    wb = openpyxl.Workbook()

    # Rename the default active sheet and populate invoice header fields.
    ws_header = wb.active
    assert ws_header is not None, "openpyxl Workbook must have a default active sheet"
    ws_header.title = "Invoice"
    invoice_data = invoice.model_dump(exclude={"line_items"})
    ws_header.append(_INVOICE_COLS)
    ws_header.append([invoice_data.get(col) for col in _INVOICE_COLS])

    # Create the LineItems sheet and write one row per line item.
    ws_items: Worksheet = wb.create_sheet(title="LineItems")
    ws_items.append(_LINE_ITEM_COLS)
    for line_item in invoice.line_items:
        item_data = line_item.model_dump()
        ws_items.append([item_data.get(col) for col in _LINE_ITEM_COLS])

    wb.save(output_path)
    logger.info("Invoice %s written to %s", invoice.invoice_number, output_path)

    return output_path
