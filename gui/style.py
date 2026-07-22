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

# Active Theme Color Palette
ThemeColors = {
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

def apply_styles(root: tk.Tk) -> None:
    """Configure all ttk styles for the application based on AppConfig theme."""
    theme_name = AppConfig().get_theme()
    
    # Define Palette dynamically
    if theme_name == "dark":
        ThemeColors.update({
            "BG_MAIN": "#0F172A",
            "BG_SURFACE": "#1E293B",
            "FG_MAIN": "#F8FAFC",
            "FG_MUTED": "#94A3B8",
            "BORDER_SLATE": "#334155",
            "ACCENT_BLUE": "#3B82F6",
            "ACCENT_BLUE_HOVER": "#2563EB",
            "ACCENT_TINT": "#1E3A8A", # dark blue tint
            "GREEN_ACCENT": "#22C55E",
            "AMBER_WARNING": "#F59E0B",
            "RED_FAILED": "#EF4444"
        })
    else:
        ThemeColors.update({
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
        })
        
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
    
    # -------------------------------------------------------------
    # Global Defaults
    # -------------------------------------------------------------
    style.configure(".", background=BG_MAIN, foreground=FG_MAIN, font=FONT_REGULAR_14)
    
    # Structural frames
    style.configure("TFrame", background=BG_MAIN)
    style.configure("Surface.TFrame", background=BG_SURFACE)
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
    
    # -------------------------------------------------------------
    # Buttons
    # -------------------------------------------------------------
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
    
    # Progress Bar Formats
    style.configure("TProgressbar", thickness=4, background=ACCENT_BLUE, troughcolor=BG_SURFACE)

