from services.base_service import BaseService


class PurchaseOrderService(BaseService):
    """
    Service for all Odoo ``purchase.order`` and ``purchase.order.line``
    operations.

    Responsibility
    --------------
    Communicate with Odoo exclusively through the injected ``OdooClient``.
    This service does not read Excel files, validate data, log, coordinate
    imports, or perform any I/O beyond XML-RPC calls.

    The caller (controller / main pipeline) is responsible for:
    - Resolving vendor names to ``partner_id`` integers via ``PartnerService``.
    - Resolving product names/SKUs to ``product_id`` integers via
      ``ProductService``.
    - Validating row data before passing it to ``create_order``.
    - Handling errors returned or raised by these methods.
    """

    ORDER_MODEL = "purchase.order"
    LINE_MODEL = "purchase.order.line"

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def get_order_by_id(self, order_id: int) -> dict | None:
        """
        Fetch a single purchase order header by its Odoo database ID.

        Parameters
        ----------
        order_id : int
            The ``purchase.order`` record ID.

        Returns
        -------
        dict | None
            A dictionary of all default Odoo fields for the record,
            or ``None`` if no record is found.
        """
        results = self.client.search_read(
            self.ORDER_MODEL,
            domain=[("id", "=", order_id)],
            limit=1
        )
        return results[0] if results else None

    def search_orders(
        self,
        domain: list | None = None,
        fields: list | None = None,
        limit: int = 100
    ) -> list[dict]:
        """
        Search purchase orders with an arbitrary domain.

        Parameters
        ----------
        domain : list | None
            An Odoo domain filter, e.g. ``[("state", "=", "purchase")]``.
            Defaults to ``[]`` (all records).
        fields : list | None
            List of field names to return. If ``None``, Odoo returns all
            default fields.
        limit : int
            Maximum number of records to return. Defaults to ``100``.

        Returns
        -------
        list[dict]
            A list of purchase order dictionaries.
        """
        if domain is None:
            domain = []

        return self.client.search_read(
            self.ORDER_MODEL,
            domain=domain,
            fields=fields,
            limit=limit
        )

    def order_exists(self, name: str) -> bool:
        """
        Check whether a purchase order with the given reference name exists.

        Parameters
        ----------
        name : str
            The PO reference as it appears in Odoo (e.g. ``"P00042"``).

        Returns
        -------
        bool
            ``True`` if at least one matching record exists, ``False``
            otherwise.
        """
        ids = self.client.search(
            self.ORDER_MODEL,
            domain=[("name", "=", name)]
        )
        return bool(ids)

    def get_order_lines(
        self,
        order_id: int,
        fields: list | None = None
    ) -> list[dict]:
        """
        Fetch all line items belonging to a purchase order.

        Parameters
        ----------
        order_id : int
            The ``purchase.order`` record ID whose lines are requested.
        fields : list | None
            List of field names to return. If ``None``, Odoo returns all
            default fields.

        Returns
        -------
        list[dict]
            A list of ``purchase.order.line`` dictionaries.
        """
        return self.client.search_read(
            self.LINE_MODEL,
            domain=[("order_id", "=", order_id)],
            fields=fields
        )

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def create_order(
        self,
        partner_id: int,
        order_lines: list[dict]
    ) -> int:
        """
        Create a new purchase order (in draft state) with all its line items
        in a single XML-RPC call.

        The created order remains in draft (``"draft"`` state). Confirming
        the order is the responsibility of the caller or a future
        ``confirm_order`` method.

        Parameters
        ----------
        partner_id : int
            The Odoo ``res.partner`` ID of the vendor.
        order_lines : list[dict]
            A list of line-item dictionaries. Each dict must contain:

            - ``product_id``  (int)   — ``product.product`` record ID.
            - ``name``        (str)   — Description / product name.
            - ``product_qty`` (float) — Ordered quantity.
            - ``price_unit``  (float) — Unit price.
            - ``date_planned`` (str)  — Expected delivery date in ISO 8601
                                        format (``"YYYY-MM-DD"``).

        Returns
        -------
        int
            The database ID of the newly created ``purchase.order`` record.

        Notes
        -----
        Order lines are submitted using Odoo's standard ``(0, 0, values)``
        Command notation for one2many fields, which instructs Odoo to create
        each line record and link it to the header in one operation.
        """
        payload = {
            "partner_id": partner_id,
            "order_line": [
                (0, 0, line) for line in order_lines
            ],
        }
        return self.client.create(self.ORDER_MODEL, payload)

    def delete_order(self, order_id: int) -> bool:
        """
        Delete a purchase order by ID.

        Used exclusively for rollback when the import pipeline determines
        that a previously created PO must be removed due to a downstream
        error. The caller is responsible for deciding when rollback is
        appropriate.

        Parameters
        ----------
        order_id : int
            The ``purchase.order`` record ID to delete.

        Returns
        -------
        bool
            ``True`` if Odoo confirms the deletion.

        Notes
        -----
        In Odoo, a ``purchase.order`` in ``draft`` state can be deleted
        directly via ``unlink``. Confirmed orders (state ``"purchase"``)
        must be cancelled first. This method assumes the order is still in
        draft state, which is guaranteed when called immediately after a
        failed ``create_order``.
        """
        return self.client.unlink(self.ORDER_MODEL, [order_id])
