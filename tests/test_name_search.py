from connection.odoo_client import OdooClient

client = OdooClient()
client.connect()

products = client.name_search(
    model="product.product",
    name="AL1SB7117-AC"
)

print(products)