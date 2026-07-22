"""
gui/style.py

Configures fonts, colors, and ttk styles required by the UX Specification V2.1.
Supports native Light/Dark theme toggling pulled from AppConfig.
"""
import tkinter as tk
from tkinter import ttk
from config.app_config import AppConfig

# Fonts remain constant across themes
FONT_REGULAR_12 = ("Segoe UI", 10) # ~12px visual weight
FONT_REGULAR_13 = ("Segoe UI", 10) # 13px equivalent muted
FONT_REGULAR_14 = ("Segoe UI", 11) 
FONT_MEDIUM_14  = ("Segoe UI", 11, "bold") # Bold for active labels/buttons
FONT_BOLD_14    = ("Segoe UI", 11, "bold")
FONT_BOLD_16    = ("Segoe UI", 13, "bold")
FONT_BOLD_20    = ("Segoe UI", 16, "bold")
FONT_MONO_12    = ("Consolas", 10)
FONT_MONO_14    = ("Consolas", 11)
FONT_H1_40      = ("Segoe UI", 40)

LIGHT_PALETTE = {
    "BG_MAIN": "#FFFFFF",
    "BG_SURFACE": "#F8FAFC",
    "FG_MAIN": "#334155",
    "FG_MUTED": "#64748B",
    "BORDER_SLATE": "#475569",
    "ACCENT_BLUE": "#2563EB",
    "ACCENT_BLUE_HOVER": "#1D4ED8",
    "ACCENT_TINT": "#EBF2FF",
    "GREEN_ACCENT": "#16A34A",
    "AMBER_WARNING": "#D97706",
    "RED_FAILED": "#DC2626"
}

DARK_PALETTE = {
    "BG_MAIN": "#0D0D0D",        
    "BG_SURFACE": "#1E1E1E",     
    "FG_MAIN": "#E0E0E0",        
    "FG_MUTED": "#9E9E9E",       
    "BORDER_SLATE": "#333333",   
    "ACCENT_BLUE": "#4DA3FF",    
    "ACCENT_BLUE_HOVER": "#6EB5FF",
    "ACCENT_TINT": "#1A3A5C",    
    "GREEN_ACCENT": "#69DB7C",   
    "AMBER_WARNING": "#FFB74D",
    "RED_FAILED": "#EF5350"
}

def get_theme_colors() -> dict:
    """Return current theme palette."""
    return DARK_PALETTE if AppConfig().get_theme() == "dark" else LIGHT_PALETTE

_theme_listeners = []

def register_theme_listener(callback) -> None:
    """Register a UI component to automatically refresh when the theme switches."""
    _theme_listeners.append(callback)

def unregister_theme_listener(callback) -> None:
    if callback in _theme_listeners:
        _theme_listeners.remove(callback)

def apply_styles(root: tk.Tk) -> None:
    """Configure all ttk styles for the application based on AppConfig theme."""
    ThemeColors = get_theme_colors()
    
    BG_MAIN = ThemeColors["BG_MAIN"]
    BG_SURFACE = ThemeColors["BG_SURFACE"]
    FG_MAIN = ThemeColors["FG_MAIN"]
    FG_MUTED = ThemeColors["FG_MUTED"]
    BORDER_SLATE = ThemeColors["BORDER_SLATE"]
    ACCENT_BLUE = ThemeColors["ACCENT_BLUE"]
    ACCENT_BLUE_HOVER = ThemeColors["ACCENT_BLUE_HOVER"]
    GREEN_ACCENT = ThemeColors["GREEN_ACCENT"]
    AMBER_WARNING = ThemeColors["AMBER_WARNING"]
    RED_FAILED = ThemeColors["RED_FAILED"]
    
    # Root level background
    root.configure(bg=BG_MAIN)
    
    style = ttk.Style(root)
    if 'clam' in style.theme_names():
         style.theme_use('clam')
    
    # Global Defaults
    style.configure(".", background=BG_MAIN, foreground=FG_MAIN, font=FONT_REGULAR_14)
    
    # Structural frames
    style.configure("TFrame", background=BG_MAIN)
    style.configure("Surface.TFrame", background=BG_SURFACE)
    
    # Selected Cards
    style.configure("Selected.TFrame", background=ThemeColors["ACCENT_TINT"])
    
    style.configure("TLabel", background=BG_MAIN, foreground=FG_MAIN)
    
    # Special Purpose Labels
    style.configure("Muted.TLabel", foreground=FG_MUTED, font=FONT_REGULAR_12, background=BG_MAIN)
    style.configure("MonoMuted.TLabel", foreground=FG_MUTED, font=FONT_MONO_12, background=BG_MAIN)
    style.configure("Bold.TLabel", font=FONT_BOLD_14, foreground=FG_MAIN, background=BG_MAIN)
    style.configure("H1.TLabel", font=FONT_BOLD_20, foreground=FG_MAIN, background=BG_MAIN)
    
    # Status Badges
    style.configure("Connected.TLabel", foreground=GREEN_ACCENT, font=FONT_REGULAR_12, background=BG_MAIN)
    style.configure("Warning.TLabel", foreground=AMBER_WARNING, font=FONT_REGULAR_12, background=BG_MAIN)
    style.configure("Error.TLabel", foreground=RED_FAILED, font=FONT_REGULAR_12, background=BG_MAIN)
    
    # Header & Footer bands
    style.configure("Header.TFrame", background=BG_MAIN)
    style.configure("Footer.TFrame", background=BG_MAIN)
    style.configure("Footer.TLabel", foreground=FG_MUTED, font=FONT_REGULAR_12, background=BG_MAIN)
    
    # Buttons
    style.configure(
        "Primary.TButton", 
        background=ACCENT_BLUE, 
        foreground="white", 
        font=FONT_MEDIUM_14,
        borderwidth=0,
        focuscolor=ACCENT_BLUE
    )
    style.map(
        "Primary.TButton",
        background=[('active', ACCENT_BLUE_HOVER), ('disabled', BORDER_SLATE)],
        foreground=[('disabled', FG_MUTED)]
    )
    
    style.configure(
        "Secondary.TButton", 
        background=BG_SURFACE, 
        foreground=FG_MAIN, 
        font=FONT_MEDIUM_14,
        borderwidth=1,
        bordercolor=BORDER_SLATE
    )
    style.map(
        "Secondary.TButton",
        background=[('active', BORDER_SLATE)],
    )
    
    style.configure(
        "Ghost.TLabel", 
        foreground=ACCENT_BLUE, 
        background=BG_MAIN, 
        font=FONT_REGULAR_14
    )
    
    style.configure(
        "ChecklistIcon.Active.TLabel",
        background=BG_MAIN,
        foreground=ACCENT_BLUE,
        font=("Segoe UI", 12)
    )
    style.configure(
        "ChecklistIcon.Complete.TLabel",
        background=BG_MAIN,
        foreground=GREEN_ACCENT,
        font=("Segoe UI", 12)
    )
    style.configure(
        "ChecklistIcon.Failed.TLabel",
        background=BG_MAIN,
        foreground=RED_FAILED,
        font=("Segoe UI", 12)
    )

    style.configure(
        "ChecklistText.TLabel",
        background=BG_MAIN,
        foreground=FG_MUTED,
        font=("Segoe UI", 12)
    )
    style.configure(
        "ChecklistText.Active.TLabel",
        background=BG_MAIN,
        foreground=ACCENT_BLUE,
        font=("Segoe UI", 12)
    )
    style.configure(
        "ChecklistText.Complete.TLabel",
        background=BG_MAIN,
        foreground=FG_MAIN,
        font=("Segoe UI", 12)
    )
    style.configure(
        "ChecklistText.Failed.TLabel",
        background=BG_MAIN,
        foreground=RED_FAILED,
        font=("Segoe UI", 12)
    )

    # -------------------------------------------------------------
    # Success / Failure View Styles
    # -------------------------------------------------------------
    style.configure(
        "SuccessIcon.TLabel",
        background=BG_MAIN,
        foreground=GREEN_ACCENT,
        font=("Segoe UI", 32)
    )
    style.configure(
        "Card.TFrame",
        background=BG_SURFACE,
        borderwidth=1,
        relief="solid",
        bordercolor=BORDER_SLATE
    )
    style.configure(
        "CardTitle.TLabel",
        background=BG_SURFACE,
        foreground=FG_MAIN,
        font=FONT_BOLD_14
    )
    style.configure(
        "CardMeta.TLabel",
        background=BG_SURFACE,
        foreground=FG_MUTED,
        font=FONT_REGULAR_12
    )
    style.configure(
        "CardMeta.Success.TLabel",
        background=BG_SURFACE,
        foreground=GREEN_ACCENT,
        font=FONT_REGULAR_12
    )
    style.configure(
        "CardMeta.Error.TLabel",
        background=BG_SURFACE,
        foreground=RED_FAILED,
        font=FONT_REGULAR_12
    )
    style.configure(
        "POId.TLabel",
        background=BG_MAIN,
        foreground=ACCENT_BLUE,
        font=("Consolas", 14, "bold")
    )

    # -------------------------------------------------------------
    # Checklist Widget Styles
    # -------------------------------------------------------------
    style.configure(
        "ChecklistIcon.TLabel",
        background=BG_MAIN,
        foreground=FG_MUTED,
        font=("Segoe UI", 12)
    )
    style.configure(
        "ChecklistIcon.Active.TLabel",
        background=BG_MAIN,
        foreground=ACCENT_BLUE,
        font=("Segoe UI", 12)
    )
    style.configure(
        "ChecklistIcon.Complete.TLabel",
        background=BG_MAIN,
        foreground=GREEN_ACCENT,
        font=("Segoe UI", 12)
    )
    style.configure(
        "ChecklistIcon.Failed.TLabel",
        background=BG_MAIN,
        foreground=RED_FAILED,
        font=("Segoe UI", 12)
    )

    style.configure(
        "ChecklistText.TLabel",
        background=BG_MAIN,
        foreground=FG_MUTED,
        font=("Segoe UI", 12)
    )
    style.configure(
        "ChecklistText.Active.TLabel",
        background=BG_MAIN,
        foreground=ACCENT_BLUE,
        font=("Segoe UI", 12)
    )
    style.configure(
        "ChecklistText.Complete.TLabel",
        background=BG_MAIN,
        foreground=FG_MAIN,
        font=("Segoe UI", 12)
    )
    style.configure(
        "ChecklistText.Failed.TLabel",
        background=BG_MAIN,
        foreground=RED_FAILED,
        font=("Segoe UI", 12)
    )

    # -------------------------------------------------------------
    # Success / Failure View Styles
    # -------------------------------------------------------------
    style.configure(
        "SuccessIcon.TLabel",
        background=BG_MAIN,
        foreground=GREEN_ACCENT,
        font=("Segoe UI", 32)
    )
    style.configure(
        "Card.TFrame",
        background=BG_SURFACE,
        borderwidth=1,
        relief="solid",
        bordercolor=BORDER_SLATE
    )
    style.configure(
        "CardTitle.TLabel",
        background=BG_SURFACE,
        foreground=FG_MAIN,
        font=FONT_BOLD_14
    )
    style.configure(
        "CardMeta.TLabel",
        background=BG_SURFACE,
        foreground=FG_MUTED,
        font=FONT_REGULAR_12
    )
    style.configure(
        "CardMeta.Success.TLabel",
        background=BG_SURFACE,
        foreground=GREEN_ACCENT,
        font=FONT_REGULAR_12
    )
    style.configure(
        "CardMeta.Error.TLabel",
        background=BG_SURFACE,
        foreground=RED_FAILED,
        font=FONT_REGULAR_12
    )
    style.configure(
        "POId.TLabel",
        background=BG_MAIN,
        foreground=ACCENT_BLUE,
        font=("Consolas", 14, "bold")
    )

