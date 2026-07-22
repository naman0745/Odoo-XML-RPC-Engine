"""
gui/widgets/checklist_widget.py
"""
import tkinter as tk
from tkinter import ttk
from typing import Dict


class ChecklistWidget(ttk.Frame):
    """
    Renders the fixed pipeline steps for the progress view.
    Exposes methods to update individual step states.
    Uses ttk styles for theme awareness.
    """
    STEPS = [
        "Reading workbook",
        "Validating columns",
        "Validating rows",
        "Resolving vendor",
        "Resolving products",
        "Creating purchase order",
    ]

    STATE_ICONS = {
        "pending": "○",
        "active": "◌",  # Usually animated, we use static char for now
        "complete": "✓",
        "failed": "✗"
    }

    ICON_STYLES = {
        "pending": "ChecklistIcon.TLabel",
        "active": "ChecklistIcon.Active.TLabel",
        "complete": "ChecklistIcon.Complete.TLabel",
        "failed": "ChecklistIcon.Failed.TLabel"
    }

    TEXT_STYLES = {
        "pending": "ChecklistText.TLabel",
        "active": "ChecklistText.Active.TLabel",
        "complete": "ChecklistText.Complete.TLabel",
        "failed": "ChecklistText.Failed.TLabel"
    }

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        self.columnconfigure(1, weight=1)
        self._rows: list[Dict[str, ttk.Label]] = []

        for i, step_name in enumerate(self.STEPS):
            icon_lbl = ttk.Label(self, text="○", style="ChecklistIcon.TLabel")
            icon_lbl.grid(row=i, column=0, padx=(0, 16), pady=6, sticky="w")

            text_lbl = ttk.Label(self, text=step_name, style="ChecklistText.TLabel")
            text_lbl.grid(row=i, column=1, pady=6, sticky="w")

            self._rows.append({"icon": icon_lbl, "text": text_lbl})

    def set_step_state(self, index: int, state: str) -> None:
        """
        :param index: 0-indexed step number
        :param state: 'pending', 'active', 'complete', or 'failed'
        """
        if index < 0 or index >= len(self._rows):
            return

        row = self._rows[index]
        icon = self.STATE_ICONS.get(state, "○")
        row["icon"].configure(text=icon)

        icon_style = self.ICON_STYLES.get(state, "ChecklistIcon.TLabel")
        text_style = self.TEXT_STYLES.get(state, "ChecklistText.TLabel")

        row["icon"].configure(style=icon_style)
        row["text"].configure(style=text_style)