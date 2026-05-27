"""UIController — pure-Python business logic coordinator for the invoice-etl UI.

This module has zero Flet imports and is fully testable with standard pytest
mocks via ``unittest.mock.patch``.
"""

from __future__ import annotations

import logging
from pathlib import Path

from invoice_etl.extract.pdf_extractor import extract_text_from_pdf
from invoice_etl.load.db_loader import load_invoice
from invoice_etl.load.excel_loader import load_invoice_to_excel
from invoice_etl.main import OutputMode
from invoice_etl.transform.invoice_transformer import transform_pages

logger = logging.getLogger(__name__)


class UIController:
    """Coordinates user selections and ETL pipeline execution for the UI layer.

    Purpose:
        Acts as the single source of truth for the user's current input file
        and desired export mode.  Executes the full ETL pipeline when
        ``run_export`` is called and returns a human-readable status string for
        every outcome.

    Usage:
        controller = UIController()
        controller.set_input_file(Path("invoice.pdf"))
        controller.set_output_mode("excel")
        message = controller.run_export(output_path=Path("output.xlsx"))

    Flow:
        1. Caller sets ``_input_file`` via ``set_input_file``.
        2. Caller sets ``_output_mode`` via ``set_output_mode`` (defaults to "db").
        3. Caller invokes ``run_export``; the controller validates state, then
           runs extract → transform → load in sequence.
        4. ``run_export`` always returns a descriptive string — it never raises.

    Invariants / Constraints:
        - Zero Flet imports; safe to instantiate in any test or headless context.
        - ``run_export`` catches all exceptions from pipeline functions and
          surfaces them as prefixed error strings rather than re-raising.

    Side Effects:
        - Excel mode: writes a ``.xlsx`` file to the given output path.
        - DB mode: inserts rows into a PostgreSQL database.

    Attributes:
        _input_file (Path | None): PDF path selected by the user.
        _output_mode (OutputMode): Current export mode, defaults to ``"db"``.
    """

    def __init__(self) -> None:
        """Initialise the controller with no input file and ``"db"`` output mode."""
        self._input_file: Path | None = None
        self._output_mode: OutputMode = "db"

    def set_input_file(self, path: Path) -> None:
        """Store the PDF file path chosen by the user.

        Args:
            path: Absolute or relative path to the input PDF invoice.

        Side Effects:
            Updates ``_input_file`` state.
        """
        self._input_file = path
        logger.debug("Input file set: %s", path)

    def set_output_mode(self, mode: OutputMode) -> None:
        """Store the user's desired export mode.

        Args:
            mode: ``"db"`` to load into PostgreSQL or ``"excel"`` to write
                an ``.xlsx`` file.

        Side Effects:
            Updates ``_output_mode`` state.
        """
        self._output_mode = mode
        logger.debug("Output mode set: %s", mode)

    def run_export(self, output_path: Path | None = None) -> str:
        """Execute the ETL pipeline with the current selections and return a status string.

        Validates that an input file has been set, then routes to the appropriate
        pipeline sequence.  In Excel mode, a missing *output_path* is treated as
        a user cancellation and the pipeline is never executed.  In DB mode the
        pipeline always runs when an input file is present.

        Args:
            output_path: Destination ``.xlsx`` path, required only when
                ``_output_mode`` is ``"excel"``.  Passing ``None`` in Excel
                mode is treated as a user cancellation — the pipeline is not
                executed.

        Returns:
            A human-readable status string.  Possible outcomes:

            - ``"No input file selected. ..."`` — no input file was set.
            - ``"Export cancelled."`` — Excel mode with ``output_path=None``.
            - ``"Invoice exported successfully to: <path>"`` — Excel success.
            - ``"Invoice loaded to database (id=<n>)."`` — DB success.
            - ``"Error: <message>"`` — any exception raised by the pipeline.

        Side Effects:
            May write a ``.xlsx`` file to disk or insert rows into a database.
        """
        # Guard: the user must have chosen an input file before exporting.
        if self._input_file is None:
            return "No input file selected. Please choose a PDF file first."

        try:
            if self._output_mode == "excel":
                # Guard: treat a missing save path as a user cancellation, before
                # running any expensive pipeline stages.
                if output_path is None:
                    return "Export cancelled."
                # Stage 1–2: extract and transform.
                pages = extract_text_from_pdf(self._input_file)
                invoice = transform_pages(pages, source_file=str(self._input_file))
                # Stage 3 (Excel): write the Invoice to an .xlsx file.
                # output_path is narrowed to Path by the guard above.
                written = load_invoice_to_excel(invoice, output_path)
                return f"Invoice exported successfully to: {written}"

            # DB mode: run all three pipeline stages and load to PostgreSQL.
            pages = extract_text_from_pdf(self._input_file)
            invoice = transform_pages(pages, source_file=str(self._input_file))
            invoice_id = load_invoice(invoice)
            return f"Invoice loaded to database (id={invoice_id})."

        except Exception as exc:  # intentional catch-all; surfaces as user-visible message
            logger.error("Export failed: %s", exc, exc_info=True)
            return f"Error: {exc}"
