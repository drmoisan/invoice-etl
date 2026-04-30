-- Invoice ETL — initial schema

CREATE TABLE IF NOT EXISTS invoices (
    id              SERIAL PRIMARY KEY,
    invoice_number  TEXT        NOT NULL UNIQUE,
    invoice_date    DATE,
    due_date        DATE,
    vendor_name     TEXT,
    vendor_address  TEXT,
    customer_name   TEXT,
    customer_address TEXT,
    currency        CHAR(3),
    subtotal        NUMERIC(18, 2),
    tax_amount      NUMERIC(18, 2),
    total_amount    NUMERIC(18, 2),
    source_file     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS line_items (
    id              SERIAL PRIMARY KEY,
    invoice_id      INTEGER     NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    description     TEXT,
    quantity        NUMERIC(18, 4),
    unit_price      NUMERIC(18, 4),
    line_total      NUMERIC(18, 2),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_line_items_invoice_id ON line_items(invoice_id);
