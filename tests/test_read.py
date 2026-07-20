from connection.odoo_client import OdooClient

client = OdooClient()
client.connect()

companies = client.read(
    model="res.company",
    ids=[1],
    fields=["id", "name"]
)

print(companies)