from connection.odoo_client import OdooClient
from services.partner_service import PartnerService
from services.product_service import ProductService
from services.purchase_order_service import PurchaseOrderService
from controllers.import_controller import ImportController

client = OdooClient()
client.connect()

controller = ImportController(
    partner_service=PartnerService(client),
    product_service=ProductService(client),
    po_service=PurchaseOrderService(client),
)

# Replace this path with a real test Excel file before running.
FILE_PATH = "D:/PO_import/PO1.xlsx"

print(f"\n--- Running import: {FILE_PATH} ---")
result = controller.import_file(FILE_PATH)

print(f"\nSuccess       : {result.success}")
print(f"Order ID      : {result.order_id}")
print(f"Rows processed: {result.rows_processed}")
print(f"Rows failed   : {result.rows_failed}")

if result.errors:
    print("\nErrors:")
    for e in result.errors:
        print(f"  {e}")

if result.row_errors:
    print("\nRow Errors:")
    for e in result.row_errors:
        print(f"  {e}")
