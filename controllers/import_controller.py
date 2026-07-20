from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from excel.excel_processor import ExcelProcessor
from services.partner_service import AmbiguousVendorError, PartnerService
from services.product_service import AmbiguousProductError, ProductService
from services.purchase_order_service import PurchaseOrderService
from utils.logger import ImportLogger


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class ImportResult:
    """
    Structured outcome of a single ``import_file()`` call.

    Attributes
    ----------
    success : bool
        ``True`` only if the PO was created in Odoo without any errors.
    file_path : str
        The path of the Excel file that was processed.
    order_id : int | None
        The Odoo ``purchase.order`` ID of the created record, or ``None``
        if the import did not reach the creation step.
    errors : list[str]
        Fatal errors that prevented the import from completing
        (e.g. file not found, vendor not found, Odoo connection error).
    row_errors : list[str]
        Per-row errors (e.g. product not found, blank required field).
        Each entry is prefixed with the Excel row number for traceability.
    rows_processed : int
        Total number of data rows that were attempted.
    rows_failed : int
        Number of data rows that produced an error and were skipped.
    """

    success: bool
    file_path: str
    order_id: int | None = None
    errors: list[str] = field(default_factory=list)
    row_errors: list[str] = field(default_factory=list)
    rows_processed: int = 0
    rows_failed: int = 0


# ---------------------------------------------------------------------------
# Controller
# ---------------------------------------------------------------------------

class ImportController:
    """
    Orchestrates the complete Purchase Order import workflow.

    Responsibility
    --------------
    Coordinate the pipeline from a validated Excel file to a draft
    ``purchase.order`` record in Odoo. This class:

    - Delegates all Excel I/O to ``ExcelProcessor``.
    - Delegates all Odoo communication to the injected service instances.
    - Writes workflow-level log entries.
    - Makes the business decisions: which rows to accept, when to abort,
      when to rollback.

    This controller does NOT:

    - Parse Excel itself.
    - Perform XML-RPC calls directly.
    - Display any UI output.
    - Move or delete files.

    Constructor dependencies
    ------------------------
    All three services must share the same connected ``OdooClient`` instance,
    and ``OdooClient.connect()`` must have been called before any import.

    Parameters
    ----------
    partner_service : PartnerService
        Used to resolve the vendor name to an Odoo ``res.partner`` ID.
    product_service : ProductService
        Used to resolve each row's Vendor Code + Color to a
        ``product.product`` ID.
    po_service : PurchaseOrderService
        Used to create (and if necessary delete) the ``purchase.order``.
    """

    def __init__(
        self,
        partner_service: PartnerService,
        product_service: ProductService,
        po_service: PurchaseOrderService,
        logger: ImportLogger | None = None,
    ) -> None:
        self._partner_service = partner_service
        self._product_service = product_service
        self._po_service = po_service
        self._logger = logger if logger is not None else ImportLogger()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def import_file(self, file_path: str) -> ImportResult:
        """
        Run the full import pipeline for a single Excel workbook.

        One Excel file represents exactly one Purchase Order.
        The vendor name is read from the first data row and is expected
        to be consistent across all subsequent rows.

        Workflow
        --------
        1. Validate the Excel file structure.
        2. Read and map all data rows.
        3. Resolve the vendor via ``PartnerService``.
        4. For each row: validate required fields and resolve product variant.
        5. If any row fails: abort — do not create a partial PO.
        6. If all rows are valid: call ``PurchaseOrderService.create_order()``.
        7. Return an ``ImportResult`` describing the outcome.

        Parameters
        ----------
        file_path : str
            Path to the ``.xlsx`` workbook to import.

        Returns
        -------
        ImportResult
            A structured result the caller (GUI / main) can inspect or
            display without knowing the internals of this pipeline.
        """
        self._logger.info(f"Import started: {Path(file_path).name}")
        processor = ExcelProcessor(file_path)

        # --- Step 1: File-level validation ---
        ok, errors = processor.validate_file()
        if not ok:
            for error in errors:
                self._logger.error(f"Import failed. Reason: {error}")
            result = ImportResult(
                success=False,
                file_path=file_path,
                errors=errors,
            )
            self._log_summary(result)
            return result
        self._logger.info("Reading Excel file.")

        # --- Step 2: Read + map rows ---
        rows = processor.get_mapped_rows()
        self._logger.info(f"{len(rows)} data row(s) read from workbook.")
        if not rows:
            self._logger.error(
                "Import failed. Reason: The workbook contains no data rows."
            )
            result = ImportResult(
                success=False,
                file_path=file_path,
                errors=["The workbook contains no data rows."],
            )
            self._log_summary(result)
            return result

        # --- Step 3: Validate PO header (once, from first row) ---
        header_row = rows[0]
        ok, msg = processor.validate_header(header_row)
        if not ok:
            self._logger.error(f"Import failed. Reason: {msg}")
            result = ImportResult(
                success=False,
                file_path=file_path,
                errors=[f"PO header row is invalid: {msg}"],
            )
            self._log_summary(result)
            return result

        # --- Step 4a: Validate all rows before any Odoo lookup ---
        pre_lookup_row_errors: list[str] = []
        pre_lookup_rows_failed = 0
        for row in rows:
            row_num = row.get("_row", "?")
            ok, msg = processor.validate_row(row)
            if not ok:
                row_error = f"Row {row_num}: {msg}"
                self._logger.warning(row_error)
                pre_lookup_row_errors.append(row_error)
                pre_lookup_rows_failed += 1

        if pre_lookup_row_errors:
            self._logger.error(
                f"Import aborted. {pre_lookup_rows_failed} row(s) failed. "
                "No PO was created."
            )
            vendor_name_early = self._extract_vendor_name(rows)
            result = ImportResult(
                success=False,
                file_path=file_path,
                errors=[
                    f"Import aborted - {pre_lookup_rows_failed} row(s) had "
                    "errors. No Purchase Order was created."
                ],
                row_errors=pre_lookup_row_errors,
                rows_processed=len(rows),
                rows_failed=pre_lookup_rows_failed,
            )
            self._log_summary(result, vendor_name=vendor_name_early)
            return result

        # --- Step 4b: Resolve vendor ---
        vendor_name = self._extract_vendor_name(rows)
        try:
            vendor = self._partner_service.get_vendor(vendor_name)
        except AmbiguousVendorError as exc:
            self._logger.error(
                "Import failed. Multiple vendors matched. "
                f"Technical details: {exc}"
            )
            return ImportResult(
                success=False,
                file_path=file_path,
                errors=[
                    f"Multiple vendors matched \"{vendor_name}\". "
                    "Please make the vendor name more specific."
                ],
            )
        except Exception as exc:
            self._logger.error(
                "Import failed. Unable to look up vendor in Odoo. "
                f"Technical details: {exc}"
            )
            return ImportResult(
                success=False,
                file_path=file_path,
                errors=[
                    "Unable to look up the vendor in Odoo. "
                    "Please try again or contact support."
                ],
            )
        if vendor is None:
            self._logger.error(
                f"Import failed. Reason: Vendor \"{vendor_name}\" "
                "was not found in Odoo."
            )
            return ImportResult(
                success=False,
                file_path=file_path,
                errors=[f"Vendor \"{vendor_name}\" was not found in Odoo."],
            )
        self._logger.info(f"Vendor found: {vendor_name}.")
        partner_id: int = vendor["id"]

        # --- Step 5: Build order lines (resolve each row — already validated in Step 4a) ---
        order_lines: list[dict] = []
        row_errors: list[str] = []
        rows_processed = len(rows)
        rows_failed = 0

        for row in rows:
            row_num = row.get("_row", "?")


            # Product lookup: Vendor Code + Color (never by name)
            try:
                product = self._product_service.find_variant(
                    vendor_code=str(row.get("x_vendor_code") or "").strip(),
                    Color=str(row.get("attribute_value_ids") or "").strip(),
                )
            except AmbiguousProductError as exc:
                vendor_code = row.get("x_vendor_code")
                color = row.get("attribute_value_ids")
                self._logger.warning(
                    f"Row {row_num}: Multiple matching products found. "
                    f"Technical details: {exc}"
                )
                row_errors.append(
                    f"Row {row_num}:\n"
                    "Multiple matching products were found.\n"
                    f"Vendor Code: {vendor_code}\n"
                    f"Color: {color}"
                )
                rows_failed += 1
                continue
            except Exception as exc:
                self._logger.error(
                    f"Row {row_num}: Unable to look up product in Odoo. "
                    f"Technical details: {exc}"
                )
                row_errors.append(
                    f"Row {row_num}:\n"
                    "Unable to look up the product in Odoo."
                )
                rows_failed += 1
                continue
           
            if product is None:
                vendor_code = row.get("x_vendor_code")
                color = row.get("attribute_value_ids")
                self._logger.warning(
                    f"Row {row_num}: No matching product found - "
                    f"Vendor Code: {vendor_code}, Color: {color}"
                )
                row_errors.append(
                    f"Row {row_num}:\n"
                    "No matching product was found.\n"
                    f"Vendor Code: {vendor_code}\n"
                    f"Color: {color}"
                )
                rows_failed += 1
                continue

            order_lines.append(self._build_line(row, product))

        # --- Step 6: Abort if any row failed (never create partial POs) ---
        if row_errors:
            result = ImportResult(
                success=False,
                file_path=file_path,
                errors=[
                    f"Import aborted - {rows_failed} row(s) had errors. "
                    "No Purchase Order was created."
                ],
                row_errors=row_errors,
                rows_processed=rows_processed,
                rows_failed=rows_failed,
            )
            self._log_summary(result, vendor_name=vendor_name)
            return result
        self._logger.info(f"{len(order_lines)} product(s) validated.")

        # --- Step 7: Create the Purchase Order ---
        try:
            order_id = self._po_service.create_order(partner_id, order_lines)
        except Exception as exc:
            self._logger.error(
                "Import failed. Unable to create the Purchase Order. "
                f"Technical details: {exc}"
            )
            result = ImportResult(
                success=False,
                file_path=file_path,
                errors=[
                    "Unable to create the Purchase Order because required "
                    "information is missing or an Odoo error occurred."
                ],
                rows_processed=rows_processed,
                rows_failed=0,
            )
            self._log_summary(result, vendor_name=vendor_name)
            return result

        # --- Step 8: Success ---
        self._logger.info(f"Purchase Order #{order_id} created successfully.")
        result = ImportResult(
            success=True,
            file_path=file_path,
            order_id=order_id,
            rows_processed=rows_processed,
            rows_failed=0,
        )
        self._log_summary(result, vendor_name=vendor_name)
        return result

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _log_summary(
        self,
        result: ImportResult,
        vendor_name: str = "(not resolved)",
    ) -> None:
        """
        Log a consistent import summary block for every outcome.

        Parameters
        ----------
        result : ImportResult
            The completed import result.
        vendor_name : str
            The vendor name as read from the workbook (used even on failure).
        """
        outcome = "Success" if result.success else "Failed"
        po_line = (
            f"Purchase Order ID : #{result.order_id}"
            if result.order_id
            else "Purchase Order    : Not created"
        )
        self._logger.info(
            "\n--- Import Summary ---"
            f"\nFile              : {Path(result.file_path).name}"
            f"\nVendor            : {vendor_name}"
            f"\nRows processed    : {result.rows_processed}"
            f"\nRows failed       : {result.rows_failed}"
            f"\nResult            : {outcome}"
            f"\n{po_line}"
            "\n----------------------"
        )

    def _extract_vendor_name(self, rows: list[dict]) -> str:
        """
        Read the vendor name from the first data row.

        Since one file equals one PO, the vendor is assumed to be the same
        across all rows. The first row is used as the authoritative source.

        Parameters
        ----------
        rows : list[dict]
            Mapped row dicts as returned by ``ExcelProcessor.get_mapped_rows()``.

        Returns
        -------
        str
            The vendor name string, stripped of leading/trailing whitespace.
        """
        return str(rows[0].get("vendor") or "").strip()

    def _build_line(self, row: dict, product: dict) -> dict:
        """
        Convert a single mapped row into an Odoo PO line dict.

        The returned dict uses Odoo field names as required by
        ``PurchaseOrderService.create_order()``.

        Parameters
        ----------
        row : dict
            A validated, mapped row from ``ExcelProcessor.get_mapped_rows()``.
        product : dict
            The ``product.product`` record returned by ``find_variant()``.
            Must contain ``id`` and ``uom_id`` keys.

        Returns
        -------
        dict
            Keys: ``product_id``, ``name``, ``product_qty``,
            ``price_unit``, ``date_planned``, ``product_uom``.
        """
        return {
            "product_id": product["id"],
            "name": str(row.get("x_vendor_code") or ""),
            "product_qty": float(row.get("product_qty") or 0),
            "price_unit": float(row.get("price_unit") or 0),
            "date_planned": str(row.get("date_planned") or ""),
            "product_uom": product["uom_id"][0],
        }
