"""
gui/style.py

Configures fonts, colors, and ttk styles required by the UX Specification V2.1.
Hardlocked to Obsidian Professional Pattern to eliminate runtime switching overhead.
"""
import tkinter as tk
from tkinter import ttk

FONT_REGULAR_12 = ("Segoe UI", 10)
FONT_REGULAR_13 = ("Segoe UI", 10)
FONT_REGULAR_14 = ("Segoe UI", 11) 
FONT_MEDIUM_14  = ("Segoe UI", 11, "bold")
FONT_BOLD_14    = ("Segoe UI", 11, "bold")
FONT_BOLD_16    = ("Segoe UI", 13, "bold")
FONT_BOLD_20    = ("Segoe UI", 16, "bold")
FONT_MONO_12    = ("Consolas", 10)
FONT_MONO_14    = ("Consolas", 11)
FONT_H1_40      = ("Segoe UI", 40)

PREMIUM_DARK = {
    "bg_0": "#0A0A0F",
    "bg_1": "#111318",
    "bg_2": "#1A1D24",
    "bg_3": "#22262F",
    "border_subtle": "#2A2E39",
    "border_default": "#353A48",
    "border_focus": "#4A9EFF",
    "text_hero": "#FFFFFF",
    "text_primary": "#E8EBF0",
    "text_secondary": "#A0A8B8",
    "text_muted": "#6B7383",
    "accent": "#4A9EFF",
    "accent_hover": "#5BA8FF",
    "success": "#34D399",
    "warning": "#FBBF24",
    "error": "#F87171",
    "mono_fg": "#D1D5DB",
    "row_alt": "#16181D",
    "row_hover": "#141B25",
    "row_selected": "#182434",
}

def get_theme_colors() -> dict:
    return PREMIUM_DARK

def apply_styles(root: tk.Tk) -> None:
    ThemeColors = get_theme_colors()
    
    bg_0 = ThemeColors["bg_0"]
    bg_1 = ThemeColors["bg_1"]
    bg_2 = ThemeColors["bg_2"]
    
    # Root level background
    root.configure(bg=bg_0)
    root.option_add("*background", bg_0)
    root.option_add("*foreground", ThemeColors["text_primary"])
    root.option_add("*Listbox*background", bg_1)
    root.option_add("*Listbox*foreground", ThemeColors["text_primary"])
    root.option_add("*Listbox*selectBackground", ThemeColors["accent"])
    
    root.option_add("*TCombobox*Listbox.background", bg_2)
    root.option_add("*TCombobox*Listbox.foreground", ThemeColors["text_primary"])
    root.option_add("*TCombobox*Listbox.selectBackground", ThemeColors["accent"])
    
    style = ttk.Style(root)
    if 'clam' in style.theme_names():
         style.theme_use('clam')
    
    # Global Defaults
    style.configure(".", background=bg_0, foreground=ThemeColors["text_primary"], font=FONT_REGULAR_14)
    
    # Structural frames
    style.configure("TFrame", background=bg_0)
    style.configure("Surface.TFrame", background=bg_1)
    
    # Inputs
    style.configure("TEntry", fieldbackground=bg_1, foreground=ThemeColors["text_primary"], insertcolor=ThemeColors["text_primary"])
    style.configure("TCombobox", fieldbackground=bg_1, foreground=ThemeColors["text_primary"], insertcolor=ThemeColors["text_primary"], background=bg_1, arrowcolor=ThemeColors["text_primary"])
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", bg_1), ("disabled", bg_0)],
        background=[("readonly", bg_1)],
        foreground=[("readonly", ThemeColors["text_primary"])]
    )
    
    # Selected Cards
    style.configure("Selected.TFrame", background=ThemeColors["row_selected"])
    
    style.configure("TLabel", background=bg_0, foreground=ThemeColors["text_primary"])
    
    # Special Purpose Labels
    style.configure("Muted.TLabel", foreground=ThemeColors["text_muted"], font=FONT_REGULAR_12, background=bg_0)
    style.configure("MonoMuted.TLabel", foreground=ThemeColors["text_muted"], font=FONT_MONO_12, background=bg_0)
    style.configure("Bold.TLabel", font=FONT_BOLD_14, foreground=ThemeColors["text_primary"], background=bg_0)
    style.configure("H1.TLabel", font=FONT_BOLD_20, foreground=ThemeColors["text_primary"], background=bg_0)
    
    # Status Badges
    style.configure("Connected.TLabel", foreground=ThemeColors["success"], font=FONT_REGULAR_12, background=bg_0)
    style.configure("Warning.TLabel", foreground=ThemeColors["warning"], font=FONT_REGULAR_12, background=bg_0)
    style.configure("Error.TLabel", foreground=ThemeColors["error"], font=FONT_REGULAR_12, background=bg_0)
    
    # Header & Footer bands
    style.configure("Header.TFrame", background=bg_0)
    style.configure("Footer.TFrame", background=bg_0)
    style.configure("Footer.TLabel", foreground=ThemeColors["text_muted"], font=FONT_REGULAR_12, background=bg_0)
    
    # Buttons
    style.configure(
        "Primary.TButton", 
        background=ThemeColors["accent"], 
        foreground="black", 
        font=FONT_MEDIUM_14,
        borderwidth=0,
        focuscolor=ThemeColors["accent"]
    )
    style.map(
        "Primary.TButton",
        background=[('active', ThemeColors["accent_hover"]), ('disabled', ThemeColors["border_default"])],
        foreground=[('disabled', ThemeColors["text_muted"])]
    )
    
    style.configure(
        "Secondary.TButton", 
        background=bg_1, 
        foreground=ThemeColors["text_primary"], 
        font=FONT_MEDIUM_14,
        borderwidth=1,
        bordercolor=ThemeColors["border_default"]
    )
    style.map(
        "Secondary.TButton",
        background=[('active', ThemeColors["border_default"])],
    )
    
    style.configure(
        "Ghost.TLabel", 
        foreground=ThemeColors["accent"], 
        background=bg_0, 
        font=FONT_REGULAR_14
    )
    
    # -------------------------------------------------------------
    # Checklist Widget Styles
    # -------------------------------------------------------------
    style.configure(
        "ChecklistIcon.TLabel",
        background=bg_0,
        foreground=ThemeColors["text_muted"],
        font=("Segoe UI", 12)
    )
    style.configure(
        "ChecklistIcon.Active.TLabel",
        background=bg_0,
        foreground=ThemeColors["accent"],
        font=("Segoe UI", 12)
    )
    style.configure(
        "ChecklistIcon.Complete.TLabel",
        background=bg_0,
        foreground=ThemeColors["success"],
        font=("Segoe UI", 12)
    )
    style.configure(
        "ChecklistIcon.Failed.TLabel",
        background=bg_0,
        foreground=ThemeColors["error"],
        font=("Segoe UI", 12)
    )

    style.configure(
        "ChecklistText.TLabel",
        background=bg_0,
        foreground=ThemeColors["text_muted"],
        font=("Segoe UI", 12)
    )
    style.configure(
        "ChecklistText.Active.TLabel",
        background=bg_0,
        foreground=ThemeColors["accent"],
        font=("Segoe UI", 12)
    )
    style.configure(
        "ChecklistText.Complete.TLabel",
        background=bg_0,
        foreground=ThemeColors["text_primary"],
        font=("Segoe UI", 12)
    )
    style.configure(
        "ChecklistText.Failed.TLabel",
        background=bg_0,
        foreground=ThemeColors["error"],
        font=("Segoe UI", 12)
    )

    # -------------------------------------------------------------
    # Success / Failure View Styles
    # -------------------------------------------------------------
    style.configure(
        "SuccessIcon.TLabel",
        background=bg_0,
        foreground=ThemeColors["success"],
        font=("Segoe UI", 32)
    )
    style.configure(
        "Card.TFrame",
        background=bg_1,
        borderwidth=1,
        relief="solid",
        bordercolor=ThemeColors["border_subtle"]
    )
    style.configure(
        "CardTitle.TLabel",
        background=bg_1,
        foreground=ThemeColors["text_hero"],
        font=FONT_BOLD_14
    )
    style.configure(
        "CardMeta.TLabel",
        background=bg_1,
        foreground=ThemeColors["text_muted"],
        font=FONT_REGULAR_12
    )
    style.configure(
        "CardMeta.Success.TLabel",
        background=bg_1,
        foreground=ThemeColors["success"],
        font=FONT_REGULAR_12
    )
    style.configure(
        "CardMeta.Error.TLabel",
        background=bg_1,
        foreground=ThemeColors["error"],
        font=FONT_REGULAR_12
    )
    style.configure(
        "POId.TLabel",
        background=bg_0,
        foreground=ThemeColors["accent"],
        font=("Consolas", 14, "bold")
    )
