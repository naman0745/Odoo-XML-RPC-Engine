"""
gui/widgets/header_band.py
"""
import tkinter as tk
from tkinter import ttk


class HeaderBand(ttk.Frame):
    """
    Fixed header band beneath the title bar. Contains application name,
    connection status indicator, and settings icon.
    """
    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, style="Header.TFrame")
        self.columnconfigure(1, weight=1)  # spacer

        # App Logo / Title
        self._title_lbl = ttk.Label(self, text="◆ PO Importer", font=("Segoe UI", 12, "bold"))
        self._title_lbl.grid(row=0, column=0, padx=16, pady=8, sticky="w")

        # Connection Indicator (Default to Checked/Connected)
        self._status_lbl = ttk.Label(self, text="● Connected to Odoo", style="Connected.TLabel")
        self._status_lbl.grid(row=0, column=2, pady=8, sticky="e")

        # Logout Power Button
        self.logout_btn = ttk.Label(self, text="⏻", font=("Segoe UI", 12), cursor="hand2")
        self.logout_btn.grid(row=0, column=3, padx=(8, 16), pady=8, sticky="e")

    def set_connection_status(self, connected: bool, errored: bool = False) -> None:
        """
        Update the connection status badge.
        :param connected: True if connected, False if disconnected.
        :param errored: True if the most recent check triggered a hard failure.
        """
        if errored:
            self._status_lbl.configure(text="● Connection check failed", style="Error.TLabel")
            self.logout_btn.grid()
        elif connected:
            self._status_lbl.configure(text="● Connected to Odoo", style="Connected.TLabel")
            self.logout_btn.grid()
        else:
            self._status_lbl.configure(text="○ Not Connected", style="Warning.TLabel")
            self.logout_btn.grid_remove()
