"""
gui/views/resolution_modal.py
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable
from gui.style import FONT_REGULAR_12, FONT_REGULAR_13, FONT_MEDIUM_14

class ResolutionModal(tk.Toplevel):
    """
    A modal window that allows users to resolve ambiguous product matches.
    """
    def __init__(self, parent: tk.Tk, ambiguities: list[dict], on_apply: Callable[[dict], None]):
        super().__init__(parent)
        self.title("Resolve Ambiguous Products")
        self.geometry("640x400")
        self.transient(parent)
        self.grab_set()
        
        self._ambiguities = ambiguities
        self._on_apply = on_apply
        self._comboboxes = {} # Maps original_code -> (Combobox, list of candidate dicts)
        
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.configure(bg="#0D0D0D")
        
        self._build_ui()
        
    def _build_ui(self) -> None:
        header = ttk.Label(
            self,
            text="The following Vendor Style Numbers were not found exactly but had close matches.\nPlease select the correct Odoo products below to retry the import.",
            font=FONT_REGULAR_12
        )
        header.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        frame = ttk.Frame(self, style="TFrame")
        frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=5)
        frame.columnconfigure(1, weight=1)
        
        ttk.Label(frame, text="Original Excel Value", font=FONT_MEDIUM_14).grid(row=0, column=0, sticky="w", pady=5)
        ttk.Label(frame, text="Suggested Odoo Match", font=FONT_MEDIUM_14).grid(row=0, column=1, sticky="w", pady=5)
        
        # Build rows for each ambiguity
        for i, item in enumerate(self._ambiguities, start=1):
            original_code = item["original_code"]
            color = item["color"]
            candidates = item["candidates"]
            mapping_key = item["mapping_key"]
            
            lbl_text = f"Row {item['row']}: {original_code}"
            if color:
                lbl_text += f" ({color})"
            ttk.Label(frame, text=lbl_text).grid(row=i, column=0, sticky="w", pady=5, padx=(0, 20))
            
            cb_values = [f"[{c.get('x_vendor_code', '')}] {c.get('name', '')}" for c in candidates]
            
            cb = ttk.Combobox(frame, values=cb_values, state="readonly", width=40)
            cb.grid(row=i, column=1, sticky="ew", pady=5)
            if cb_values:
                cb.current(0)
            self._comboboxes[mapping_key] = (cb, candidates)
            
        btn_frame = ttk.Frame(self, style="TFrame")
        btn_frame.grid(row=2, column=0, sticky="e", padx=20, pady=15)
        
        apply_btn = ttk.Button(btn_frame, text="Apply Fixes & Retry", command=self._handle_apply, style="Primary.TButton")
        apply_btn.pack(side="right", padx=5)
        
        cancel_btn = ttk.Button(btn_frame, text="Cancel", command=self.destroy)
        cancel_btn.pack(side="right", padx=5)

    def _handle_apply(self) -> None:
        user_mappings = {}
        for mapping_key, (cb, candidates) in self._comboboxes.items():
            selected_idx = cb.current()
            if selected_idx >= 0:
                user_mappings[mapping_key] = candidates[selected_idx]
        
        self.destroy()
        self._on_apply(user_mappings)
