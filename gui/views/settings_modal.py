"""
gui/views/settings_modal.py
"""
import tkinter as tk
from tkinter import ttk, messagebox
from config.app_config import AppConfig
from config.version import APP_VERSION
from gui.style import apply_styles

class SettingsModal(tk.Toplevel):
    def __init__(self, parent: tk.Widget, on_settings_changed=None):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("500x300")
        self.resizable(False, False)
        
        # Make it modal
        self.transient(parent)
        self.grab_set()
        
        self.on_settings_changed = on_settings_changed
        self.config = AppConfig()
        
        # Apply standard styles
        self.configure(bg=parent.cget("bg"))
        
        container = ttk.Frame(self, padding=24)
        container.pack(fill="both", expand=True)
        
        # Header
        ttk.Label(container, text="Application Settings", style="H1.TLabel").pack(anchor="w", pady=(0, 20))
        
        # Theme Setting
        ttk.Label(container, text="Theme:").pack(anchor="w")
        self.theme_var = tk.StringVar(value=self.config.get_theme())
        themes = ["light", "dark"]
        self.theme_combo = ttk.Combobox(container, textvariable=self.theme_var, values=themes, state="readonly")
        self.theme_combo.pack(fill="x", pady=(4, 16))
        
        # Info Block
        info_frame = ttk.Frame(container, style="Surface.TFrame", padding=12)
        info_frame.pack(fill="x", pady=(16, 24))
        ttk.Label(info_frame, text=f"Version: {APP_VERSION}", style="Bold.TLabel").pack(anchor="w")
        ttk.Label(info_frame, text="Odoo Credentials managed externally via config/settings.py", style="Muted.TLabel").pack(anchor="w")
        
        # Footer buttons
        footer = ttk.Frame(container)
        footer.pack(fill="x", side="bottom")
        
        reset_btn = ttk.Button(footer, text="Reset to Defaults", style="Secondary.TButton")
        reset_btn.configure(command=self._reset_defaults)
        reset_btn.pack(side="left")
        
        save_btn = ttk.Button(footer, text="Save & Apply", style="Primary.TButton")
        save_btn.configure(command=self._save_settings)
        save_btn.pack(side="right")
        
    def _reset_defaults(self):
        if messagebox.askyesno("Confirm Reset", "Reset theme to default?", parent=self):
            defaults = self.config.reset_to_defaults()
            self.theme_var.set(defaults["theme"])
            
    def _save_settings(self):
        new_theme = self.theme_var.get()
        
        self.config.set_theme(new_theme)
        
        if self.on_settings_changed:
            self.on_settings_changed()
            
        self.destroy()
