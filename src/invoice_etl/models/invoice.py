"""Pydantic v2 models for invoices and line items."""

from __future__ import annotations

import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class LineItem(BaseModel):
    description: str | None = None
    quantity: Decimal | None = None
    unit_price: Decimal | None = None
    line_total: Decimal | None = None


class Invoice(BaseModel):
    invoice_number: str
    invoice_date: datetime.date | None = None
    due_date: datetime.date | None = None
    vendor_name: str | None = None
    vendor_address: str | None = None
    customer_name: str | None = None
    customer_address: str | None = None
    currency: str | None = Field(default=None, max_length=3)
    subtotal: Decimal | None = None
    tax_amount: Decimal | None = None
    total_amount: Decimal | None = None
    line_items: list[LineItem] = Field(default_factory=list)
    source_file: str | None = None
