from connection.odoo_client import OdooClient
from services.partner_service import PartnerService

client = OdooClient()
client.connect()

service = PartnerService(client)

vendors = service.search_partners(
    domain=[("supplier", "=", True)],
    fields=["id", "name"],
    limit=5
)

print(vendors)
print(type(vendors))

for vendor in vendors:
    print(vendor)
    
print(service.vendor_exists("Dell"))