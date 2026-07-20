from connection.odoo_client import OdooClient
from services.product_service import ProductService


client = OdooClient()
client.connect()

service = ProductService(client)

products = service.search_products(
    fields=["id", "name"],
    limit=5
)

for product in products:
    print(product)

    print()

    product = service.find_product(
        "[125U9001-BLK] 125U9001 (BLACK)"
    )

    print(product)

print(service.product_exists("[125U9001-BLK] 125U9001 (BLACK)"))


products = client.search_read(
    "product.product",
    [("attribute_value_ids", "=", "WG-DAL-DALMATIAN")],
    []
)

print(f"Found {len(products)} products\n")

for product in products:
    print(product)