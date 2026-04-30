"""PDF extraction — reads raw text blocks from invoice PDFs."""

from __future__ import annotations

import logging
from pathlib import Path

import pdfplumber

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: Path) -> list[str]:
    """Return a list of page text strings extracted from *pdf_path*.

    Raises:
        FileNotFoundError: If *pdf_path* does not exist.
        ValueError: If the file is not a readable PDF.
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    pages: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            pages.append(text)

    logger.debug("Extracted %d page(s) from %s", len(pages), pdf_path.name)
    return pages
