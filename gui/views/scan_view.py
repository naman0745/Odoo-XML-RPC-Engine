"""
gui/views/scan_view.py
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from gui.models.ui_models import PendingOrderInfo
from gui.widgets.order_card import OrderCard
from gui.style import FONT_H1_40


class ScanView(ttk.Frame):
    """
    Displays the folder scan results (list of pending orders or empty state).
    Completely passive. Exposes load_files().
    """
    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        self.pack_propagate(False)

        # Callbacks
        self.on_order_selected: Optional[Callable[[PendingOrderInfo], None]] = None
        self.on_refresh: Optional[Callable[[], None]] = None
        self.on_import_clicked: Optional[Callable[[], None]] = None
        self.on_open_folder: Optional[Callable[[], None]] = None
        self.on_change_folder: Optional[Callable[[], None]] = None
        self.on_theme_toggle: Optional[Callable[[], None]] = None

        # ---------------------------------------------------------
        # Header Area (Metadata + Refresh)
        # ---------------------------------------------------------
        self.header_frame = ttk.Frame(self)
        self.header_frame.pack(fill="x", pady=(24, 16), padx=32)

        # Top row: metadata, refresh, and theme toggle
        self.top_row = ttk.Frame(self.header_frame)
        self.top_row.pack(fill="x")

        self.meta_lbl = ttk.Label(self.top_row, text="0 pending orders · Last scanned: never", style="Bold.TLabel")
        self.meta_lbl.pack(side="left")

        refresh_btn = ttk.Button(self.top_row, text="⟳ Refresh", style="Ghost.TLabel", cursor="hand2")
        refresh_btn.bind("<Button-1>", lambda e: self.on_refresh() if self.on_refresh else None)
        refresh_btn.pack(side="left", padx=16)

        # Theme toggle button on the right side
        theme_toggle_btn = ttk.Button(self.top_row, text="◐ Theme", style="Ghost.TLabel", cursor="hand2")
        theme_toggle_btn.bind("<Button-1>", lambda e: self._handle_theme_toggle())
        theme_toggle_btn.pack(side="right")

        # Bottom row: folder path and change folder button
        self.folder_row = ttk.Frame(self.header_frame)
        self.folder_row.pack(fill="x", pady=(8, 0))

        self.folder_path_lbl = ttk.Label(self.folder_row, text="", style="Muted.TLabel")
        self.folder_path_lbl.pack(side="left")

        change_folder_btn = ttk.Button(self.folder_row, text="Change Folder", style="Ghost.TLabel", cursor="hand2")
        change_folder_btn.bind("<Button-1>", lambda e: self._handle_change_folder())
        change_folder_btn.pack(side="left", padx=(8, 0))

        # ---------------------------------------------------------
        # Main Content Area (List vs Empty)
        # ---------------------------------------------------------
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill="both", expand=True, padx=32)

        self._selected_order: Optional[PendingOrderInfo] = None
        self._cards: list[OrderCard] = []
        self._current_orders: list[PendingOrderInfo] = []

    def load_files(self, orders: list[PendingOrderInfo], last_scanned: str, incoming_path: str = "") -> None:
        """Populate the view with order data."""
        self._selected_order = None
        self._current_orders = orders

        # Clear existing cards / empty state contents
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self._cards.clear()

        # Update metadata
        count = len(orders)
        self.meta_lbl.configure(text=f"{count} pending order{'s' if count != 1 else ''} · Last scanned: {last_scanned}")

        # Update folder path display
        if incoming_path:
            self.folder_path_lbl.configure(text=incoming_path)

        if count == 0:
            self._render_empty_state(incoming_path)
        else:
            for order in orders:
                card = OrderCard(
                    self.content_frame, 
                    order, 
                    self._handle_card_click, 
                    self._handle_import_click
                )
                card.pack(fill="x", pady=(0, 8))
                self._cards.append(card)

            # Auto-select if exactly 1
            if count == 1:
                self._handle_card_click(self._cards[0], orders[0])

    def _render_empty_state(self, incoming_path: str) -> None:
        # Inner centered frame
        center = ttk.Frame(self.content_frame)
        center.place(relx=0.5, rely=0.4, anchor="center")

        ttk.Label(center, text="📂", font=FONT_H1_40).pack(pady=(0, 16))
        ttk.Label(center, text="No pending purchase orders found.", style="Bold.TLabel").pack()
        ttk.Label(center, text="Add Excel workbooks to the Incoming Orders folder to begin.", style="Muted.TLabel").pack(pady=8)
        
        display_path = incoming_path if incoming_path else "Workspace / Incoming Orders"
        ttk.Label(center, text=display_path, style="MonoMuted.TLabel").pack(pady=(0,24))
        
        btn_frame = ttk.Frame(center)
        btn_frame.pack()
        open_folder_btn = ttk.Button(btn_frame, text="Open Incoming Folder", style="Secondary.TButton")
        open_folder_btn.configure(command=self._handle_open_folder)
        open_folder_btn.pack(side="left", padx=8)

        refresh_btn_empty = ttk.Button(btn_frame, text="Refresh", style="Secondary.TButton")
        refresh_btn_empty.configure(command=lambda: self.on_refresh() if self.on_refresh else None)
        refresh_btn_empty.pack(side="left", padx=8)

    def _handle_open_folder(self) -> None:
        if self.on_open_folder:
            self.on_open_folder()

    def _handle_change_folder(self) -> None:
        if self.on_change_folder:
            self.on_change_folder()

    def _handle_theme_toggle(self) -> None:
        if self.on_theme_toggle:
            self.on_theme_toggle()

    def _handle_card_click(self, clicked_card: OrderCard, order: PendingOrderInfo) -> None:
        for card in self._cards:
            card.set_selected(False)
        clicked_card.set_selected(True)
        self._selected_order = order
        
        if self.on_order_selected:
            self.on_order_selected(order)

    def _handle_import_click(self) -> None:
        if self._selected_order and self.on_import_clicked:
            self.on_import_clicked()
