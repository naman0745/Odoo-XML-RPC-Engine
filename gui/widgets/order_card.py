"""
gui/widgets/order_card.py
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from gui.models.ui_models import PendingOrderInfo
from gui.style import ThemeColors


class OrderCard(tk.Frame):
    """
    A single clickable card representing a pending purchase order.
    Takes structured PendingOrderInfo data.
    """
    def __init__(self, parent: tk.Widget, order_info: PendingOrderInfo, on_click: Callable[['OrderCard', PendingOrderInfo], None]) -> None:
        # Use tk.Frame rather than ttk.Frame for easier background & border manipulation
        super().__init__(parent, bg=ThemeColors["BG_MAIN"], highlightbackground=ThemeColors["BORDER_SLATE"], highlightthickness=1)
        self.order_info = order_info
        self.on_click = on_click
        self.is_selected = False

        self.columnconfigure(1, weight=1)

        # File Icon
        self._icon_lbl = tk.Label(self, text="📄", font=("Segoe UI", 16), bg=ThemeColors["BG_MAIN"])
        self._icon_lbl.grid(row=0, column=0, rowspan=2, padx=(16, 12), pady=16, sticky="n")

        # Filename
        self._filename_lbl = ttk.Label(self, text=order_info.filename, style="Bold.TLabel")
        self._filename_lbl.grid(row=0, column=1, sticky="w", pady=(16, 0))

        # Metadata
        meta_text = f"{order_info.size_kb} KB · Modified {order_info.modified_date} · {order_info.full_path.parent}"
        self._meta_lbl = ttk.Label(self, text=meta_text, style="Muted.TLabel")
        self._meta_lbl.grid(row=1, column=1, sticky="w", pady=(2, 16))

        # Bind events
        self._bind_events()

    def _bind_events(self) -> None:
        for widget in (self, self._icon_lbl, self._filename_lbl, self._meta_lbl):
            widget.bind("<Button-1>", self._on_click_handler)
            widget.bind("<Enter>", self._on_hover_in)
            widget.bind("<Leave>", self._on_hover_out)

    def _on_click_handler(self, event: tk.Event) -> None:
        self.on_click(self, self.order_info)

    def _on_hover_in(self, event: tk.Event) -> None:
        if not self.is_selected:
            self.configure(highlightbackground=ThemeColors["FG_MUTED"])

    def _on_hover_out(self, event: tk.Event) -> None:
        if not self.is_selected:
            self.configure(highlightbackground=ThemeColors["BORDER_SLATE"])

    def set_selected(self, selected: bool) -> None:
        self.is_selected = selected
        if selected:
            self.configure(highlightbackground=ThemeColors["ACCENT_BLUE"], highlightthickness=2, bg=ThemeColors["ACCENT_TINT"])
            self._icon_lbl.configure(bg=ThemeColors["ACCENT_TINT"])
            self._filename_lbl.configure(background=ThemeColors["ACCENT_TINT"])
            self._meta_lbl.configure(background=ThemeColors["ACCENT_TINT"])
        else:
            self.configure(highlightbackground=ThemeColors["BORDER_SLATE"], highlightthickness=1, bg=ThemeColors["BG_MAIN"])
            self._icon_lbl.configure(bg=ThemeColors["BG_MAIN"])
            self._filename_lbl.configure(background=ThemeColors["BG_MAIN"])
            self._meta_lbl.configure(background=ThemeColors["BG_MAIN"])
