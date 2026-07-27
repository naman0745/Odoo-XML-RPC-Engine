"""
gui/widgets/status_bar.py
"""
import tkinter as tk
from tkinter import ttk
from gui import APP_VERSION


class StatusBar(ttk.Frame):
    """
    Thin strip anchored to the bottom. Shows version, last import,
    and supplementary actions like configure folders or view logs.
    """
    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, style="Footer.TFrame")
        self.columnconfigure(1, weight=1)  # spacer

        self._version_lbl = ttk.Label(self, text=APP_VERSION, style="Footer.TLabel")
        self._version_lbl.grid(row=0, column=0, padx=16, pady=4, sticky="w")

        # Optional center text (e.g., Last import timestamp)
        self._last_import_lbl = ttk.Label(self, text="Last import: —", style="Footer.TLabel")
        self._last_import_lbl.grid(row=0, column=1, pady=4)

        # Action Links
        self._log_lbl = ttk.Label(self, text="View Log", style="Footer.TLabel", cursor="hand2")
        self._log_lbl.grid(row=0, column=2, padx=(0, 16), pady=4, sticky="e")

    def set_last_import(self, text: str) -> None:
        """Updates the last import label."""
        self._last_import_lbl.configure(text=text)
