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

        # Callbacks
        self.on_selection_changed: Optional[Callable[[list[PendingOrderInfo]], None]] = None
        self.on_refresh: Optional[Callable[[], None]] = None
        self.on_process_clicked: Optional[Callable[[list[PendingOrderInfo]], None]] = None
        self.on_open_folder: Optional[Callable[[], None]] = None
        self.on_change_folder: Optional[Callable[[], None]] = None

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
        
        self.select_all_btn = ttk.Button(self.top_row, text="Select All", style="Ghost.TLabel", cursor="hand2")
        self.select_all_btn.bind("<Button-1>", lambda e: self._handle_select_all())
        self.select_all_btn.pack(side="left", padx=16)

        # Bottom row: folder path and change folder button
        self.folder_row = ttk.Frame(self.header_frame)
        self.folder_row.pack(fill="x", pady=(8, 0))

        self.folder_path_lbl = ttk.Label(self.folder_row, text="", style="Muted.TLabel")
        self.folder_path_lbl.pack(side="left")

        change_folder_btn = ttk.Button(self.folder_row, text="Change Folder", style="Ghost.TLabel", cursor="hand2")
        change_folder_btn.bind("<Button-1>", lambda e: self._handle_change_folder())
        change_folder_btn.pack(side="left", padx=(8, 0))

        # ---------------------------------------------------------
        # Footer Area (Process Button)
        # ---------------------------------------------------------
        self.footer_frame = ttk.Frame(self, style="Surface.TFrame")
        self.footer_frame.pack(side="bottom", fill="x")
        
        self.process_btn = ttk.Button(self.footer_frame, text="Process Selected (0)", style="Primary.TButton", state="disabled")
        self.process_btn.configure(command=self._handle_process_click)
        self.process_btn.pack(side="right", padx=32, pady=16)

        # ---------------------------------------------------------
        # Main Content Area (Scrollable Canvas)
        # ---------------------------------------------------------
        self.wrapper = ttk.Frame(self)
        self.wrapper.pack(fill="both", expand=True, padx=32, pady=(0, 16))
        
        # The background of Canvas should match the BG_MAIN which is #0D0D0D
        self.canvas = tk.Canvas(self.wrapper, bg="#0D0D0D", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.wrapper, orient="vertical", command=self.canvas.yview)
        
        self.content_frame = ttk.Frame(self.canvas)
        self.content_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw", tags="self.content_frame")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig('self.content_frame', width=e.width))

        self.canvas.bind("<Enter>", self._bound_to_mousewheel)
        self.canvas.bind("<Leave>", self._unbound_to_mousewheel)

        self._selected_orders: list[PendingOrderInfo] = []
        self._cards: list[OrderCard] = []
        self._current_orders: list[PendingOrderInfo] = []

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def load_files(self, orders: list[PendingOrderInfo], last_scanned: str, incoming_path: str = "") -> None:
        """Populate the view with order data."""
        self._selected_orders.clear()
        self._update_process_button()
        self._current_orders = orders
        self.select_all_btn.configure(text="Select All")

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
                    self._handle_card_click
                )
                card.pack(fill="x", pady=(0, 8))
                self._cards.append(card)

            # Auto-select all by default if you want, or leave unselected.
            # For robust batching, we start with all unselected naturally.

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

    def _update_process_button(self) -> None:
        count = len(self._selected_orders)
        if count == 0:
            self.process_btn.configure(text="Process Selected (0)", state="disabled")
        else:
            self.process_btn.configure(text=f"Process Selected ({count})", state="normal")
            
        if self._current_orders and count == len(self._current_orders):
            self.select_all_btn.configure(text="Deselect All")
        else:
            self.select_all_btn.configure(text="Select All")

    def _handle_select_all(self) -> None:
        if not self._current_orders:
            return
            
        if len(self._selected_orders) == len(self._current_orders):
            # Deselect all
            self._selected_orders.clear()
            for card in self._cards:
                card.set_selected(False)
        else:
            # Select all
            self._selected_orders = self._current_orders.copy()
            for card in self._cards:
                card.set_selected(True)
                
        self._update_process_button()
        if self.on_selection_changed:
            self.on_selection_changed(self._selected_orders)

    def _handle_card_click(self, clicked_card: OrderCard, order: PendingOrderInfo, is_selected: bool) -> None:
        if is_selected:
            if order not in self._selected_orders:
                self._selected_orders.append(order)
        else:
            if order in self._selected_orders:
                self._selected_orders.remove(order)
                
        self._update_process_button()
        
        if self.on_selection_changed:
            self.on_selection_changed(self._selected_orders)

    def _handle_process_click(self) -> None:
        if self._selected_orders and self.on_process_clicked:
            self.on_process_clicked(self._selected_orders.copy())
