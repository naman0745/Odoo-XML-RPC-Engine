"""
gui/widgets/order_card.py
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from gui.models.ui_models import PendingOrderInfo
from gui.style import get_theme_colors


class OrderCard(ttk.Frame):
    """
    A single clickable card representing a pending purchase order.
    Takes structured PendingOrderInfo data.
    Uses ttk styles for theme awareness.
    """
    def __init__(
        self,
        parent: tk.Widget,
        order_info: PendingOrderInfo,
        on_click: Callable[['OrderCard', PendingOrderInfo, bool], None]
    ) -> None:
        super().__init__(parent, style="Surface.TFrame")
        self.order_info = order_info
        self.on_click = on_click
        self.is_selected = False

        self.columnconfigure(1, weight=1)

        # File Icon
        self._icon_lbl = ttk.Label(self, text="📄", font=("Segoe UI", 16), background=get_theme_colors()["bg_1"])
        self._icon_lbl.grid(row=0, column=0, rowspan=2, padx=(16, 12), pady=16, sticky="n")

        # Filename
        self._filename_lbl = ttk.Label(self, text=order_info.filename, style="Bold.TLabel", background=get_theme_colors()["bg_1"])
        self._filename_lbl.grid(row=0, column=1, sticky="w", pady=(16, 0))

        # Metadata
        meta_text = f"{order_info.size_kb} KB · Modified {order_info.modified_date} · {order_info.full_path.parent}"
        self._meta_lbl = ttk.Label(self, text=meta_text, style="Muted.TLabel", background=get_theme_colors()["bg_1"])
        self._meta_lbl.grid(row=1, column=1, sticky="w", pady=(2, 16))

        # Checkbox visually replacing the arrow
        self._checkbox_lbl = tk.Label(self, text="☐", font=("Segoe UI", 20), fg=get_theme_colors()["text_muted"], bg=get_theme_colors()["bg_1"], cursor="hand2")
        self._checkbox_lbl.grid(row=0, column=2, rowspan=2, padx=(0, 24), sticky="e")

        # Bind events
        self._bind_events()

    def _refresh_colors(self) -> None:
        colors = get_theme_colors()
        bg_col = colors["row_selected"] if self.is_selected else colors["bg_1"]
        self._icon_lbl.configure(background=bg_col)
        self._filename_lbl.configure(background=bg_col)
        self._meta_lbl.configure(background=bg_col)
        self._checkbox_lbl.configure(background=bg_col)

    def _bind_events(self) -> None:
        for widget in (self, self._icon_lbl, self._filename_lbl, self._meta_lbl, self._checkbox_lbl):
            widget.bind("<Button-1>", self._on_click_handler)
            widget.bind("<Enter>", self._on_hover_in)
            widget.bind("<Leave>", self._on_hover_out)

    def _on_click_handler(self, event: tk.Event) -> None:
        self.toggle_selection()

    def toggle_selection(self) -> None:
        self.set_selected(not self.is_selected)
        self.on_click(self, self.order_info, self.is_selected)

    def _on_hover_in(self, event: tk.Event) -> None:
        pass # ttk outline handled by parent natively or disabled to avoid visual tearing

    def _on_hover_out(self, event: tk.Event) -> None:
        pass

    def set_selected(self, selected: bool) -> None:
        self.is_selected = selected
        colors = get_theme_colors()
        bg_col = colors["row_selected"] if selected else colors["bg_1"]
        
        self.configure(style="Selected.TFrame" if selected else "Surface.TFrame")
        self._icon_lbl.configure(background=bg_col)
        self._filename_lbl.configure(background=bg_col)
        self._meta_lbl.configure(background=bg_col)
        self._checkbox_lbl.configure(background=bg_col)
        
        if selected:
            self._checkbox_lbl.configure(text="☑", fg=colors["accent"])
        else:
            self._checkbox_lbl.configure(text="☐", fg=colors["text_muted"])