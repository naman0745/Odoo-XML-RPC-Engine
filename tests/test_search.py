from connection.odoo_client import OdooClient

client = OdooClient()
client.connect()

ids = client.search(
    model="res.company",
    domain=[]
)

print(ids)