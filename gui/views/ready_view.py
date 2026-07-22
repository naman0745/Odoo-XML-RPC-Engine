"""
gui/views/ready_view.py
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from gui.models.ui_models import PendingOrderInfo
from gui.widgets.order_card import OrderCard


class ReadyView(ttk.Frame):
    """
    Displays the selected order, ready for import.
    Completely passive. Exposes set_order().
    """
    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        self.pack_propagate(False)

        # Callbacks
        self.on_import_clicked: Optional[Callable[[], None]] = None
        self.on_back_clicked: Optional[Callable[[], None]] = None

        # Content container
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill="x", padx=32, pady=32)

        # Card placeholder (filled in set_order)
        self._card: Optional[OrderCard] = None

        # Import Button
        self.import_btn = ttk.Button(self, text="Import Purchase Order", style="Primary.TButton")
        self.import_btn.configure(command=self._handle_import_click)
        self.import_btn.pack(pady=24)

        # Back link
        self.back_link = ttk.Label(self, text="← Back to order list", style="Ghost.TLabel", cursor="hand2")
        self.back_link.bind("<Button-1>", lambda e: self.on_back_clicked() if self.on_back_clicked else None)
        self.back_link.pack(side="bottom", pady=24)

    def set_order(self, order: PendingOrderInfo) -> None:
        if self._card:
            self._card.destroy()

        # We construct an OrderCard but pass a no-op click handler just for display
        self._card = OrderCard(self.content_frame, order, lambda *args: None)
        # Default it to selected to show the blue highlight
        self._card.set_selected(True)
        # However, prevent hover from stripping 'selected' styling by disabling cursor change
        # (It's a presentation element here, not interactive)
        self._card.pack(fill="x")

    def _handle_import_click(self) -> None:
        if self.on_import_clicked:
            self.on_import_clicked()
