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
        self.on_prev_clicked: Optional[Callable[[], None]] = None
        self.on_next_clicked: Optional[Callable[[], None]] = None

        # Content container
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill="x", padx=32, pady=32)

        # Card placeholder (filled in set_order)
        self._card: Optional[OrderCard] = None

        # Navigation container for Prev/Next
        self.nav_frame = ttk.Frame(self.content_frame)
        self.nav_frame.pack(fill="x", pady=16)

        self.prev_btn = ttk.Button(self.nav_frame, text="← Prev", style="Secondary.TButton")
        self.prev_btn.pack(side="left")
        self.prev_btn.configure(command=self._handle_prev_click)

        self.next_btn = ttk.Button(self.nav_frame, text="Next →", style="Secondary.TButton")
        self.next_btn.pack(side="right")
        self.next_btn.configure(command=self._handle_next_click)

        # Import Button
        self.import_btn = ttk.Button(self, text="Import Purchase Order", style="Primary.TButton")
        self.import_btn.configure(command=self._handle_import_click)
        self.import_btn.pack(pady=24)

        # Back link
        self.back_link = ttk.Label(self, text="← Back to entire list", style="Ghost.TLabel", cursor="hand2")
        self.back_link.bind("<Button-1>", lambda e: self.on_back_clicked() if self.on_back_clicked else None)
        self.back_link.pack(side="bottom", pady=24)

    def set_order(self, order: PendingOrderInfo, has_prev: bool = False, has_next: bool = False) -> None:
        if self._card:
            self._card.destroy()

        self._card = OrderCard(self.content_frame, order, lambda *args: None)
        self._card.set_selected(True)
        # Put the card BEFORE the nav frame
        self._card.pack(before=self.nav_frame, fill="x")

        # Disable navigation safely if at bounds
        self.prev_btn.state(["!disabled"] if has_prev else ["disabled"])
        self.next_btn.state(["!disabled"] if has_next else ["disabled"])

    def _handle_import_click(self) -> None:
        if self.on_import_clicked:
            self.on_import_clicked()
            
    def _handle_prev_click(self) -> None:
        if self.on_prev_clicked:
            self.on_prev_clicked()
            
    def _handle_next_click(self) -> None:
        if self.on_next_clicked:
            self.on_next_clicked()
