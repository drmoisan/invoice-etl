"""Pydantic v2 models for invoices and line items."""

from __future__ import annotations

import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class LineItem(BaseModel):
    """A single line-item row extracted from an invoice.

    Carries common fields present in all invoice formats as well as SOD-specific
    fields that are only populated when the SOD parsing path is used.

    Attributes:
        description: Human-readable product description.
        quantity: Number of units ordered.
        unit_price: Per-unit price.
        line_total: Extended price (quantity × unit_price).
        item: Five-digit SKU / item code (SOD format only).
        store_number: Five-digit zero-padded store code (SOD format only).
        order_date: Store order date (SOD format only).
        offer_number: Deal / offer identifier (SOD format only).
        unit_of_measure: Uppercase unit abbreviation, e.g. "EA" or "CS" (SOD format only).
    """

    description: str | None = None
    """Human-readable product description."""
    quantity: Decimal | None = None
    """Number of units ordered."""
    unit_price: Decimal | None = None
    """Per-unit price."""
    line_total: Decimal | None = None
    """Extended price (quantity × unit_price)."""
    item: str | None = None
    """Five-digit SKU / item code — populated by the SOD parser."""
    store_number: str | None = None
    """Five-digit zero-padded store code — populated by the SOD parser."""
    order_date: datetime.date | None = None
    """Store order date converted from MM/DD/YYYY — populated by the SOD parser."""
    offer_number: str | None = None
    """Deal / offer identifier — populated by the SOD parser."""
    unit_of_measure: str | None = None
    """Uppercase unit-of-measure abbreviation, e.g. "EA" or "CS" — populated by the SOD parser."""


class Invoice(BaseModel):
    """A fully structured invoice record assembled by the transform stage.

    Attributes:
        invoice_number: Unique document identifier (required).
        invoice_date: Issue date of the invoice.
        due_date: Payment due date.
        vendor_name: Selling entity name.
        vendor_address: Selling entity address.
        customer_name: Buying entity name.
        customer_address: Buying entity address.
        customer_number: Buying entity account identifier (SOD format only).
        currency: ISO-4217 currency code (max 3 chars).
        subtotal: Pre-tax total.
        tax_amount: Tax portion.
        total_amount: Grand total including tax.
        line_items: Ordered list of individual line-item records.
        source_file: Originating file path for traceability.
    """

    invoice_number: str
    """Unique document identifier; required for database upsert."""
    invoice_date: datetime.date | None = None
    """Issue date of the invoice."""
    due_date: datetime.date | None = None
    """Payment due date."""
    vendor_name: str | None = None
    """Selling entity name."""
    vendor_address: str | None = None
    """Selling entity address."""
    customer_name: str | None = None
    """Buying entity name."""
    customer_address: str | None = None
    """Buying entity address."""
    customer_number: str | None = None
    """Buying entity account identifier — populated by the SOD parser."""
    currency: str | None = Field(default=None, max_length=3)
    """ISO-4217 currency code (max 3 chars)."""
    subtotal: Decimal | None = None
    """Pre-tax total."""
    tax_amount: Decimal | None = None
    """Tax portion."""
    total_amount: Decimal | None = None
    """Grand total including tax."""
    line_items: list[LineItem] = []
    """Ordered list of individual line-item records."""
    source_file: str | None = None
    """Originating file path for traceability."""
