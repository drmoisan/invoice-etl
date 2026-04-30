"""Tests for the extract stage."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from invoice_etl.extract.pdf_extractor import extract_text_from_pdf


def test_extract_raises_when_file_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        extract_text_from_pdf(tmp_path / "nonexistent.pdf")


def test_extract_returns_page_texts(tmp_path: Path) -> None:
    fake_pdf = tmp_path / "invoice.pdf"
    fake_pdf.touch()

    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Invoice #001"
    mock_pdf = MagicMock()
    mock_pdf.pages = [mock_page]
    mock_pdf.__enter__ = lambda s: s  # type: ignore[method-assign]
    mock_pdf.__exit__ = MagicMock(return_value=False)

    with patch("invoice_etl.extract.pdf_extractor.pdfplumber.open", return_value=mock_pdf):
        pages = extract_text_from_pdf(fake_pdf)

    assert pages == ["Invoice #001"]
