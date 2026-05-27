"""Tests for invoice_etl.ui.controller.UIController.

All tests use ``unittest.mock.patch`` to replace pipeline functions with
mocks.  No real file I/O, PDF parsing, or database connections are performed.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from invoice_etl.ui.controller import UIController

# ---------------------------------------------------------------------------
# Module-level patch targets — these are the names as imported in controller.py
# ---------------------------------------------------------------------------
_EXTRACT = "invoice_etl.ui.controller.extract_text_from_pdf"
_TRANSFORM = "invoice_etl.ui.controller.transform_pages"
_LOAD_EXCEL = "invoice_etl.ui.controller.load_invoice_to_excel"
_LOAD_DB = "invoice_etl.ui.controller.load_invoice"

# Reusable fake paths for arrange sections
_FAKE_PDF = Path("/fake/invoice.pdf")
_FAKE_XLSX = Path("/fake/output.xlsx")


class TestUIControllerGuardNoInputFile:
    """Tests for run_export when no input file has been set."""

    def test_returns_descriptive_message_when_no_input_file(self) -> None:
        """Verify run_export returns a clear message when _input_file is unset.

        Scenario: Brand-new controller, no set_input_file call, run_export invoked.
        Expected: Returns a string containing 'No input file'.
        """
        # Arrange
        controller = UIController()

        # Act
        result = controller.run_export()

        # Assert
        assert "No input file" in result

    def test_pipeline_not_called_when_no_input_file(self) -> None:
        """Verify no pipeline functions are invoked when the input file guard fires.

        Scenario: run_export called with no input file, all pipeline functions patched.
        Expected: None of the pipeline mocks are called.
        """
        # Arrange
        controller = UIController()

        # Act — patch all pipeline functions to detect unexpected calls
        with (
            patch(_EXTRACT) as mock_extract,
            patch(_TRANSFORM) as mock_transform,
            patch(_LOAD_EXCEL) as mock_load_excel,
            patch(_LOAD_DB) as mock_load_db,
        ):
            controller.run_export()

        # Assert
        mock_extract.assert_not_called()
        mock_transform.assert_not_called()
        mock_load_excel.assert_not_called()
        mock_load_db.assert_not_called()


class TestUIControllerExcelMode:
    """Tests for run_export in Excel output mode."""

    def _make_controller(self) -> UIController:
        """Return a controller configured with a fake PDF input and excel mode."""
        ctrl = UIController()
        ctrl.set_input_file(_FAKE_PDF)
        ctrl.set_output_mode("excel")
        return ctrl

    def test_returns_cancelled_when_output_path_is_none(self) -> None:
        """Verify run_export returns a cancellation message when output_path is None.

        Scenario: Excel mode, output_path=None (user dismissed save dialog).
        Expected: Returns a string containing 'cancelled' (case-insensitive).
        """
        # Arrange
        controller = self._make_controller()

        # Act
        result = controller.run_export(output_path=None)

        # Assert
        assert "cancelled" in result.lower()

    def test_pipeline_not_called_when_output_path_is_none(self) -> None:
        """Verify no pipeline functions run when the user cancels the save dialog.

        Scenario: Excel mode, output_path=None, all pipeline functions patched.
        Expected: None of the pipeline mocks are called.
        """
        # Arrange
        controller = self._make_controller()

        # Act
        with (
            patch(_EXTRACT) as mock_extract,
            patch(_TRANSFORM) as mock_transform,
            patch(_LOAD_EXCEL) as mock_load_excel,
        ):
            controller.run_export(output_path=None)

        # Assert
        mock_extract.assert_not_called()
        mock_transform.assert_not_called()
        mock_load_excel.assert_not_called()

    def test_success_path_calls_pipeline_and_returns_success_message(self) -> None:
        """Verify the full pipeline runs and a success message is returned.

        Scenario: Excel mode, confirmed output_path, all pipeline functions mocked.
        Expected: extract called with input PDF, transform called with pages,
        load_invoice_to_excel called with invoice and output_path, success message
        contains the output path string.
        """
        # Arrange
        controller = self._make_controller()
        mock_invoice = MagicMock()

        with (
            patch(_EXTRACT, return_value=["page text"]) as mock_extract,
            patch(_TRANSFORM, return_value=mock_invoice) as mock_transform,
            patch(_LOAD_EXCEL, return_value=_FAKE_XLSX) as mock_load,
        ):
            # Act
            result = controller.run_export(output_path=_FAKE_XLSX)

        # Assert — each pipeline stage called once with the expected arguments
        mock_extract.assert_called_once_with(_FAKE_PDF)
        mock_transform.assert_called_once_with(["page text"], source_file=str(_FAKE_PDF))
        mock_load.assert_called_once_with(mock_invoice, _FAKE_XLSX)
        assert str(_FAKE_XLSX) in result

    def test_etl_failure_returns_error_string_without_raising(self) -> None:
        """Verify an ETL exception is caught and returned as an error message.

        Scenario: extract_text_from_pdf raises FileNotFoundError.
        Expected: run_export returns a string prefixed 'Error:' containing the
        exception message; no exception propagates to the caller.
        """
        # Arrange
        controller = self._make_controller()

        # Act
        with patch(_EXTRACT, side_effect=FileNotFoundError("PDF not found")):
            result = controller.run_export(output_path=_FAKE_XLSX)

        # Assert
        assert result.startswith("Error:")
        assert "PDF not found" in result


class TestUIControllerDbMode:
    """Tests for run_export in database output mode."""

    def _make_controller(self) -> UIController:
        """Return a controller configured with a fake PDF input and db mode."""
        ctrl = UIController()
        ctrl.set_input_file(_FAKE_PDF)
        ctrl.set_output_mode("db")
        return ctrl

    def test_success_path_calls_pipeline_and_returns_success_message(self) -> None:
        """Verify the full pipeline runs and a success message containing the db id is returned.

        Scenario: DB mode, all pipeline functions mocked, load_invoice returns id=42.
        Expected: extract and transform called once each; load_invoice called once;
        success message contains the returned id.
        """
        # Arrange
        controller = self._make_controller()
        mock_invoice = MagicMock()

        with (
            patch(_EXTRACT, return_value=["page text"]) as mock_extract,
            patch(_TRANSFORM, return_value=mock_invoice) as mock_transform,
            patch(_LOAD_DB, return_value=42) as mock_load_db,
        ):
            # Act
            result = controller.run_export()

        # Assert
        mock_extract.assert_called_once_with(_FAKE_PDF)
        mock_transform.assert_called_once_with(["page text"], source_file=str(_FAKE_PDF))
        mock_load_db.assert_called_once_with(mock_invoice)
        assert "42" in result

    def test_none_output_path_does_not_cancel_db_mode(self) -> None:
        """Verify that passing output_path=None in db mode does not trigger cancellation.

        Scenario: DB mode, output_path=None (no save path needed for DB).
        Expected: run_export does not return a 'cancelled' message.
        """
        # Arrange
        controller = self._make_controller()

        with (
            patch(_EXTRACT, return_value=[]),
            patch(_TRANSFORM, return_value=MagicMock()),
            patch(_LOAD_DB, return_value=0),
        ):
            # Act
            result = controller.run_export(output_path=None)

        # Assert
        assert "cancelled" not in result.lower()

    def test_excel_loader_not_called_in_db_mode(self) -> None:
        """Verify load_invoice_to_excel is never called when mode is 'db'.

        Scenario: DB mode, all pipeline functions patched.
        Expected: load_invoice_to_excel mock is never called.
        """
        # Arrange
        controller = self._make_controller()

        with (
            patch(_EXTRACT, return_value=[]),
            patch(_TRANSFORM, return_value=MagicMock()),
            patch(_LOAD_DB, return_value=0),
            patch(_LOAD_EXCEL) as mock_load_excel,
        ):
            # Act
            controller.run_export()

        # Assert
        mock_load_excel.assert_not_called()

    def test_db_failure_returns_error_string_without_raising(self) -> None:
        """Verify a database exception is caught and returned as an error message.

        Scenario: load_invoice raises RuntimeError.
        Expected: run_export returns a string prefixed 'Error:' containing the
        exception message; no exception propagates.
        """
        # Arrange
        controller = self._make_controller()

        # Act
        with (
            patch(_EXTRACT, return_value=[]),
            patch(_TRANSFORM, return_value=MagicMock()),
            patch(_LOAD_DB, side_effect=RuntimeError("DB connection failed")),
        ):
            result = controller.run_export()

        # Assert
        assert result.startswith("Error:")
        assert "DB connection failed" in result


class TestUIControllerSetterBehavior:
    """Behavioral tests for UIController's state management methods."""

    def test_set_input_file_enables_pipeline_execution(self) -> None:
        """Verify that setting an input file allows run_export to pass the file guard.

        Scenario: set_input_file called, then run_export with mocked pipeline.
        Expected: 'No input file' guard message is NOT returned.
        """
        # Arrange
        controller = UIController()
        controller.set_input_file(_FAKE_PDF)

        with (
            patch(_EXTRACT, return_value=[]),
            patch(_TRANSFORM, return_value=MagicMock()),
            patch(_LOAD_DB, return_value=0),
        ):
            # Act
            result = controller.run_export()

        # Assert
        assert "No input file" not in result

    def test_set_output_mode_excel_enables_cancel_on_none_path(self) -> None:
        """Verify that switching to excel mode causes None output_path to cancel.

        Scenario: set_output_mode("excel") called, then run_export(output_path=None).
        Expected: 'cancelled' appears in the returned message.
        """
        # Arrange
        controller = UIController()
        controller.set_input_file(_FAKE_PDF)
        controller.set_output_mode("excel")

        # Act
        result = controller.run_export(output_path=None)

        # Assert
        assert "cancelled" in result.lower()

    def test_mode_toggle_from_excel_back_to_db(self) -> None:
        """Verify toggling from excel mode back to db mode works correctly.

        Scenario: Set excel, then set db, then run_export(output_path=None).
        Expected: 'cancelled' does NOT appear (db mode ignores output_path).
        """
        # Arrange
        controller = UIController()
        controller.set_input_file(_FAKE_PDF)
        controller.set_output_mode("excel")
        controller.set_output_mode("db")  # Toggle back

        with (
            patch(_EXTRACT, return_value=[]),
            patch(_TRANSFORM, return_value=MagicMock()),
            patch(_LOAD_DB, return_value=0),
        ):
            # Act
            result = controller.run_export(output_path=None)

        # Assert — db mode should succeed even without an output path
        assert "cancelled" not in result.lower()

    def test_default_mode_is_db(self) -> None:
        """Verify UIController defaults to 'db' output mode.

        Scenario: Fresh controller, no set_output_mode call, run_export with mocked pipeline.
        Expected: load_invoice (DB loader) is called, not load_invoice_to_excel.
        """
        # Arrange
        controller = UIController()
        controller.set_input_file(_FAKE_PDF)

        with (
            patch(_EXTRACT, return_value=[]),
            patch(_TRANSFORM, return_value=MagicMock()),
            patch(_LOAD_DB, return_value=0) as mock_db,
            patch(_LOAD_EXCEL) as mock_excel,
        ):
            # Act
            controller.run_export()

        # Assert
        mock_db.assert_called_once()
        mock_excel.assert_not_called()
