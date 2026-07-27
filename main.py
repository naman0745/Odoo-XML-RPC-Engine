"""
Main entry point for the Purchase Order Importer application.

This module serves as the Composition Root of the application, responsible for:
1. Initializing the logging system.
2. Establishing the connection to the Odoo server.
3. Constructing the dependency tree (Services -> Controller).
4. Coordinating the import workflow execution.

Architecture:
    The application follows a layered architecture:
    [CLI/GUI] -> [ImportController] -> [Services] -> [OdooClient]
                                       -> [ExcelProcessor]
"""

import sys
from pathlib import Path
from typing import Tuple

from config.version import APP_VERSION
from config.settings import ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD
from connection.auth_manager import AuthenticationManager
from controllers.import_controller import ImportController, ImportResult
from filesystem.import_manifest import ImportManifest
from filesystem.workspace_manager import WorkspaceManager
from filesystem.file_manager import FileManager
from services.partner_service import PartnerService
from services.product_service import ProductService
from services.purchase_order_service import PurchaseOrderService
from utils.logger import ImportLogger


def bootstrap() -> Tuple[ImportController, ImportLogger, FileManager]:
    """
    Composition Root: Initializes all application dependencies in the
    correct order and returns the primary controller and logger.

    Returns:
        Tuple[ImportController, ImportLogger, FileManager]: The configured controller, logger, and file manager instance.

    Raises:
        Exception: If Odoo connection fails or dependency instantiation errors occur.
    """
    # Ensure the workspace folder structure exists.
    workspace = WorkspaceManager()
    workspace.ensure_workspace()

    # Initialize Logging
    logger = ImportLogger(log_file=str(workspace.logs / "import.log"))
    logger.info("Bootstrapping application dependencies...")

    # Initialize import manifest (duplicate protection)
    manifest = ImportManifest(workspace.config / "import_manifest.json")

    try:
        # Establish Odoo connection
        auth_manager = AuthenticationManager(url=ODOO_URL, db=ODOO_DB)
        context = auth_manager.authenticate(
            username=ODOO_USERNAME,
            password=ODOO_PASSWORD
        )
        
        client = context.client
        logger.info("Odoo connection established successfully.")

        # Initialize domain services
        partner_service = PartnerService(client)
        product_service = ProductService(client)
        po_service = PurchaseOrderService(client)

        # Initialize orchestration controller
        controller = ImportController(
            partner_service=partner_service,
            product_service=product_service,
            po_service=po_service,
            logger=logger,
            manifest=manifest,
        )

        logger.info("Application dependencies successfully initialized.")
        return controller, logger, FileManager(workspace)

    except Exception as e:
        logger.error(f"Critical failure during bootstrapping: {str(e)}")
        raise


def print_result(result: ImportResult) -> None:
    """
    Formats and prints the ImportResult to the console.
    """
    print("\n" + "=" * 40)
    print(f" IMPORT RESULT (v{APP_VERSION}) ")
    print("=" * 40)
    print(f"File:    {result.file_path}")
    print(f"Success: {'✅ YES' if result.success else '❌ NO'}")

    if result.order_id:
        print(f"Order ID: #{result.order_id}")

    if result.errors:
        print("\nFatal Errors:")
        for err in result.errors:
            print(f"  - {err}")

    if result.row_errors:
        print("\nRow Validation Errors:")
        for row_err in result.row_errors:
            print(f"  - {row_err}")

    print(f"\nProcessed: {result.rows_processed} rows")
    print(f"Failed:    {result.rows_failed} rows")
    print("=" * 40 + "\n")


def main() -> int:
    """
    Main execution loop for the CLI.

    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    # Handle CLI arguments
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_excel_file>")
        return 1

    file_path = sys.argv[1]

    try:
        # Setup execution environment
        controller, logger, file_manager = bootstrap()

        # Execute the workflow
        result = controller.import_file(file_path)

        # Output the outcome
        print_result(result)

        if result.success:
            try:
                final_path = file_manager.move_to_processed(Path(file_path))
                print(f"Moved workbook to: {final_path.name}")
            except Exception as e:
                print(f"⚠ Warning: PO created, but workbook could not be moved: {e}")

        return 0 if result.success else 1

    except Exception as e:
        # Handle fatal initialization errors
        print(f"\n[CRITICAL ERROR] Application failed to start: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
