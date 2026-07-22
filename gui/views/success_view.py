"""
gui/views/success_view.py
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional


class SuccessView(ttk.Frame):
    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        self.pack_propagate(False)

        self.on_process_next_clicked: Optional[Callable[[], None]] = None
        self.on_back_clicked: Optional[Callable[[], None]] = None

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True, padx=48, pady=32)

        header = ttk.Frame(container)
        header.pack(fill="x", pady=(0, 24))

        ttk.Label(header, text="✓", style="SuccessIcon.TLabel").pack(side="left", padx=(0, 16))

        title_frame = ttk.Frame(header)
        title_frame.pack(side="left", fill="x", expand=True)
        ttk.Label(title_frame, text="Purchase Order Created", style="H1.TLabel").pack(anchor="w")
        self.po_id_lbl = ttk.Label(title_frame, text="PO00000", style="POId.TLabel")
        self.po_id_lbl.pack(anchor="w")

        self.summary_frame = ttk.Frame(container, style="Card.TFrame")
        self.summary_frame.pack(fill="x", pady=(0, 24), ipadx=16, ipady=16)

        # Grid layout for summary
        self.workbook_lbl = ttk.Label(self.summary_frame, text="Workbook: Unknown", style="CardTitle.TLabel")
        self.workbook_lbl.grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.rows_lbl = ttk.Label(self.summary_frame, text="Rows Imported: 0", style="CardMeta.TLabel")
        self.rows_lbl.grid(row=1, column=0, sticky="w", pady=(0, 4))

        self.time_lbl = ttk.Label(self.summary_frame, text="Time Taken: < 1s", style="CardMeta.TLabel")
        self.time_lbl.grid(row=2, column=0, sticky="w", pady=(0, 4))

        self.move_lbl = ttk.Label(self.summary_frame, text="File Moved: Processed Orders", style="CardMeta.Success.TLabel")
        self.move_lbl.grid(row=3, column=0, sticky="w", pady=(12, 0))

        btn_frame = ttk.Frame(container)
        btn_frame.pack(anchor="w")

        self.action_btn = ttk.Button(btn_frame, text="Back to Order List", style="Secondary.TButton")
        self.action_btn.configure(command=self._handle_back)
        self.action_btn.pack(side="left")

    def set_result(self, po_id: str, workbook: str, rows_total: int, time_taken: str, move_status: str, move_success: bool = True) -> None:
        self.po_id_lbl.configure(text=po_id)
        self.workbook_lbl.configure(text=f"Workbook: {workbook}")
        self.rows_lbl.configure(text=f"Rows Imported: {rows_total}")
        self.time_lbl.configure(text=f"Time Taken: {time_taken}")
        self.move_lbl.configure(
            text=f"File Status: {move_status}",
            style="CardMeta.Success.TLabel" if move_success else "CardMeta.Error.TLabel"
        )

    def set_pending_count(self, count: int) -> None:
        if count > 0:
            self.action_btn.configure(
                text=f"Process Next File ({count} remain)",
                style="Primary.TButton",
                command=self._handle_process_next
            )
        else:
            self.action_btn.configure(
                text="Back to Order List",
                style="Secondary.TButton",
                command=self._handle_back
            )

    def _handle_process_next(self) -> None:
        if self.on_process_next_clicked:
            self.on_process_next_clicked()

    def _handle_back(self) -> None:
        if self.on_back_clicked:
            self.on_back_clicked()