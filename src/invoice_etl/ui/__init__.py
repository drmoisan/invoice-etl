"""invoice_etl.ui — Flet-based graphical interface for the invoice-etl pipeline.

This sub-package contains the desktop UI layer, structured as two modules:

- ``controller``: Pure-Python UIController with no Flet dependencies.  All
  business logic lives here and is fully testable with standard pytest mocks.
- ``app``: Thin Flet wiring layer that binds widget events to UIController
  methods.  This module is excluded from unit-test coverage because it requires
  a live Flet runtime.
"""
