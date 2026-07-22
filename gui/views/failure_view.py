"""
gui/views/failure_view.py
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from gui.style import ThemeColors


class FailureView(ttk.Frame):
    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        self.pack_propagate(False)

        self.on_retry_clicked: Optional[Callable[[], None]] = None
        self.on_back_clicked: Optional[Callable[[], None]] = None
        self.on_open_excel_clicked: Optional[Callable[[], None]] = None
        self.is_tech_expanded: bool = False

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True, padx=48, pady=32)

        # Header
        header = ttk.Frame(container)
        header.pack(fill="x", pady=(0, 24))
        
        ttk.Label(header, text="⚠", font=("Segoe UI", 32), foreground=ThemeColors["AMBER_WARNING"]).pack(side="left", padx=(0, 16))
        
        title_frame = ttk.Frame(header)
        title_frame.pack(side="left", fill="x", expand=True)
        ttk.Label(title_frame, text="Purchase Order NOT Created", style="H1.TLabel").pack(anchor="w")
        self.workbook_lbl = ttk.Label(title_frame, text="Workbook: Unknown", style="Muted.TLabel")
        self.workbook_lbl.pack(anchor="w")

        # Summary Frame
        self.summary_frame = tk.Frame(container, bg=ThemeColors["BG_SURFACE"], highlightbackground=ThemeColors["BORDER_SLATE"], highlightthickness=1)
        self.summary_frame.pack(fill="x", pady=(0, 16), ipadx=16, ipady=8)
        
        self.stage_lbl = ttk.Label(self.summary_frame, text="Stage: Validating Data", style="Bold.TLabel", background=ThemeColors["BG_SURFACE"])
        self.stage_lbl.pack(anchor="w")
        
        self.summary_lbl = ttk.Label(self.summary_frame, text="0 Rows Checked · 0 Rows Failed", style="Muted.TLabel", background=ThemeColors["BG_SURFACE"])
        self.summary_lbl.pack(anchor="w")

        # Scrollable Error List
        list_container = ttk.Frame(container)
        list_container.pack(fill="both", expand=True)
        
        ttk.Label(list_container, text="Validation Details:", style="Bold.TLabel").pack(anchor="w", pady=(0, 4))
        
        self.error_text = tk.Text(
            list_container, wrap="word", font=("Segoe UI", 10), 
            bg=ThemeColors["BG_SURFACE"], fg=ThemeColors["FG_MAIN"],
            relief="flat", highlightbackground=ThemeColors["BORDER_SLATE"], highlightthickness=1,
            padx=12, pady=12
        )
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.error_text.yview)
        self.error_text.configure(yscrollcommand=scrollbar.set)
        
        self.error_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Technical Details Toggle
        self.tech_btn = ttk.Label(container, text="▶ Show Technical Details", style="Ghost.TLabel", cursor="hand2")
        self.tech_btn.pack(anchor="w", pady=(16, 8))
        self.tech_btn.bind("<Button-1>", self._toggle_tech)
        
        self.tech_details_frame = tk.Frame(container, bg=ThemeColors["BG_SURFACE"], highlightbackground=ThemeColors["BORDER_SLATE"], highlightthickness=1)
        self.tech_code_lbl = ttk.Label(self.tech_details_frame, text="", style="MonoMuted.TLabel", background=ThemeColors["BG_SURFACE"])
        self.tech_code_lbl.pack(anchor="w", padx=12, pady=8)

        ttk.Label(container, text="ⓘ Workbook remains in Incoming Orders — please correct the errors and try again.", style="Muted.TLabel").pack(anchor="w", pady=(8, 16))

        # Buttons
        btn_frame = ttk.Frame(container)
        btn_frame.pack(anchor="e")
        
        self.back_btn = ttk.Button(btn_frame, text="Back to Order List", style="Secondary.TButton")
        self.back_btn.configure(command=self._handle_back)
        self.back_btn.pack(side="left", padx=(0, 8))

        self.open_excel_btn = ttk.Button(btn_frame, text="Open in Excel", style="Secondary.TButton")
        self.open_excel_btn.configure(command=self._handle_open_excel)
        self.open_excel_btn.pack(side="left", padx=(0, 8))

        self.retry_btn = ttk.Button(btn_frame, text="Try Again", style="Primary.TButton")
        self.retry_btn.configure(command=self._handle_retry)
        self.retry_btn.pack(side="left")

    def set_error(self, workbook: str, stage: str, checked: int, failed: int, fatal_error: str, row_errors: list[str]) -> None:
        self.workbook_lbl.configure(text=f"Workbook: {workbook}")
        self.stage_lbl.configure(text=f"Import Stage: {stage}")
        self.summary_lbl.configure(text=f"Rows Checked: {checked}    |    Rows Failed: {failed}")
        
        self.tech_code_lbl.configure(text=f"Internal Database Mapping:\n{fatal_error}")
        
        self.error_text.configure(state="normal")
        self.error_text.delete("1.0", tk.END)
        self.error_text.tag_config("bold", font=("Segoe UI", 11, "bold"))
        self.error_text.tag_config("muted", foreground=ThemeColors["FG_MUTED"])
        
        if not row_errors:
            clean_err = fatal_error
            if "XMLRPC" in clean_err or "faultCode" in clean_err:
                clean_err = "Server communication failed. Please check your network connection and ensure Odoo is online."
            elif "Traceback" in clean_err or "Exception" in clean_err:
                clean_err = "The application encountered an unexpected internal error."
            elif "WinError" in clean_err:
                clean_err = "The operating system rejected the file. Please ensure Microsoft Excel is closed."
                
            self.error_text.insert(tk.END, "Critical Failure:\n", "bold")
            self.error_text.insert(tk.END, f"{clean_err}\n")
        else:
            for i, err in enumerate(row_errors):
                self.error_text.insert(tk.END, f"{err}\n")
                if i < len(row_errors) - 1:
                    self.error_text.insert(tk.END, "\n" + "-"*60 + "\n\n", "muted")
                    
        self.error_text.configure(state="disabled")
        
        self.is_tech_expanded = False
        self.tech_btn.configure(text="▶ Show Technical Details")
        self.tech_details_frame.pack_forget()

    def _toggle_tech(self, event) -> None:
        self.is_tech_expanded = not self.is_tech_expanded
        if self.is_tech_expanded:
            self.tech_btn.configure(text="▼ Hide Technical Details")
            self.tech_details_frame.pack(fill="x", after=self.tech_btn)
        else:
            self.tech_btn.configure(text="▶ Show Technical Details")
            self.tech_details_frame.pack_forget()

    def _handle_retry(self) -> None:
        if self.on_retry_clicked:
            self.on_retry_clicked()
            
    def _handle_back(self) -> None:
        if self.on_back_clicked:
            self.on_back_clicked()

    def _handle_open_excel(self) -> None:
        if self.on_open_excel_clicked:
            self.on_open_excel_clicked()
