"""Load validated Invoice models into PostgreSQL via SQLAlchemy."""

from __future__ import annotations

import logging
import os

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from invoice_etl.models.invoice import Invoice

logger = logging.getLogger(__name__)


def _get_engine() -> Engine:
    """Build a SQLAlchemy engine from environment variables."""
    host = os.environ["POSTGRES_HOST"]
    port = os.environ.get("POSTGRES_PORT", "5432")
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]
    db = os.environ["POSTGRES_DB"]
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    return create_engine(url, pool_pre_ping=True)


def load_invoice(invoice: Invoice, engine: Engine | None = None) -> int:
    """Insert *invoice* (and its line items) into the database.

    Returns:
        The newly created invoice row ``id``.
    """
    if engine is None:
        engine = _get_engine()

    with engine.begin() as conn:
        result = conn.execute(
            text(
                """
                INSERT INTO invoices (
                    invoice_number, invoice_date, due_date,
                    vendor_name, vendor_address,
                    customer_name, customer_address, customer_number,
                    currency, subtotal, tax_amount, total_amount, source_file
                ) VALUES (
                    :invoice_number, :invoice_date, :due_date,
                    :vendor_name, :vendor_address,
                    :customer_name, :customer_address, :customer_number,
                    :currency, :subtotal, :tax_amount, :total_amount, :source_file
                )
                ON CONFLICT (invoice_number) DO NOTHING
                RETURNING id
                """
            ),
            invoice.model_dump(exclude={"line_items"}),
        )
        row = result.fetchone()
        if row is None:
            logger.warning("Invoice %s already exists — skipped.", invoice.invoice_number)
            return -1

        invoice_id: int = row[0]

        for item in invoice.line_items:
            conn.execute(
                text(
                    """
                    INSERT INTO line_items (
                        invoice_id, description, quantity, unit_price, line_total,
                        item, store_number, order_date, offer_number, unit_of_measure
                    ) VALUES (
                        :invoice_id, :description, :quantity, :unit_price, :line_total,
                        :item, :store_number, :order_date, :offer_number, :unit_of_measure
                    )
                    """
                ),
                {"invoice_id": invoice_id, **item.model_dump()},
            )

    logger.info("Loaded invoice %s (id=%d)", invoice.invoice_number, invoice_id)
    return invoice_id
