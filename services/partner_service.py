from services.base_service import BaseService


class AmbiguousVendorError(ValueError):
    def __init__(self, vendor_name, matches):
        self.vendor_name = vendor_name
        self.matches = matches
        details = ", ".join(
            f"{match.get('id')}:{match.get('name')}" for match in matches
        )
        super().__init__(
            f"Multiple vendors matched '{vendor_name}': {details}"
        )


class PartnerService(BaseService):

    MODEL = "res.partner"

    def get_partner_by_id(self, partner_id):
        result = self.client.read(
            self.MODEL,
            [partner_id]
        )

        return result[0] if result else None

    def search_partners(self, domain=None, fields=None, limit=100):
        if domain is None:
            domain = []

        return self.client.search_read(
        self.MODEL,
        domain=domain,
        fields=fields,
        limit=limit
    )

    def get_vendor(self, vendor_name):
        vendors = self.client.search_read(
            self.MODEL,
            domain=[
                ("supplier", "=", True),
                ("name", "=", vendor_name)
            ],
            limit=2
        )

        if len(vendors) > 1:
            raise AmbiguousVendorError(vendor_name, vendors)

        return vendors[0] if vendors else None

    def vendor_exists(self, vendor_name):
        return self.get_vendor(vendor_name) is not None
