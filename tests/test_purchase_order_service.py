from connection.odoo_client import OdooClient
from services.purchase_order_service import PurchaseOrderService


client = OdooClient()
client.connect()

service = PurchaseOrderService(client)

# --- search_orders ---
print("\n--- search_orders (limit 3) ---")
orders = service.search_orders(
    fields=["id", "name", "partner_id", "state"],
    limit=3
)
for order in orders:
    print(order)

# --- get_order_by_id ---
if orders:
    first_id = orders[0]["id"]
    print(f"\n--- get_order_by_id({first_id}) ---")
    order = service.get_order_by_id(first_id)
    print(order)

    # --- order_exists ---
    first_name = orders[0]["name"]
    print(f"\n--- order_exists('{first_name}') ---")
    print(service.order_exists(first_name))

    # --- get_order_lines ---
    print(f"\n--- get_order_lines({first_id}) ---")
    lines = service.get_order_lines(
        first_id,
        fields=["id", "product_id", "product_qty", "price_unit", "date_planned"]
    )
    for line in lines:
        print(line)
else:
    print("No purchase orders found in this Odoo instance.")
