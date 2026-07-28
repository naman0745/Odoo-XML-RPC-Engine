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

    def find_payment_term_id(self, term_name: str) -> int | None:
        """
        Look up a payment term strictly by its exact display name dynamically.
        """
        records = self.client.search_read(
            "account.payment.term",
            domain=[("name", "=ilike", term_name)],
            fields=["id"],
            limit=1
        )
        return records[0]["id"] if records else None

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def create_order(
        self,
        partner_id: int,
        order_lines: list[dict],
        x_country: str | None = None,
        payment_term_id: int | None = None,
        date_order: str | None = None,
        x_ship_via: str | None = None,
        x_sample_date: str | None = None,
    ) -> tuple[int, str]:
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
        country_id : int, optional
            The Country ID for the PO (mapped to a custom or inherited field).
        payment_term_id : int, optional
            The Payment Terms ID for the PO.

        Returns
        -------
        tuple[int, str]
            The database ID and standard PO UI Name of the newly created ``purchase.order`` record.

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
        if x_country:
            payload["x_country"] = x_country  # String selection mapped from Excel directly!
        if payment_term_id:
            payload["payment_term_id"] = payment_term_id
        if date_order:
            payload["date_order"] = date_order
        if x_ship_via:
            payload["x_ship_via"] = x_ship_via
        if x_sample_date:
            payload["x_sample_date"] = x_sample_date
        order_id = self.client.create(self.ORDER_MODEL, payload)
        # Fetch the human-readable PO Name formatted directly from the server
        po_record = self.client.search_read(
            self.ORDER_MODEL,
            domain=[("id", "=", order_id)],
            fields=["name"],
            limit=1
        )
        order_name = po_record[0]["name"] if po_record else f"PO-{order_id}"
        return order_id, order_name

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
