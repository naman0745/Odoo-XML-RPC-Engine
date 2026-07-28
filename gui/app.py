import sys
from typing import Callable

from connection.auth_manager import AuthenticationManager, AuthenticatedContext
from controllers.import_controller import ImportController
from filesystem.folder_scanner import FolderScanner
from filesystem.import_manifest import ImportManifest
from filesystem.workspace_manager import WorkspaceManager
from filesystem.file_manager import FileManager
from services.partner_service import PartnerService
from services.product_service import ProductService
from services.purchase_order_service import PurchaseOrderService
from utils.logger import ImportLogger

from gui.main_window import MainWindow
from gui.style import apply_styles
from gui.controllers.gui_controller import GuiController


def init_unauthenticated(
    root: MainWindow, 
    workspace: WorkspaceManager,
    auth_manager: AuthenticationManager,
    on_auth_success: Callable[[AuthenticatedContext], None]
) -> GuiController:
    """
    Stage 1: Initialize the UI and passive systems without requiring an Odoo connection.
    Hooks the AuthManager into the UI controller.
    """
    apply_styles(root)
    
    scanner = FolderScanner(workspace)
    file_manager = FileManager(workspace)
    
    # Instantiate Controller explicitly without Business Logic
    controller = GuiController(
        root, 
        workspace, 
        scanner, 
        file_manager, 
        auth_manager, 
        on_auth_success
    )
    return controller


def init_authenticated(
    controller: GuiController, 
    context: AuthenticatedContext, 
    manifest: ImportManifest, 
    logger: ImportLogger
) -> None:
    """
    Stage 2: Construct the domain graph now that an authenticated session exists,
    and wire it into the waiting UI controller.
    """
    client = context.client
    
    partner_service = PartnerService(client)
    product_service = ProductService(client)
    po_service = PurchaseOrderService(client)
    
    import_ctrl = ImportController(
        partner_service=partner_service,
        product_service=product_service,
        po_service=po_service,
        logger=logger,
        manifest=manifest
    )
    
    controller.inject_authenticated_services(import_ctrl)


def main() -> int:
    """
    Entry point for the GUI application.
    """
    # 1. Initialize Root
    root = MainWindow()

    # 2. Workspace & Logging Core
    workspace = WorkspaceManager()
    workspace.ensure_workspace()
    manifest = ImportManifest(workspace.config / "import_manifest.json")
    logger = ImportLogger(log_file=str(workspace.logs / "import.log"))
    
    # 3. Startup Pipeline: Unauthenticated Stage
    auth_manager = AuthenticationManager()
    
    # Controller requires a callback to initialize domain graph upon success
    controller = None  # Reference required in closure
    
    def handle_auth_success(context: AuthenticatedContext):
        init_authenticated(controller, context, manifest, logger)
        
    controller = init_unauthenticated(root, workspace, auth_manager, handle_auth_success)
    
    # 4. Start Application (Will initialize into LoginView)
    controller.start()

    # 5. Enter event loop
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
