"""Deprecated GUI module.

The interactive Tk GUI was removed at the user's request. Use
``day08.excel_calibrate`` to compute calibrations and write native Excel
charts instead.

This module is a light stub so imports like ``from day08 import gui`` will
continue to work but the GUI functionality no longer exists.
"""

def gui_removed(*args, **kwargs):
    raise RuntimeError(
        "The day08 GUI has been removed. Run 'python -m day08.excel_calibrate' instead to create Excel charts."
    )

__all__ = ["gui_removed"]
