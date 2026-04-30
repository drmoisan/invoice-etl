"""Transform raw extracted text into validated Invoice models."""

from __future__ import annotations

import datetime
import logging
import re
from decimal import Decimal, InvalidOperation
from typing import TypedDict

from invoice_etl.models.invoice import Invoice, LineItem

logger = logging.getLogger(__name__)


class _SodHeader(TypedDict):
    """Typed return structure for ``_parse_sod_header``.

    All fields except ``invoice_number`` may be ``None`` when the corresponding
    label is absent from the page text.
    """

    invoice_number: str
    invoice_date: datetime.date | None
    customer_number: str | None
    customer_name: str | None
    total_amount: Decimal | None


# ---------------------------------------------------------------------------
# Simple regex-based field parsers — replace with ML/template logic as needed
# ---------------------------------------------------------------------------

_INVOICE_NUMBER_RE = re.compile(r"(?i)invoice\s*[#no.:]+\s*([A-Z0-9\-]+)")
_DATE_RE = re.compile(r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})")
_AMOUNT_RE = re.compile(r"(?i)(subtotal|tax|total)[^\d]*([\d,]+\.\d{2})")
_CURRENCY_RE = re.compile(r"\b(USD|EUR|CAD|GBP)\b")

# ---------------------------------------------------------------------------
# SOD (Store Order Deal) format regexes
# ---------------------------------------------------------------------------

# Matches the labeled "Invoice Number: SOD00093649" header field.
_SOD_INVOICE_NUMBER_RE = re.compile(r"Invoice Number:\s*(\S+)")

# Matches the labeled "Invoice Date: 03/16/2026" header field.
_SOD_INVOICE_DATE_RE = re.compile(r"Invoice Date:\s*(\d{1,2}/\d{1,2}/\d{4})")

# Matches the labeled "Customer Number: 081997" header field.
_SOD_CUSTOMER_NUMBER_RE = re.compile(r"Customer Number:\s*(\S+)")

# Matches the grand total line "TOTAL: $17,865.06" (dollar sign optional).
_SOD_TOTAL_RE = re.compile(r"TOTAL:\s*\$?([\d,]+\.\d{2})")

# Matches a complete SOD line-item row with 9 capture groups:
#   1: item code (5-digit SKU)
#   2: description (non-greedy, stops before store+date anchor)
#   3: store number (5-digit, zero-padded)
#   4: order date (MM/DD/YYYY)
#   5: offer number
#   6: quantity
#   7: unit of measure (uppercase alpha)
#   8: unit price
#   9: line total
# The leading digit is a per-page sequence counter — consumed but not captured.
_SOD_LINE_ITEM_RE = re.compile(
    r"^\d+\s+"  # sequence counter (consumed, not captured)
    r"(\d{5})\s+"  # group 1: item code (5-digit)
    r"(.+?)\s+"  # group 2: description (non-greedy, anchored by store+date)
    r"(\d{5})\s+"  # group 3: store number (5-digit)
    r"(\d{2}/\d{2}/\d{4})\s+"  # group 4: order date MM/DD/YYYY
    r"(\d+)\s+"  # group 5: offer number
    r"([\d.]+)\s+"  # group 6: quantity
    r"([A-Z]+)\s+"  # group 7: UOM (uppercase alpha)
    r"([\d.]+)\s+"  # group 8: unit price
    r"([\d.]+)\s*$",  # group 9: line total
)

# Partial-row detection: starts with a counter + 5-digit item code but lacks a date.
# Used by ``_merge_truncated_lines`` to identify rows split across page boundaries.
_PARTIAL_ROW_RE = re.compile(r"^\d+\s+\d{5}\s+")

# Matches an embedded date field MM/DD/YYYY within a line-item row.
# Used together with ``_PARTIAL_ROW_RE`` to confirm a row is truly truncated.
_DATE_IN_LINE_RE = re.compile(r"\d{2}/\d{2}/\d{4}")


def _parse_decimal(value: str) -> Decimal | None:
    """Convert a string to Decimal, stripping commas. Returns None on failure.

    Args:
        value: A numeric string, potentially containing comma thousands-separators.

    Returns:
        A ``Decimal`` instance, or ``None`` if the conversion fails.
    """
    try:
        return Decimal(value.replace(",", ""))
    except InvalidOperation:
        return None


# ---------------------------------------------------------------------------
# SOD-specific helper functions
# ---------------------------------------------------------------------------

# Customer name block: two consecutive all-caps lines where the second contains
# a common company-suffix keyword. Used to extract the company name from page 1.
_SOD_CUSTOMER_NAME_BLOCK_RE = re.compile(
    r"^([A-Z][A-Z\s]+)\n([A-Z][A-Z\s]+(?:LLC|INC|CORP|CO|COMPANY)[A-Z\s]*)\s*$",
    re.MULTILINE,
)


def _parse_sod_header(text: str) -> _SodHeader:
    """Extract SOD invoice header fields from page-1 text using labeled-field regexes.

    Applies ``_SOD_INVOICE_NUMBER_RE``, ``_SOD_INVOICE_DATE_RE``,
    ``_SOD_CUSTOMER_NUMBER_RE``, and ``_SOD_TOTAL_RE`` to extract structured
    header values. Customer name is identified by a heuristic that locates
    consecutive all-caps lines; if the primary regex fails, the last
    consecutive all-caps line is used as a fallback. If all heuristics fail,
    ``customer_name`` defaults to ``None``.

    Args:
        text: Raw text extracted from the first PDF page.

    Returns:
        A ``_SodHeader`` TypedDict with keys ``invoice_number``, ``invoice_date``,
        ``customer_number``, ``customer_name``, and ``total_amount``.
    """
    # Extract invoice number from the labeled header field.
    invoice_number = "UNKNOWN"
    if m := _SOD_INVOICE_NUMBER_RE.search(text):
        invoice_number = m.group(1).strip()

    # Parse invoice date, converting from MM/DD/YYYY to datetime.date.
    invoice_date: datetime.date | None = None
    if m := _SOD_INVOICE_DATE_RE.search(text):
        invoice_date = datetime.datetime.strptime(m.group(1), "%m/%d/%Y").date()

    # Extract the customer account number from the labeled header field.
    customer_number: str | None = None
    if m := _SOD_CUSTOMER_NUMBER_RE.search(text):
        customer_number = m.group(1).strip()

    # Attempt to identify customer name from consecutive all-caps lines.
    # Primary strategy: match two all-caps lines where the second has a company suffix.
    customer_name: str | None = None
    if m := _SOD_CUSTOMER_NAME_BLOCK_RE.search(text):
        customer_name = m.group(2).strip()
    else:
        # Fallback: collect all consecutive all-caps lines and use the last one.
        caps_lines = [
            line.strip() for line in text.splitlines() if line.strip() and line.strip().isupper()
        ]
        if caps_lines:
            customer_name = caps_lines[-1]

    # Extract the grand total amount.
    total_amount: Decimal | None = None
    if m := _SOD_TOTAL_RE.search(text):
        total_amount = _parse_decimal(m.group(1))

    return _SodHeader(
        invoice_number=invoice_number,
        invoice_date=invoice_date,
        customer_number=customer_number,
        customer_name=customer_name,
        total_amount=total_amount,
    )


def _merge_truncated_lines(lines: list[str]) -> list[str]:
    """Merge line-item rows split across PDF page boundaries.

    A row is identified as truncated when it begins with the item-counter and
    item-code prefix (``\\d+ \\d{5}``) but contains no date field (MM/DD/YYYY).
    The immediately following line that does not start with a digit is treated
    as the continuation and is joined with a single space.

    Args:
        lines: Raw text lines from a single PDF page.

    Returns:
        A new list of lines with split rows merged into single entries.
    """
    merged: list[str] = []
    skip_next = False

    for i, line in enumerate(lines):
        # This line was already consumed as a continuation in the previous iteration.
        if skip_next:
            skip_next = False
            continue

        stripped = line.strip()

        # Preserve blank lines without modification.
        if not stripped:
            merged.append(stripped)
            continue

        # Determine whether this line is a truncated item row (prefix present, no date).
        # Both regexes are defined at module scope alongside the other SOD constants.
        is_partial = bool(_PARTIAL_ROW_RE.match(stripped)) and not bool(
            _DATE_IN_LINE_RE.search(stripped)
        )

        if is_partial and i + 1 < len(lines):
            next_stripped = lines[i + 1].strip()
            # Continuation lines do not start with a digit (no item counter prefix).
            if next_stripped and not next_stripped[0].isdigit():
                merged.append(stripped + " " + next_stripped)
                skip_next = True
                continue

        merged.append(stripped)

    return merged


def _parse_sod_line_item(line: str) -> LineItem | None:
    """Match one text line against ``_SOD_LINE_ITEM_RE`` and return a ``LineItem``.

    Constructs a ``LineItem`` from the nine capture groups when the regex matches.
    Fields use the existing ``_parse_decimal`` helper for numeric conversion and
    ``datetime.datetime.strptime`` for date conversion. Returns ``None`` for any
    line that does not fully match (headers, blank lines, totals rows, etc.).

    Args:
        line: A single text line from a SOD PDF page.

    Returns:
        A populated ``LineItem``, or ``None`` if the line does not match.
    """
    m = _SOD_LINE_ITEM_RE.match(line.strip())
    if m is None:
        return None

    # Convert the order date string from MM/DD/YYYY to datetime.date.
    order_date = datetime.datetime.strptime(m.group(4), "%m/%d/%Y").date()

    return LineItem(
        item=m.group(1),
        description=m.group(2).strip(),
        store_number=m.group(3),
        order_date=order_date,
        offer_number=m.group(5),
        quantity=_parse_decimal(m.group(6)),
        unit_of_measure=m.group(7),
        unit_price=_parse_decimal(m.group(8)),
        line_total=_parse_decimal(m.group(9)),
    )


def _transform_sod_pages(pages: list[str], source_file: str | None) -> Invoice:
    """Orchestrate SOD header and line-item parsing across all pages.

    Parses the invoice header from the first page only, then iterates all pages
    applying ``_merge_truncated_lines`` followed by ``_parse_sod_line_item`` on
    each resulting line. Non-``None`` results accumulate into ``line_items``.

    Args:
        pages: Raw text strings, one per PDF page.
        source_file: Optional originating file path for traceability.

    Returns:
        A fully populated ``Invoice`` with header fields and all parsed line items.
    """
    # Parse header from the first page only; subsequent pages repeat header fields.
    header = _parse_sod_header(pages[0])

    line_items: list[LineItem] = []

    # Iterate every page to accumulate line items across the full document.
    for page_text in pages:
        lines = page_text.splitlines()
        # Merge any rows split at the end of the previous page before parsing.
        merged_lines = _merge_truncated_lines(lines)
        for line in merged_lines:
            item = _parse_sod_line_item(line)
            if item is not None:
                line_items.append(item)

    return Invoice(
        invoice_number=header["invoice_number"],
        invoice_date=header["invoice_date"],
        customer_number=header["customer_number"],
        customer_name=header["customer_name"],
        total_amount=header["total_amount"],
        line_items=line_items,
        source_file=source_file,
    )


def transform_pages(pages: list[str], source_file: str | None = None) -> Invoice:
    """Parse *pages* (raw text per page) into an :class:`~invoice_etl.models.invoice.Invoice`.

    Detects SOD format by checking for the ``"Customer Number:"`` label in the
    combined page text. If detected, delegates to ``_transform_sod_pages()``;
    otherwise, follows the existing generic parsing path.

    Args:
        pages: Raw text strings extracted by pdfplumber, one element per PDF page.
        source_file: Optional originating file path stored on the returned Invoice.

    Returns:
        A populated ``Invoice`` instance.
    """
    full_text = "\n".join(pages)

    # Dispatch to the SOD-specific parser when the Customer Number label is present.
    if "Customer Number:" in full_text:
        return _transform_sod_pages(pages, source_file=source_file)

    # Generic parsing path — unchanged for all non-SOD inputs.
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
