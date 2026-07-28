import tkinter as tk
from tkinter import ttk
from config.app_config import AppConfig

class SettingsModal(tk.Toplevel):
    def __init__(self, parent: tk.Widget, on_save_callback) -> None:
        super().__init__(parent)
        self.title("Connection Settings")
        self.geometry("450x300")
        self.transient(parent)
        self.grab_set()
        
        self.on_save_callback = on_save_callback
        self._config = AppConfig()

        self._build_ui()
        self._load_current()

    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding=24)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Odoo Environment Configuration", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 16))

        # URL
        ttk.Label(container, text="Server URL:").pack(anchor="w")
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(container, textvariable=self.url_var, width=50)
        self.url_entry.pack(fill="x", pady=(4, 16))

        # DB
        ttk.Label(container, text="Database Name:").pack(anchor="w")
        self.db_var = tk.StringVar()
        self.db_entry = ttk.Entry(container, textvariable=self.db_var, width=50)
        self.db_entry.pack(fill="x", pady=(4, 24))

        # Buttons
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill="x")
        
        save_btn = ttk.Button(btn_frame, text="Save Settings", command=self._save)
        save_btn.pack(side="right")
        
        cancel_btn = ttk.Button(btn_frame, text="Cancel", command=self.destroy)
        cancel_btn.pack(side="right", padx=8)

    def _load_current(self) -> None:
        # We fetch current from AppConfig
        url = self._config.get_odoo_url()
        db = self._config.get_odoo_db()
        self.url_var.set(url or "")
        self.db_var.set(db or "")

    def _save(self) -> None:
        new_url = self.url_var.get().strip()
        new_db = self.db_var.get().strip()
        
        # Save securely via AppConfig which manages the .json injection natively
        self._config.set_odoo_url(new_url)
        self._config.set_odoo_db(new_db)
        
        self.destroy()
        if self.on_save_callback:
            self.on_save_callback(new_url, new_db)
