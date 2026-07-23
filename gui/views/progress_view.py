"""
gui/views/progress_view.py
"""
import tkinter as tk
from tkinter import ttk

from gui.widgets.checklist_widget import ChecklistWidget


class ProgressView(ttk.Frame):
    """
    Shows a 6-step progress checklist for the pipeline.
    Passive view updated by GUI controller. 
    Does not contain simulated timer logic.
    """
    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)

        # Header: Filename
        self.filename_lbl = ttk.Label(self, text="", style="Bold.TLabel")
        self.filename_lbl.pack(anchor="w", padx=32, pady=(32, 16))

        # Checklist Widget
        self.checklist = ChecklistWidget(self)
        self.checklist.pack(fill="x", padx=32)

        # Progress Bar & text
        progress_frame = ttk.Frame(self)
        progress_frame.pack(fill="x", padx=32, pady=24)
        
        self.pbar = ttk.Progressbar(progress_frame, mode="determinate", maximum=6, style="TProgressbar")
        self.pbar.pack(side="left", fill="x", expand=True, padx=(0, 16))

        self.step_lbl = ttk.Label(progress_frame, text="(0 of 6)", style="Muted.TLabel")
        self.step_lbl.pack(side="right")

    def set_filename(self, filename: str) -> None:
        self.filename_lbl.configure(text=filename)

    def reset(self) -> None:
        for i in range(6):
            self.checklist.set_step_state(i, "pending")
        self.pbar.configure(value=0)
        self.step_lbl.configure(text="(0 of 6)")

    def update_step(self, step_idx: int, state: str) -> None:
        self.checklist.set_step_state(step_idx, state)
        if state == "complete":
            self.pbar.configure(value=step_idx + 1)
            self.step_lbl.configure(text=f"({step_idx + 1} of 6)")
