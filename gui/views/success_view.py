"""
gui/views/success_view.py
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

class SuccessView(ttk.Frame):
    """
    Displays the aggregated results of a batch import run.
    """
    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)

        self.on_process_next_clicked: Optional[Callable[[], None]] = None
        self.on_back_clicked: Optional[Callable[[], None]] = None
        self.on_view_failure: Optional[Callable[[list], None]] = None

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True, padx=48, pady=32)

        header = ttk.Frame(container)
        header.pack(fill="x", pady=(0, 24))

        self.icon_lbl = ttk.Label(header, text="✓", style="SuccessIcon.TLabel")
        self.icon_lbl.pack(side="left", padx=(0, 16))

        title_frame = ttk.Frame(header)
        title_frame.pack(side="left", fill="x", expand=True)
        self.title_lbl = ttk.Label(title_frame, text="Batch Complete", style="H1.TLabel")
        self.title_lbl.pack(anchor="w")
        
        self.summary_lbl = ttk.Label(title_frame, text="0 of 0 imported successfully", style="Muted.TLabel")
        self.summary_lbl.pack(anchor="w")

        # Scrollable log area for results
        self.results_frame = ttk.Frame(container, style="Card.TFrame")
        self.results_frame.pack(fill="both", expand=True, pady=(0, 24))
        
        self.listbox = tk.Listbox(self.results_frame, font=("Segoe UI", 11), bg="#1E1E1E", fg="#E0E0E0", borderwidth=0, highlightthickness=0)
        self.listbox.pack(side="left", fill="both", expand=True, padx=(16, 0), pady=16)
        
        self.scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=self.listbox.yview)
        self.scrollbar.pack(side="right", fill="y", pady=16, padx=(0, 16))
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        
        # Double click bind for failures
        self.listbox.bind("<Double-Button-1>", self._handle_item_double_click)
        
        self._batch_results = []

        btn_frame = ttk.Frame(container)
        btn_frame.pack(anchor="w")

        self.action_btn = ttk.Button(btn_frame, text="Back to Dashboard", style="Primary.TButton")
        self.action_btn.configure(command=self._handle_back)
        self.action_btn.pack(side="left")

    def set_batch_results(self, results: list[dict], total_time: str) -> None:
        """
        results format: [{"order": PendingOrderInfo, "result": ImportResult, "moved": bool}]
        """
        self._batch_results = results
        success_count = sum(1 for r in results if r["result"].success)
        total = len(results)
        
        if success_count == total:
            self.icon_lbl.configure(text="✓", style="SuccessIcon.TLabel")
            self.title_lbl.configure(text="Batch Complete")
        elif success_count == 0:
            self.icon_lbl.configure(text="✖", style="Error.TLabel")
            self.title_lbl.configure(text="Batch Failed")
        else:
            self.icon_lbl.configure(text="⚠", style="Warning.TLabel")
            self.title_lbl.configure(text="Batch Partially Completed")

        self.summary_lbl.configure(text=f"{success_count} of {total} imported successfully in {total_time}.")
        
        self.listbox.delete(0, tk.END)
        for idx, item in enumerate(results):
            order = item["order"]
            res = item["result"]
            if res.success:
                status = f"✅ SUCCESS: {order.filename} -> PO#{res.order_id}"
            else:
                err_msg = res.errors[0] if res.errors else "Unknown error"
                status = f"❌ FAILED: {order.filename} -> {err_msg}"
            self.listbox.insert(tk.END, status)
            if not res.success:
                self.listbox.itemconfig(idx, {'fg': '#EF5350'})

    def set_pending_count(self, count: int) -> None:
        pass # obsolete for batch view

    def _handle_back(self) -> None:
        if self.on_back_clicked:
            self.on_back_clicked()
            
    def _handle_item_double_click(self, event) -> None:
        selection = self.listbox.curselection()
        if not selection or not self.on_view_failure:
            return
            
        index = selection[0]
        if index < len(self._batch_results):
            item = self._batch_results[index]
            res = item["result"]
            if not res.success:
                self.on_view_failure([res, item["order"]])