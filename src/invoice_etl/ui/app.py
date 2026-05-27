"""Flet application entry point for the invoice-etl UI.

This module is the thin view layer.  It wires Flet widget events to
``UIController`` methods and contains no business logic of its own.

This module is intentionally excluded from unit-test coverage because it
requires a live Flet runtime to execute.
"""

from __future__ import annotations

import logging
from pathlib import Path

import flet as ft

from invoice_etl.ui.controller import UIController

logger = logging.getLogger(__name__)


async def main(page: ft.Page) -> None:
    """Configure and render the invoice-etl Flet application page.

    Sets up all controls (two FilePicker services, mode radio group, export
    button, status label) and registers asynchronous event handlers that
    delegate to ``UIController``.

    In Flet 0.24+, ``FilePicker`` is a ``Service`` control (non-visual) and
    must be registered via ``page.services``.  Adding it to ``page.overlay``
    (reserved for visual overlay controls such as dialogs) causes the Flet
    client to attempt a visual render and emit "Unknown control: FilePicker".

    Args:
        page: The Flet ``Page`` object provided by the Flet runtime on startup.

    Flow:
        1. Create a ``UIController`` to hold application state.
        2. Instantiate display controls (status label, path label, radio group).
        3. Create two ``FilePicker`` services — one for input selection, one
           for the save-file dialog — and register both via ``page.services``.
        4. Call ``page.update()`` to propagate service registrations to the
           Flet client before any async handler invokes them.
        5. Register async handlers for pick-file, save-file, mode-change,
           and export.
        6. Build and add the root Column layout to the page.

    Side Effects:
        Mutates *page* by appending two entries to ``page.services`` and
        adding a root Column control.
    """
    page.title = "Invoice ETL"
    page.padding = 30

    controller = UIController()

    # --- Display-only widgets updated by event handlers ---
    status_text = ft.Text(value="", size=14, selectable=True)
    input_path_label = ft.Text(value="No file selected", size=12, italic=True)

    # --- Output mode selector (defaults to database mode) ---
    output_mode_radio = ft.RadioGroup(
        content=ft.Row(
            controls=[
                ft.Radio(value="db", label="Export to PostgreSQL database"),
                ft.Radio(value="excel", label="Export to Excel file"),
            ]
        ),
        value="db",
    )

    # -----------------------------------------------------------------------
    # FilePicker services.
    # FilePicker is a Service control and must be appended to page.services,
    # not page.overlay.  Separate instances are used for input selection and
    # the save-file dialog to avoid any state cross-contamination.
    # page.update() is called immediately after so the client registers both
    # pickers before any async handler tries to invoke them.
    # -----------------------------------------------------------------------
    input_picker = ft.FilePicker()
    save_picker = ft.FilePicker()
    page.services.append(input_picker)
    page.services.append(save_picker)
    page.update()

    # -----------------------------------------------------------------------
    # Event handlers
    # -----------------------------------------------------------------------

    async def on_pick_file_click() -> None:
        """Open the native file-open dialog and update the input-path label.

        Calls ``input_picker.pick_files`` which blocks (awaits) until the user
        selects a file or dismisses the dialog.  An empty or cancelled result
        is silently ignored.
        """
        files = await input_picker.pick_files(
            dialog_title="Select Invoice PDF",
            # file_type must be CUSTOM for allowed_extensions filtering to apply.
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["pdf"],
            allow_multiple=False,
        )
        if files:
            # Use the first (and only) file from single-selection mode.
            chosen = files[0].path
            if chosen:
                controller.set_input_file(Path(chosen))
                input_path_label.value = chosen
                input_path_label.update()

    async def on_export_click() -> None:
        """Dispatch the export action based on the selected output mode.

        Excel mode opens a native save-file dialog via ``save_picker``; the
        ETL pipeline is only invoked after the user confirms a destination
        path.  Passing ``None`` to ``run_export`` (user cancelled) is a
        no-op — the pipeline is not executed.  DB mode runs the pipeline
        immediately without a save dialog.  The status label is updated with
        the human-readable result string from ``UIController.run_export``.
        """
        mode = output_mode_radio.value

        if mode == "excel":
            # save_file blocks until the user confirms or cancels the dialog.
            save_path = await save_picker.save_file(
                dialog_title="Save Invoice as Excel",
                file_name="invoice.xlsx",
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["xlsx"],
            )
            result = controller.run_export(Path(save_path) if save_path else None)
        else:
            # DB mode: no output path required; run the ETL pipeline directly.
            result = controller.run_export()

        status_text.value = result
        status_text.update()

    def on_mode_change() -> None:
        """Sync the controller's output mode with the RadioGroup selection."""
        val = output_mode_radio.value
        # Explicit equality checks allow Pyright to narrow to Literal types.
        if val == "excel":
            controller.set_output_mode("excel")
        else:
            controller.set_output_mode("db")

    # Wire on_change after defining the handler so the closure captures the widget.
    output_mode_radio.on_change = on_mode_change

    # --- Page layout ---
    page.add(
        ft.Column(
            controls=[
                ft.Text("Invoice ETL", size=28, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("1. Select input PDF", size=16, weight=ft.FontWeight.W_500),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            content="Choose PDF...",
                            on_click=on_pick_file_click,
                        ),
                        input_path_label,
                    ],
                    spacing=12,
                ),
                ft.Divider(),
                ft.Text("2. Select output mode", size=16, weight=ft.FontWeight.W_500),
                output_mode_radio,
                ft.Divider(),
                ft.ElevatedButton(
                    content="Export",
                    on_click=on_export_click,
                ),
                ft.Divider(),
                ft.Text("Status", size=14, weight=ft.FontWeight.W_500),
                status_text,
            ],
            spacing=14,
            expand=True,
        )
    )


def run_app() -> None:
    """Launch the Flet desktop application.

    Purpose:
        Provides a named entry point callable by the ``invoice-etl-ui``
        Poetry script.  Delegates to ``ft.run`` which starts the Flet
        event loop and opens a native desktop window.

    Side Effects:
        Blocks the calling process until the Flet window is closed.
    """
    # ft.run's `target` parameter has no type annotation (a deprecated compat
    # param in Flet 0.84), causing reportUnknownMemberType in Pyright strict mode.
    # Suppression is line-specific; all other types in this call are known.
    ft.run(main)  # type: ignore[reportUnknownMemberType]
