"""Entry point — run the full ETL pipeline for one or more PDF files."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

from invoice_etl.extract.pdf_extractor import extract_text_from_pdf
from invoice_etl.load.db_loader import load_invoice
from invoice_etl.transform.invoice_transformer import transform_pages

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def run(pdf_paths: list[Path]) -> None:
    """Execute the ETL pipeline for each PDF in *pdf_paths*."""
    for path in pdf_paths:
        logger.info("Processing %s", path.name)
        pages = extract_text_from_pdf(path)
        invoice = transform_pages(pages, source_file=str(path))
        invoice_id = load_invoice(invoice)
        if invoice_id > 0:
            logger.info("Invoice %s → db id %d", invoice.invoice_number, invoice_id)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: invoice-etl <path/to/invoice.pdf> [...]")
        sys.exit(1)
    run([Path(p) for p in sys.argv[1:]])


if __name__ == "__main__":
    main()
