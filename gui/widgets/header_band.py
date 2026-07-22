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
        self._status_lbl.grid(row=0, column=2, padx=10, pady=8, sticky="e")

        # Gear Icon (Settings)
        # Using a unicode char for gear. No logic hooked up yet.
        self._gear_btn = ttk.Label(self, text="⚙", style="Ghost.TLabel", cursor="hand2")
        self._gear_btn.grid(row=0, column=3, padx=(0, 16), pady=8, sticky="e")

    def set_connection_status(self, connected: bool, errored: bool = False) -> None:
        """
        Update the connection status badge.
        :param connected: True if connected, False if disconnected.
        :param errored: True if the most recent check triggered a hard failure.
        """
        if errored:
            self._status_lbl.configure(text="● Connection check failed", style="Error.TLabel")
        elif connected:
            self._status_lbl.configure(text="● Connected to Odoo", style="Connected.TLabel")
        else:
            self._status_lbl.configure(text="○ Not Connected", style="Warning.TLabel")
