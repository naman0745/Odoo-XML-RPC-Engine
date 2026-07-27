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

from typing import Optional, Callable

from connection.auth_manager import AuthenticationManager, AuthenticatedContext
from connection.exceptions import OdooConnectionError, AuthenticationExpiredError, ConnectionLostError
from controllers.import_controller import ImportController, ImportResult
from filesystem.folder_scanner import FolderScanner
from filesystem.workspace_manager import WorkspaceManager
from filesystem.file_manager import FileManager
from gui.main_window import MainWindow
from gui.models.ui_models import PendingOrderInfo
from gui.views.failure_view import FailureView
from gui.views.progress_view import ProgressView
from gui.views.scan_view import ScanView
from gui.views.success_view import SuccessView
from gui.style import apply_styles
from config.app_config import AppConfig
import time
import os
import subprocess
import keyring
from config.settings import ODOO_USERNAME

APP_KEYRING_SERVICE = "PO_Importer_App"



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
        file_manager: FileManager,
        auth_manager: AuthenticationManager,
        on_auth_success: Callable[[AuthenticatedContext], None]
    ) -> None:
        self.window = main_window
        self.workspace = workspace
        self.scanner = scanner
        self.file_manager = file_manager
        self.auth_manager = auth_manager
        self.on_auth_success = on_auth_success
        
        self.import_ctrl = None
        self.is_connected = False
        
        # Instantiate views
        from gui.views.login_view import LoginView
        self.login_view = LoginView(self.window.content_container)
        self.scan_view = ScanView(self.window.content_container)
        self.progress_view = ProgressView(self.window.content_container)
        self.success_view = SuccessView(self.window.content_container)
        self.failure_view = FailureView(self.window.content_container)

        self.window.register_views(
            self.login_view,
            self.scan_view, 
            self.progress_view, 
            self.success_view, 
            self.failure_view
        )

        self.window.header.set_connection_status(self.is_connected, errored=False)
        self._bind_events()
        self.window.protocol("WM_DELETE_WINDOW", self._on_window_close)

        # State
        self._batch_queue: list[PendingOrderInfo] = []
        self._batch_results: list[dict] = []
        self._batch_total: int = 0
        self._current_processing_order: Optional[PendingOrderInfo] = None
        self._is_importing: bool = False
        self._sim_run_id: int = 0

    def inject_authenticated_services(self, import_ctrl: ImportController) -> None:
        """
        Populate the controller with its primary domain dependency post-login.
        Transitions the UI state to connected.
        """
        self.import_ctrl = import_ctrl
        self.is_connected = True
        self.window.header.set_connection_status(True, errored=False)


    def _bind_events(self) -> None:
        self.login_view.on_login = self._attempt_login
        
        self.scan_view.on_selection_changed = None # unused locally
        self.scan_view.on_refresh = self._handle_refresh
        self.scan_view.on_process_clicked = self._start_batch_import
        self.scan_view.on_open_folder = self._open_incoming_folder
        self.scan_view.on_change_folder = self._change_folder

        self.success_view.on_back_clicked = self.start
        self.success_view.on_view_failure = self._handle_drill_down_failure
        
        # For fatal failures blocking the sequence
        self.failure_view.on_retry_clicked = self.start
        self.failure_view.on_back_clicked = self.start
        self.failure_view.on_open_excel_clicked = self._open_failed_file_in_excel

        # Global Config Actions
        self.window.header.logout_btn.bind("<Button-1>", self._handle_logout_click)
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
                os.startfile(str(target.resolve()))
            except Exception:
                pass
        else:
            from tkinter import messagebox
            messagebox.showinfo("No Logs", "No log file found yet. Run an import to generate logs.", parent=self.window)

    def _open_failed_file_in_excel(self) -> None:
        """Opens the physically targeted file in Excel for manual corrections."""
        order_to_open = getattr(self, '_current_error_order', None) or getattr(self, '_selected_order', None)
        
        if order_to_open and order_to_open.full_path:
            import os
            try:
                os.startfile(order_to_open.full_path)
            except Exception:
                # Silently catch OS errors if there's no handler or if it fails
                pass

    def _handle_drill_down_failure(self, args: list) -> None:
        """Route to FailureView dynamically, modifying the Back button to bounce to SuccessView."""
        result, order = args
        
        self._current_error_order = order
        
        self.failure_view.set_error(
            workbook=order.filename,
            stage="Batch Execution",
            checked=result.rows_processed,
            failed=result.rows_failed,
            fatal_error=result.errors[0] if result.errors else "Unknown Error",
            row_errors=result.row_errors
        )
        
        # Override the return routing temporarily
        original_back = self.failure_view.on_back_clicked
        original_retry = self.failure_view.on_retry_clicked
        
        def _return_to_batch():
            self._current_error_order = None
            self.window.show_view("success")
            self.failure_view.on_back_clicked = original_back
            self.failure_view.on_retry_clicked = original_retry
            
        self.failure_view.on_back_clicked = _return_to_batch
        self.failure_view.on_retry_clicked = _return_to_batch
        self.window.show_view("failure")

    def _handle_enter_key(self, event) -> None:
        if getattr(self, '_is_importing', False):
            return
            
        current_view = self.window._current_view
        if current_view == self.window._views.get("scan"):
            if getattr(self.scan_view, "process_btn", None) and self.scan_view.process_btn.cget("state") == "normal":
                self._start_batch_import(self.scan_view._selected_orders)
        elif current_view == self.window._views.get("success"):
            self.start()
        elif current_view == self.window._views.get("failure"):
            self.start()

    def _handle_escape_key(self, event) -> None:
        if getattr(self, '_is_importing', False):
            return
            
        current_view = self.window._current_view
        if current_view in (self.window._views.get("success"), 
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
        
        if not self.is_connected:
            self.window.show_view("login")
            
            config = AppConfig()
            last_user = config.get_last_username()
            if not last_user:
                last_user = ODOO_USERNAME or ""

            if last_user:
                try:
                    saved_password = keyring.get_password(APP_KEYRING_SERVICE, last_user)
                    if saved_password:
                        self.login_view.set_credentials(last_user, saved_password, remember=True)
                        self.window.after(100, lambda: self._attempt_login(last_user, saved_password, remember_me=True))
                        return
                except Exception:
                    pass

            self.login_view.clear_password()
        else:
            self.window.show_view("scan")
            self._handle_refresh()

    def _handle_logout_click(self, event=None) -> None:
        if getattr(self, '_is_importing', False) or not self.is_connected:
            return
        if messagebox.askyesno("Logout", "Are you sure you want to log out of Odoo?", parent=self.window):
            self.logout()

    def logout(self) -> None:
        if getattr(self, '_is_importing', False) and self.is_connected:
            return
            
        self.auth_manager.logout()
        last_user = AppConfig().get_last_username()
        if last_user:
            try:
                keyring.delete_password(APP_KEYRING_SERVICE, last_user)
            except Exception:
                pass
                
        self.is_connected = False
        self.import_ctrl = None
        self.window.header.set_connection_status(False, errored=False)
        self.start()

    def _attempt_login(self, username, password, remember_me=False) -> None:
        try:
            context = self.auth_manager.authenticate(username, password)
            
            if remember_me:
                AppConfig().set_last_username(username)
                try:
                    keyring.set_password(APP_KEYRING_SERVICE, username, password)
                except Exception:
                    pass
            else:
                try:
                    keyring.delete_password(APP_KEYRING_SERVICE, username)
                except Exception:
                    pass

            self.login_view.clear_password()
            self.login_view.clear_error()
            self.on_auth_success(context)
            self.start()
        except OdooConnectionError as e:
            self.login_view.show_error(str(e))
            self.login_view.clear_password()
        except Exception as e:
            self.login_view.show_error(str(e))
            self.login_view.clear_password()

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
            pass

    def _change_folder(self) -> None:
        """Allow user to change the workspace folder."""
        from tkinter import filedialog
        from config.app_config import AppConfig
        
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

    # -------------------------------------------------------------
    # Batch Processing Pipeline 
    # -------------------------------------------------------------

    def _start_batch_import(self, orders: list[PendingOrderInfo], custom_mappings: dict = None) -> None:
        if not self.import_ctrl:
            self.failure_view.set_error(
                "Could not connect to Odoo backend. Please check network.",
                "0 rows validated", "CONNECTION_ERROR", "Connecting"
            )
            self.window.show_view("failure")
            return
            
        if not custom_mappings: # Only reset on initial start
            self._batch_queue = orders.copy()
            self._batch_results = []
            self._batch_total = len(orders)
            self._batch_start_time = time.time()
        
        self._is_importing = True
        self._process_next_in_batch(custom_mappings)

    def _process_next_in_batch(self, custom_mappings: dict = None) -> None:
        if not self._batch_queue:
            self._finish_batch()
            return
            
        self._current_processing_order = self._batch_queue.pop(0)
        
        idx = len(self._batch_results) + 1
        self.progress_view.set_filename(f"Batch ({idx}/{self._batch_total}): {self._current_processing_order.filename}")
        self.progress_view.reset()
        self.window.show_view("progress")
        
        self._sim_run_id += 1
        self._simulate_progress(0, 500, self._sim_run_id)
        target_path = self._current_processing_order.full_path
        
        def _worker():
            try:
                result = self.import_ctrl.import_file(str(target_path), user_mappings=custom_mappings)
                self.window.after(0, self._on_import_finished, result)
            except Exception as e:
                self.window.after(0, self._on_import_crashed, e)
                
        threading.Thread(target=_worker, daemon=True).start()



    def _simulate_progress(self, idx: int, delay_ms: int, expected_sim_id: int = -1) -> None:
        """Advance checklist items visually to keep the UI feeling 'alive' during blocking operations."""
        if not self._is_importing or self._sim_run_id != expected_sim_id:
            return
            
        stages = 6
        if idx > 0:
            self.progress_view.update_step(idx - 1, "complete")
        
        if idx < stages:
            self.progress_view.update_step(idx, "active")
            next_delay = min(delay_ms * 2, 2000) 
            self.window.after(delay_ms, self._simulate_progress, idx + 1, next_delay, expected_sim_id)

    def _on_import_finished(self, result: ImportResult) -> None:
        """Handle the result object returned from the backend thread."""
        self._sim_run_id += 1 
        if result.success:
            for i in range(6):
                self.progress_view.update_step(i, "complete")
        else:
            for i in range(6):
                self.progress_view.update_step(i, "failed")
            
        if not result.success and result.ambiguities:
            self._batch_queue.insert(0, self._current_processing_order) # Put it back to retry
            from gui.views.resolution_modal import ResolutionModal
            ResolutionModal(self.window, result.ambiguities, self._retry_with_mappings)
            return

        move_success = False
        if result.success:
            try:
                self.file_manager.move_to_processed(Path(self._current_processing_order.full_path))
                move_success = True
            except Exception:
                move_success = False

        self._batch_results.append({
            "order": self._current_processing_order,
            "result": result,
            "moved": move_success
        })
        
        # Advance batch with a longer delay on failure so the crosses are visible
        delay = 100 if result.success else 600
        self.window.after(delay, self._process_next_in_batch)

    def _finish_batch(self) -> None:
        self._is_importing = False
        duration = time.time() - self._batch_start_time
        time_str = f"{duration:.1f}s" if duration > 0.1 else "< 1s"
        
        now_str = datetime.now().strftime("%I:%M %p").lower().lstrip("0")
        self.window.status_bar.set_last_import(f"Last import: today at {now_str}")
        
        # UX Fast-path: If user only selected 1 file and it failed, skip the listbox entirely and show real errors
        if self._batch_total == 1:
            res = self._batch_results[0]["result"]
            if not res.success:
                order = self._batch_results[0]["order"]
                self._current_error_order = order
                self.failure_view.set_error(
                    workbook=order.filename,
                    stage="Import Pipeline",
                    checked=res.rows_processed,
                    failed=res.rows_failed,
                    fatal_error=res.errors[0] if res.errors else "Unknown Error",
                    row_errors=res.row_errors
                )
                
                # Reset routes
                def _return_to_start():
                    self._current_error_order = None
                    self.start()
                    
                self.failure_view.on_back_clicked = _return_to_start
                self.failure_view.on_retry_clicked = _return_to_start
                
                self.window.show_view("failure")
                return

        self.success_view.set_batch_results(self._batch_results, time_str)
        self.window.show_view("success")

    def _on_import_crashed(self, exception: Exception) -> None:
        """Handle unexpected crashes from the backend thread."""
        self._sim_run_id += 1  # Halt simulation override
        self._is_importing = False
        
        # Intercept Domain Connection Exceptions
        if isinstance(exception, (AuthenticationExpiredError, ConnectionLostError)):
            messagebox.showerror(
                "Connection Lost", 
                str(exception) + "\n\nAborting batch and disconnecting.", 
                parent=self.window
            )
            self.logout()
            return
            
        pseudo_res = ImportResult(success=False, file_path=str(self._current_processing_order.full_path), errors=[str(exception)])
        self._batch_results.append({
            "order": self._current_processing_order,
            "result": pseudo_res,
            "moved": False
        })
        
        for i in range(6):
            self.progress_view.update_step(i, "failed")
            
        self.window.after(600, self._process_next_in_batch)

    def _retry_with_mappings(self, mappings: dict) -> None:
        """Called by the ResolutionModal to resubmit with user mappings."""
        if self._current_processing_order:
            self._process_next_in_batch(custom_mappings=mappings)
