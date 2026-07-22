"""
gui/widgets/checklist_widget.py
"""
import tkinter as tk
from tkinter import ttk
from typing import Dict

from gui.style import ThemeColors


class ChecklistWidget(ttk.Frame):
    """
    Renders the fixed pipeline steps for the progress view.
    Exposes methods to update individual step states.
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

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        self.columnconfigure(1, weight=1)
        self._rows: list[Dict[str, tk.Label]] = []

        for i, step_name in enumerate(self.STEPS):
            icon_lbl = tk.Label(self, text="○", font=("Segoe UI", 12), bg=ThemeColors["BG_MAIN"], fg=ThemeColors["FG_MUTED"])
            icon_lbl.grid(row=i, column=0, padx=(0, 16), pady=6, sticky="w")
            
            text_lbl = tk.Label(self, text=step_name, font=("Segoe UI", 12), bg=ThemeColors["BG_MAIN"], fg=ThemeColors["FG_MUTED"])
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

        if state == "pending":
            color = ThemeColors["FG_MUTED"]
        elif state == "active":
            color = ThemeColors["ACCENT_BLUE"]
        elif state == "complete":
            color = ThemeColors["GREEN_ACCENT"]
        elif state == "failed":
            color = ThemeColors["RED_FAILED"]
        else:
            color = ThemeColors["FG_MAIN"]

        # When complete, text remains standard slate.
        text_color = color if state in ("active", "failed") else ThemeColors["FG_MAIN"]
        if state == "pending":
            text_color = ThemeColors["FG_MUTED"]

        row["icon"].configure(fg=color)
        row["text"].configure(fg=text_color)
