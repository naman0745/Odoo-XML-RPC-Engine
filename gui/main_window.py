"""
gui/main_window.py
"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional

from config.version import APP_VERSION
from gui.views.failure_view import FailureView
from gui.views.progress_view import ProgressView
from gui.views.ready_view import ReadyView
from gui.views.scan_view import ScanView
from gui.views.success_view import SuccessView
from gui.widgets.header_band import HeaderBand
from gui.widgets.status_bar import StatusBar


class MainWindow(tk.Tk):
    """
    The Single Root Window. 
    Manages the 5 mutually exclusive states defined in UX Spec V2.1.
    """
    def __init__(self) -> None:
        super().__init__()
        self.title(f"Purchase Order Importer v{APP_VERSION}")
        self.geometry("760x560")
        self.minsize(640, 480)
        
        # Grid layout for root
        self.rowconfigure(1, weight=1)  # The content area is stretchy
        self.columnconfigure(0, weight=1)

        # 1. Header Band
        self.header = HeaderBand(self)
        self.header.grid(row=0, column=0, sticky="ew")

        # 2. Main Content Container
        self.content_container = ttk.Frame(self, style="TFrame")
        self.content_container.grid(row=1, column=0, sticky="nsew")
        
        # Center the content uniformly up to max-width 640px. 
        # (For simplicity here, we let the inner frame expand up to that)
        self.content_container.columnconfigure(0, weight=1)
        self.content_container.rowconfigure(0, weight=1)

        self._current_view: Optional[ttk.Frame] = None
        self._views: Dict[str, ttk.Frame] = {}

        # 3. Footer Band
        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=2, column=0, sticky="ew")

    def register_views(
        self,
        scan_view: ScanView,
        ready_view: ReadyView,
        progress_view: ProgressView,
        success_view: SuccessView,
        failure_view: FailureView
    ) -> None:
        """Register instantiated views."""
        self._views = {
            "scan": scan_view,
            "ready": ready_view,
            "progress": progress_view,
            "success": success_view,
            "failure": failure_view
        }

    def show_view(self, view_name: str) -> None:
        """Swap out the content area for the requested view."""
        if view_name not in self._views:
            raise ValueError(f"Unknown view: {view_name}")

        view = self._views[view_name]

        if self._current_view and self._current_view != view:
            self._current_view.grid_forget()

        self._current_view = view
        
        # Add to container
        view.grid(row=0, column=0, sticky="nsew")
