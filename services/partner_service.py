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
