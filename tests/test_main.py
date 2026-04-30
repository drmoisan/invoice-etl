"""Tests for the CLI entry point and orchestration in ``invoice_etl.main``."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import call, patch

import pytest

from invoice_etl.main import main, run
from invoice_etl.models.invoice import Invoice


def _make_invoice(invoice_number: str) -> Invoice:
    """Return a minimal Invoice model for orchestration tests.

    Purpose:
        Build a real Invoice instance so the entry-point tests can verify
        logging and loader handoff behavior without relying on loosely typed
        mocks.

    Args:
        invoice_number (str): Unique invoice identifier exposed by the
            transformed invoice.

    Returns:
        Invoice: A minimal model instance suitable for CLI orchestration tests.

    Raises:
        None.

    Side Effects:
        None.
    """
    return Invoice(invoice_number=invoice_number)


def test_run_processes_each_path_and_passes_source_file_to_transform() -> None:
    """run orchestrates extract, transform, and load for each provided PDF path."""
    # Arrange: prepare two PDF paths and deterministic stage outputs.
    pdf_paths = [Path("first.pdf"), Path("nested/second.pdf")]
    page_batches = [["page one"], ["page two"]]
    invoices = [_make_invoice("INV-001"), _make_invoice("INV-002")]

    with (
        patch("invoice_etl.main.extract_text_from_pdf", side_effect=page_batches) as extract_mock,
        patch("invoice_etl.main.transform_pages", side_effect=invoices) as transform_mock,
        patch("invoice_etl.main.load_invoice", side_effect=[101, 102]) as load_mock,
    ):
        # Act: run the end-to-end orchestration loop for both paths.
        run(pdf_paths)

    # Assert: every stage receives the expected per-file inputs and outputs.
    assert extract_mock.call_args_list == [call(pdf_paths[0]), call(pdf_paths[1])]
    assert transform_mock.call_args_list == [
        call(page_batches[0], source_file=str(pdf_paths[0])),
        call(page_batches[1], source_file=str(pdf_paths[1])),
    ]
    assert load_mock.call_args_list == [call(invoices[0]), call(invoices[1])]


def test_run_logs_loaded_invoice_when_loader_returns_positive_id() -> None:
    """run emits the success log when the loader returns a positive database id."""
    # Arrange: create a single successful invoice flow.
    invoice = _make_invoice("INV-001")

    with (
        patch("invoice_etl.main.extract_text_from_pdf", return_value=["page one"]),
        patch("invoice_etl.main.transform_pages", return_value=invoice),
        patch("invoice_etl.main.load_invoice", return_value=42),
        patch("invoice_etl.main.logger.info") as logger_info,
    ):
        # Act: process one input file through the orchestrator.
        run([Path("invoice.pdf")])

    # Assert: the positive insert id triggers the success log entry.
    assert call("Invoice %s → db id %d", "INV-001", 42) in logger_info.call_args_list


def test_run_does_not_log_loaded_invoice_when_loader_returns_minus_one() -> None:
    """run skips the success log when the loader reports a duplicate invoice."""
    # Arrange: create a duplicate-load outcome that should not log success.
    invoice = _make_invoice("INV-001")

    with (
        patch("invoice_etl.main.extract_text_from_pdf", return_value=["page one"]),
        patch("invoice_etl.main.transform_pages", return_value=invoice),
        patch("invoice_etl.main.load_invoice", return_value=-1),
        patch("invoice_etl.main.logger.info") as logger_info,
    ):
        # Act: process one file whose database insert is skipped.
        run([Path("invoice.pdf")])

    # Assert: only the processing log is emitted for the duplicate path.
    assert logger_info.call_args_list == [call("Processing %s", "invoice.pdf")]


def test_main_prints_usage_and_exits_when_no_pdf_args() -> None:
    """main prints usage and exits with code 1 when no PDF paths are supplied."""
    # Arrange: simulate invocation without any positional PDF arguments.
    with (
        patch("invoice_etl.main.sys.argv", ["invoice-etl"]),
        patch("builtins.print") as print_mock,
        patch("invoice_etl.main.run") as run_mock,
        patch("invoice_etl.main.sys.exit", side_effect=SystemExit(1)) as exit_mock,
        pytest.raises(SystemExit) as exc_info,
    ):
        # Act / Assert: main should stop immediately after printing usage.
        main()

    assert exc_info.value.code == 1
    assert print_mock.call_args_list == [call("Usage: invoice-etl <path/to/invoice.pdf> [...]")]
    exit_mock.assert_called_once_with(1)
    run_mock.assert_not_called()


def test_main_builds_path_objects_from_argv_and_delegates_to_run() -> None:
    """main converts argv strings to Path objects before delegating to run."""
    # Arrange: simulate two CLI path arguments.
    expected_paths = [Path("first.pdf"), Path("nested/second.pdf")]

    with (
        patch("invoice_etl.main.sys.argv", ["invoice-etl", "first.pdf", "nested/second.pdf"]),
        patch("invoice_etl.main.run") as run_mock,
    ):
        # Act: invoke the CLI entry point.
        main()

    # Assert: run receives the exact Path objects derived from argv.
    run_mock.assert_called_once_with(expected_paths)
