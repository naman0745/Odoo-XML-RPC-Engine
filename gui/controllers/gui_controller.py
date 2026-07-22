"""
gui/controllers/gui_controller.py
"""
import os
import threading
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
from datetime import datetime
from pathlib import Path
from typing import Optional

from controllers.import_controller import ImportController, ImportResult
from filesystem.folder_scanner import FolderScanner
from filesystem.workspace_manager import WorkspaceManager
from filesystem.file_manager import FileManager
from gui.main_window import MainWindow
from gui.models.ui_models import PendingOrderInfo
from gui.views.failure_view import FailureView
from gui.views.progress_view import ProgressView
from gui.views.ready_view import ReadyView
from gui.views.scan_view import ScanView
from gui.views.success_view import SuccessView
from gui.views.settings_modal import SettingsModal
from gui.style import apply_styles
from config.app_config import AppConfig
import time
import os
import subprocess


class GuiController:
    """
    Bridge between the GUI views and backend. Connects passive views to
    FolderScanner, ImportController, and WorkspaceManager.
    """
    def __init__(
        self, 
        main_window: MainWindow, 
        workspace: WorkspaceManager,
        scanner: FolderScanner,
        import_ctrl: Optional[ImportController],
        is_connected: bool,
        file_manager: FileManager
    ) -> None:
        self.window = main_window
        self.workspace = workspace
        self.scanner = scanner
        self.import_ctrl = import_ctrl
        self.is_connected = is_connected
        self.file_manager = file_manager
        
        # Instantiate views
        self.scan_view = ScanView(self.window.content_container)
        self.ready_view = ReadyView(self.window.content_container)
        self.progress_view = ProgressView(self.window.content_container)
        self.success_view = SuccessView(self.window.content_container)
        self.failure_view = FailureView(self.window.content_container)

        self.window.register_views(
            self.scan_view, 
            self.ready_view, 
            self.progress_view, 
            self.success_view, 
            self.failure_view
        )

        # Update initial connection status in the header
        self.window.header.set_connection_status(is_connected, errored=False)

        # Wire up event hooks
        self._bind_events()
        self.window.protocol("WM_DELETE_WINDOW", self._on_window_close)

        # State
        self._selected_order: Optional[PendingOrderInfo] = None
        self._is_importing: bool = False

    def _bind_events(self) -> None:
        self.scan_view.on_order_selected = self._handle_order_selected
        self.scan_view.on_refresh = self._handle_refresh
        self.scan_view.on_import_clicked = self._handle_ready_to_import
        self.scan_view.on_open_folder = self._open_incoming_folder
        self.scan_view.on_change_folder = self._change_folder
        self.scan_view.on_theme_toggle = self._toggle_theme

        self.ready_view.on_back_clicked = self.start
        self.ready_view.on_import_clicked = self._start_import

        self.success_view.on_back_clicked = self.start
        self.success_view.on_process_next_clicked = self._process_next_file
        
        # For failures, we can go back to start, retry, or open in Excel
        self.failure_view.on_retry_clicked = self._start_import
        self.failure_view.on_back_clicked = self.start
        self.failure_view.on_open_excel_clicked = self._open_failed_file_in_excel

        # Global Config Actions
        self.window.header._gear_btn.bind("<Button-1>", lambda e: self._open_settings())
        self.window.status_bar._conf_lbl.bind("<Button-1>", lambda e: self._open_settings())
        self.window.status_bar._log_lbl.bind("<Button-1>", lambda e: self._open_log_file())

        # Keyboard Navigation
        self.window.bind("<Return>", self._handle_enter_key)
        self.window.bind("<Escape>", self._handle_escape_key)
        self.window.bind("<Control-r>", self._handle_ctrl_r_key)
        self.window.bind("<Control-R>", self._handle_ctrl_r_key)

    def _open_log_file(self) -> None:
        default_log = self.workspace.logs / "import.log"
        fallback_log = Path("logs/import.log")
        
        target = default_log if default_log.exists() else fallback_log
        if target.exists():
            try:
                os.startfile(str(target))
            except Exception:
                # If on Mac/Linux or failure
                pass
        else:
            from tkinter import messagebox
            messagebox.showinfo("No Logs", "No log file found yet. Run an import to generate logs.", parent=self.window)

    def _open_settings(self) -> None:
        SettingsModal(self.window, on_settings_changed=self._apply_settings)

    def _apply_settings(self) -> None:
        """Called automatically after Save & Apply is pressed inside the Settings Modal."""
        # 1. Flash new color profile
        apply_styles(self.window)

    def _open_failed_file_in_excel(self) -> None:
        if getattr(self, '_selected_order', None) and self._selected_order.full_path:
            try:
                os.startfile(str(self._selected_order.full_path))
            except Exception:
                # Silently catch OS errors if there's no handler or if it fails
                pass

    def _process_next_file(self) -> None:
        """Invoked from Success view to seamlessly jump into the next Ready state."""
        pending_paths = self.scanner.get_pending_files()
        
        if not pending_paths:
            self.start()
            return
            
        next_path = pending_paths[0]
        try:
            stats = next_path.stat()
            size_kb = max(1, stats.st_size // 1024)
            mod_date = datetime.fromtimestamp(stats.st_mtime).strftime("%d %b")
            
            self._selected_order = PendingOrderInfo(next_path.name, size_kb, mod_date, next_path)
            self._handle_ready_to_import()
        except OSError:
            self.start()

    def _handle_enter_key(self, event) -> None:
        if getattr(self, '_is_importing', False):
            return
            
        current_view = self.window._current_view
        if current_view == self.window._views.get("scan"):
            self._handle_ready_to_import()
        elif current_view == self.window._views.get("ready"):
            self._start_import()
        elif current_view == self.window._views.get("success"):
            if self.success_view.action_btn.cget("text").startswith("Process Next"):
                self._process_next_file()
            else:
                self.start()
        elif current_view == self.window._views.get("failure"):
            self._start_import()

    def _handle_escape_key(self, event) -> None:
        if getattr(self, '_is_importing', False):
            return
            
        current_view = self.window._current_view
        if current_view in (self.window._views.get("ready"), 
                            self.window._views.get("success"), 
                            self.window._views.get("failure")):
            self.start()

    def _handle_ctrl_r_key(self, event) -> None:
        if getattr(self, '_is_importing', False):
            return
            
        if self.window._current_view == self.window._views.get("scan"):
            self._handle_refresh()

    def _on_window_close(self) -> None:
        """Prevent the application from closing if an import is running."""
        if getattr(self, '_is_importing', False):
            messagebox.showwarning(
                "Import in Progress", 
                "An import is currently running in the background. Please wait for it to finish before closing the application."
            )
        else:
            self.window.destroy()

    def start(self) -> None:
        """Initial entry point simulating a freshly booted app or returning to scan."""
        self._selected_order = None
        self._is_importing = False
        self.window.show_view("scan")
        self._handle_refresh()

    def _handle_refresh(self) -> None:
        """Scan real folder for pending orders and update the ScanView."""
        pending_paths = self.scanner.get_pending_files()
        
        gui_orders = []
        for path in pending_paths:
            try:
                stats = path.stat()
                size_kb = max(1, stats.st_size // 1024)
                mod_date = datetime.fromtimestamp(stats.st_mtime).strftime("%d %b")
                gui_orders.append(
                    PendingOrderInfo(path.name, size_kb, mod_date, path)
                )
            except OSError:
                continue
                
        now_str = datetime.now().strftime("%I:%M %p").lower().lstrip("0")
        self.scan_view.load_files(
            gui_orders, 
            last_scanned=f"today at {now_str}",
            incoming_path=str(self.workspace.incoming)
        )
        
    def _open_incoming_folder(self) -> None:
        """Open the OS default file explorer for the incoming directory."""
        try:
            os.startfile(self.workspace.incoming)
        except AttributeError:
            # Fallback if not on Windows (though UX spec dictates Windows desktop)
            pass

    def _change_folder(self) -> None:
        """Allow user to change the workspace folder."""
        current_path = str(self.workspace.root)
        new_dir = filedialog.askdirectory(
            initialdir=current_path,
            parent=self.window,
            title="Select Workspace Folder"
        )
        if new_dir and new_dir != current_path:
            # Update workspace configuration
            AppConfig().set_workspace_path(Path(new_dir))
            self.workspace._root = Path(new_dir)
            self.workspace.ensure_workspace()
            # Refresh to show files from new location
            self._handle_refresh()

    def _toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        current_theme = AppConfig().get_theme()
        new_theme = "dark" if current_theme == "light" else "light"
        AppConfig().set_theme(new_theme)
        apply_styles(self.window)

    def _handle_order_selected(self, order: PendingOrderInfo) -> None:
        self._selected_order = order

    def _handle_ready_to_import(self) -> None:
        if self._selected_order:
            self.ready_view.set_order(self._selected_order)
            self.window.show_view("ready")

    def _start_import(self) -> None:
        """
        Transition to progress state and dispatch the blocking ImportController
        work to a background thread to keep the GUI responsive.
        """
        if not self._selected_order or self._is_importing:
            return
            
        # Re-check backend component availability
        if not self.import_ctrl:
            self.failure_view.set_error(
                "Could not connect to Odoo backend. Please restart the application or check your network.",
                "0 rows validated · 0 rows imported",
                "CONNECTION_ERROR",
                "Connecting to Odoo"
            )
            self.window.header.set_connection_status(False, errored=True)
            self.window.show_view("failure")
            return
            
        self._is_importing = True
        self.progress_view.set_filename(self._selected_order.filename)
        self.progress_view.reset()
        self.window.show_view("progress")
        
        self._import_start_time = time.time()

        # Kick off visual progress simulation in the main thread (for user feedback)
        # while the backend threads blocking IO underneath.
        self._simulate_progress(0, 500)
        
        target_path = self._selected_order.full_path
        
        def _worker():
            try:
                # The backend call is fully synchronous
                result = self.import_ctrl.import_file(str(target_path))
                self.window.after(0, self._on_import_finished, result)
            except Exception as e:
                self.window.after(0, self._on_import_crashed, e)
                
        threading.Thread(target=_worker, daemon=True).start()

    def _simulate_progress(self, idx: int, delay_ms: int) -> None:
        """Advance checklist items visually to keep the UI feeling 'alive' during blocking operations."""
        if not self._is_importing:
            return
            
        stages = 6
        if idx > 0:
            self.progress_view.update_step(idx - 1, "complete")
        
        if idx < stages:
            self.progress_view.update_step(idx, "active")
            # Step slower as it goes further so we don't 'finish' simulated progress 
            # wildly early before the real backend finishes.
            next_delay = min(delay_ms * 2, 2000) 
            self.window.after(delay_ms, self._simulate_progress, idx + 1, next_delay)

    def _on_import_finished(self, result: ImportResult) -> None:
        """Handle the result object returned from the backend thread."""
        self._is_importing = False
        
        # Complete checklist visually to 100% just before showing results
        for i in range(6):
            self.progress_view.update_step(i, "complete")
            
        if result.success:
            try:
                self.file_manager.move_to_processed(Path(self._selected_order.full_path))
                move_status = "Moved to Processed Orders"
                move_success = True
            except Exception as e:
                move_status = f"Failed to move file ({e})"
                move_success = False

            duration = time.time() - getattr(self, '_import_start_time', time.time())
            time_str = f"{duration:.1f}s" if duration > 0.1 else "< 1s"
            
            self.success_view.set_result(
                po_id=f"PO{result.order_id}", 
                workbook=self._selected_order.filename,
                rows_total=result.rows_processed, 
                time_taken=time_str,
                move_status=move_status, 
                move_success=move_success
            )
            # Log the timestamp in footer
            now_str = datetime.now().strftime("%I:%M %p").lower().lstrip("0")
            self.window.status_bar.set_last_import(f"Last import: today at {now_str}")
            
            pending_paths = self.scanner.get_pending_files()
            self.success_view.set_pending_count(len(pending_paths))

            self.window.show_view("success")
        else:
            # Reformat error list for the FailureView
            if result.duplicate_of:
                primary_error = result.errors[0]
                stage = "Checking Manifest"
            else:
                primary_error = result.errors[0] if result.errors else "An unexpected error occurred."
                stage = "Execution"

            self.failure_view.set_error(
                workbook=self._selected_order.filename if self._selected_order else "Unknown",
                stage=stage,
                checked=result.rows_processed,
                failed=result.rows_failed,
                fatal_error=primary_error,
                row_errors=result.row_errors
            )
            self.window.show_view("failure")

    def _on_import_crashed(self, exception: Exception) -> None:
        """Handle unexpected crashes from the backend thread."""
        self._is_importing = False
        self.failure_view.set_error(
            workbook=self._selected_order.filename if self._selected_order else "Unknown",
            stage="Execution Pipeline",
            checked=0,
            failed=0,
            fatal_error=str(exception),
            row_errors=[]
        )
        self.window.show_view("failure")
