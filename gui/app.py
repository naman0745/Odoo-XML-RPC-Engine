import sys

from connection.odoo_client import OdooClient
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


def main() -> int:
    """
    Entry point for the GUI application.
    Independent from the CLI (main.py).
    """
    # 1. Initialize Root
    root = MainWindow()

    # 2. Configure Global Styling
    apply_styles(root)

    # 3. Initialize Backend Components
    workspace = WorkspaceManager()
    workspace.ensure_workspace()
    
    manifest = ImportManifest(workspace.config / "import_manifest.json")
    scanner = FolderScanner(workspace)
    
    logger = ImportLogger()
    import_ctrl = None
    client_connected = False
    
    try:
        client = OdooClient()
        client.connect()
        client_connected = True
        
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
    except Exception as e:
        logger.error(f"Failed to connect to backend: {e}")

    # 4. Instantiate Controller explicitly connecting UI to Business Logic
    file_manager = FileManager(workspace)
    controller = GuiController(root, workspace, scanner, import_ctrl, client_connected, file_manager)

    # 5. Start Application
    controller.start()

    # 6. Enter event loop
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
