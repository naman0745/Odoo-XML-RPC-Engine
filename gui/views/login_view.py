import tkinter as tk
from tkinter import ttk
from typing import Callable

class LoginView(ttk.Frame):
    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, style="TFrame")
        self.on_login: Callable[[str, str, str, str, bool], None] = lambda url, db, u, p, r: None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # Center panel
        panel = ttk.Frame(self, style="Card.TFrame", padding=30)
        panel.grid(row=1, column=0)

        # Title
        title_lbl = ttk.Label(panel, text="Sign in to Odoo", style="CardTitle.TLabel")
        title_lbl.pack(pady=(0, 20))

        # Error Message (hidden by default)
        self.error_var = tk.StringVar()
        self.error_lbl = ttk.Label(panel, textvariable=self.error_var, foreground="#F87171", background="#111318", wraplength=300)
        
        # Odoo URL
        url_frame = ttk.Frame(panel, style="Surface.TFrame")
        url_frame.pack(fill="x", pady=5)
        ttk.Label(url_frame, text="Odoo URL", style="Card.TLabel").pack(anchor="w")
        self.url_entry = ttk.Entry(url_frame, font=("Segoe UI", 11))
        self.url_entry.pack(fill="x", pady=2)

        # Database
        db_frame = ttk.Frame(panel, style="Surface.TFrame")
        db_frame.pack(fill="x", pady=5)
        ttk.Label(db_frame, text="Database", style="Card.TLabel").pack(anchor="w")
        self.db_entry = ttk.Entry(db_frame, font=("Segoe UI", 11))
        self.db_entry.pack(fill="x", pady=2)
        
        # Username
        user_frame = ttk.Frame(panel, style="Surface.TFrame")
        user_frame.pack(fill="x", pady=5)
        ttk.Label(user_frame, text="Username", style="Card.TLabel").pack(anchor="w")
        self.user_entry = ttk.Entry(user_frame, font=("Segoe UI", 11))
        self.user_entry.pack(fill="x", pady=2)

        # Password
        pass_frame = ttk.Frame(panel, style="Surface.TFrame")
        pass_frame.pack(fill="x", pady=5)
        ttk.Label(pass_frame, text="Password", style="Card.TLabel").pack(anchor="w")
        
        pass_input_frame = ttk.Frame(pass_frame, style="Surface.TFrame")
        pass_input_frame.pack(fill="x", pady=2)
        
        self.pass_entry = ttk.Entry(pass_input_frame, font=("Segoe UI", 11), show="*")
        self.pass_entry.pack(side="left", fill="x", expand=True)
        
        self.show_pass_var = tk.BooleanVar(value=False)
        self.show_pass_chk = ttk.Checkbutton(
            pass_input_frame, 
            text="👁", 
            style="Toolbutton",
            variable=self.show_pass_var,
            command=self._toggle_password
        )
        self.show_pass_chk.pack(side="right", padx=(5, 0))

        # Remember Me
        self.remember_var = tk.BooleanVar(value=False)
        self.remember_chk = ttk.Checkbutton(panel, text="Remember Me", variable=self.remember_var, style="Card.TCheckbutton")
        self.remember_chk.pack(anchor="w", pady=(5, 15))

        # Login Btn
        self.login_btn = ttk.Button(panel, text="Login", style="Primary.TButton", command=self._handle_login)
        self.login_btn.pack(fill="x")
        
        # Bind enter key
        self.url_entry.bind("<Return>", lambda e: self.db_entry.focus_set())
        self.db_entry.bind("<Return>", lambda e: self.user_entry.focus_set())
        self.user_entry.bind("<Return>", lambda e: self.pass_entry.focus_set())
        self.pass_entry.bind("<Return>", lambda e: self._handle_login())

    def _toggle_password(self):
        if self.show_pass_var.get():
            self.pass_entry.config(show="")
        else:
            self.pass_entry.config(show="*")

    def _handle_login(self):
        url = self.url_entry.get().strip()
        db = self.db_entry.get().strip()
        user = self.user_entry.get().strip()
        pwd = self.pass_entry.get()
        remember = self.remember_var.get()
        if user and pwd and url and db:
            # Disable UX
            self.login_btn.state(['disabled'])
            self.login_btn.config(text="Authenticating...")
            self.update_idletasks()
            self.on_login(url, db, user, pwd, remember)
            self.login_btn.state(['!disabled'])
            self.login_btn.config(text="Login")

    def set_credentials(self, url: str, db: str, username: str, password: str, remember: bool = True):
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, url)
        self.db_entry.delete(0, tk.END)
        self.db_entry.insert(0, db)
        self.user_entry.delete(0, tk.END)
        self.user_entry.insert(0, username)
        self.pass_entry.delete(0, tk.END)
        self.pass_entry.insert(0, password)
        self.remember_var.set(remember)

    def show_error(self, message: str):
        self.error_var.set(message)
        self.error_lbl.pack(before=self.user_entry.master, pady=(0, 10))

    def clear_error(self):
        self.error_var.set("")
        self.error_lbl.pack_forget()

    def clear_password(self):
        self.pass_entry.delete(0, tk.END)
        self.pass_entry.focus_set()
