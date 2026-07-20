from connection.odoo_client import OdooClient
from services.purchase_order_service import PurchaseOrderService


client = OdooClient()
client.connect()

service = PurchaseOrderService(client)

print("PurchaseOrderService initialized successfully.")