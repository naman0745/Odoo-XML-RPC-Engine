from connection.odoo_client import OdooClient

client = OdooClient()
client.connect()

companies = client.search_read(
    model="res.company",
    domain=[],
    fields=["id", "name"]
)

print(companies)