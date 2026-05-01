"""Entry point — run the full ETL pipeline for one or more PDF files."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Literal, cast

from dotenv import load_dotenv

from invoice_etl.extract.pdf_extractor import extract_text_from_pdf
from invoice_etl.load.db_loader import load_invoice
from invoice_etl.load.excel_loader import load_invoice_to_excel
from invoice_etl.transform.invoice_transformer import transform_pages

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Valid output mode literals used by both run() and main().
OutputMode = Literal["db", "excel"]


def run(pdf_paths: list[Path], *, output: OutputMode = "db") -> None:
    """Execute the ETL pipeline for each PDF in *pdf_paths*.

    Args:
        pdf_paths: List of PDF file paths to process.
        output: Destination for the transformed invoice data.  ``"db"`` (default)
            writes to PostgreSQL via :func:`load_invoice`; ``"excel"`` writes a
            ``.xlsx`` file via :func:`load_invoice_to_excel`.
    """
    for path in pdf_paths:
        logger.info("Processing %s", path.name)
        pages = extract_text_from_pdf(path)
        invoice = transform_pages(pages, source_file=str(path))

        # Route to the appropriate loader based on the requested output mode.
        if output == "excel":
            excel_path = load_invoice_to_excel(invoice, path.with_suffix(".xlsx"))
            logger.info("Invoice %s → %s", invoice.invoice_number, excel_path)
        else:
            invoice_id = load_invoice(invoice)
            if invoice_id > 0:
                logger.info("Invoice %s → db id %d", invoice.invoice_number, invoice_id)


def main() -> None:
    """Parse CLI arguments and invoke :func:`run` for each supplied PDF path."""
    parser = argparse.ArgumentParser(
        prog="invoice-etl",
        description="Extract, transform, and load invoice PDF data.",
    )
    parser.add_argument("pdfs", nargs="*", metavar="PDF", help="Input PDF file paths")
    parser.add_argument(
        "--output",
        choices=["db", "excel"],
        default="db",
        help="Output destination: db (default) writes to PostgreSQL; excel writes .xlsx",
    )
    args = parser.parse_args()

    # Preserve the original usage message format expected by callers and tests.
    if not args.pdfs:
        print("Usage: invoice-etl <path/to/invoice.pdf> [...]")
        sys.exit(1)

    # argparse choices enforcement guarantees args.output is a valid OutputMode.
    output_mode = cast(OutputMode, args.output)
    run([Path(p) for p in args.pdfs], output=output_mode)


if __name__ == "__main__":
    main()
