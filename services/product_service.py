from services.base_service import BaseService


class AmbiguousProductError(ValueError):
    def __init__(self, vendor_code, color, matches):
        self.vendor_code = vendor_code
        self.color = color
        self.matches = matches
        details = ", ".join(
            f"{match.get('id')}:{match.get('name')}" for match in matches
        )
        super().__init__(
            "Multiple products matched "
            f"Vendor Code='{vendor_code}', Color='{color}': {details}"
        )


class ProductService(BaseService):

    MODEL = "product.product"

    def get_product_by_id(self, product_id):
        result = self.client.read(
            self.MODEL,
            [product_id]
        )

        return result[0] if result else None

    def search_products(self, domain=None, fields=None, limit=100):
        if domain is None:
            domain = []

            return self.client.search_read(
        self.MODEL,
        domain=domain,
        fields=fields,
        limit=limit
    )

    def find_product(self, name):
        result = self.client.name_search(
            self.MODEL,
            name=name,
            limit=1
        )

        return result[0] if result else None

    def product_exists(self, name):
        return self.find_product(name) is not None

    def find_variant(
        self,
        vendor_code: str,
        Color: str,
    ) -> dict | None:
        """
        Find a single ``product.product`` variant by Vendor Code and Color.

        This is the canonical product-matching strategy for the PO import
        pipeline. Products must never be searched by display name.

        Odoo field mapping
        ------------------
        - **Vendor Code** is stored in ``product.product.x_vendor_code``
          (custom field).
        - **Color** is matched against the standard product variant attribute
          values via ``product.product.attribute_value_ids.name``.

        Parameters
        ----------
        vendor_code : str
            The vendor's style / article number (e.g. ``"VND-001"``).
        color : str
            The colour attribute value exactly as stored in Odoo
            (e.g. ``"Blue"``).

        Returns
        -------
        dict | None
            The first matching ``product.product`` record dict
            (fields: ``id``, ``name``, ``x_vendor_code``), or ``None``
            if no variant is found.
        """
        results = self.client.search_read(
            self.MODEL,
            domain=[
                ("x_vendor_code", "=", vendor_code),
                ("attribute_value_ids", "=", Color),
            ],
            fields=["id", "name", "x_vendor_code", "uom_id"],
            limit=2,
        )
        if len(results) > 1:
            raise AmbiguousProductError(vendor_code, Color, results)
        return results[0] if results else None
