from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from excel.excel_processor import ExcelProcessor
from filesystem.import_manifest import ImportManifest
from filesystem.order_fingerprint import generate_fingerprint
from services.partner_service import AmbiguousVendorError, PartnerService
from services.product_service import (
    AmbiguousProductError,
    ProductNotFoundError,
    ColorNotFoundError,
    ProductService,
)
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
    order_name : str | None
        The native Odoo ``name`` (e.g., 'PO00045') of the created record.
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
    order_name: str | None = None
    duplicate_of: int | None = None
    errors: list[str] = field(default_factory=list)
    row_errors: list[str] = field(default_factory=list)
    ambiguities: list[dict] = field(default_factory=list)
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
        Used to resolve each row's Vendor Style Number + Color to a
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
        manifest: ImportManifest | None = None,
    ) -> None:
        self._partner_service = partner_service
        self._product_service = product_service
        self._po_service = po_service
        self._logger = logger if logger is not None else ImportLogger()
        self._manifest = manifest

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def import_file(self, file_path: str, user_mappings: dict = None) -> ImportResult:
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
        user_mappings : dict
            Optional dictionary mapping faulty vendor style numbers to exact Odoo products
            resolved by the user via the Ambiguity UI.

        Returns
        -------
        ImportResult
            A structured result the caller (GUI / main) can inspect or
            display without knowing the internals of this pipeline.
        """
        self._logger.info(f"Import started: {Path(file_path).name}")
        processor = ExcelProcessor(file_path)

        try:
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

            # --- Step 2a: Duplicate detection (fail-safe) ---
            # This check runs before any Odoo communication.
            # If fingerprint generation or manifest access fails for ANY reason,
            # the import is aborted — never silently bypassed.
            if self._manifest is not None:
                try:
                    fingerprint = generate_fingerprint(rows)
                except Exception as exc:
                    self._logger.error(
                        f"Import aborted. Duplicate protection error: "
                        f"could not generate order fingerprint: {exc}"
                    )
                    return ImportResult(
                        success=False,
                        file_path=file_path,
                        errors=[
                            "Import aborted: duplicate protection could not "
                            f"generate an order fingerprint ({exc}). "
                            "Please contact support."
                        ],
                    )

                try:
                    if self._manifest.is_imported(fingerprint):
                        entry = self._manifest.get_entry(fingerprint)
                        existing_po_id = entry.get("po_id") if entry else None
                        msg = (
                            f"Duplicate import rejected. This Purchase Order was "
                            f"already imported as PO #{existing_po_id}."
                            if existing_po_id
                            else "Duplicate import rejected. This Purchase Order "
                                "has already been imported."
                        )
                        self._logger.warning(msg)
                        return ImportResult(
                            success=False,
                            file_path=file_path,
                            duplicate_of=existing_po_id,
                            errors=[msg],
                        )
                except RuntimeError as exc:
                    # Manifest is corrupt or unreadable — abort, do not bypass.
                    self._logger.error(
                        f"Import aborted. {exc}"
                    )
                    return ImportResult(
                        success=False,
                        file_path=file_path,
                        errors=[str(exc)],
                    )

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
            
            # Extract x_country strictly from the Excel file payload mapped as a selection string
            x_country_value = rows[0].get("x_country")
            x_country_key = str(x_country_value).lower().strip() if x_country_value else None
            
            # Map Ship Via to Odoo's internal selection keys (e.g. "Boat / Air" -> "boat_air")
            raw_ship = rows[0].get("x_ship_via")
            ship_via_key = str(raw_ship).lower().replace(" / ", "_").strip() if raw_ship else None
            
            # Extract Payment Terms string from Excel and resolve it to Odoo ID dynamically
            raw_payment = rows[0].get("payment_term_id")
            payment_term_id = None
            if raw_payment:
                payment_term_id = self._po_service.find_payment_term_id(str(raw_payment).strip())
                if not payment_term_id:
                    self._logger.warning(
                        f"Warning: Payment term '{raw_payment}' not found in Odoo. "
                        "Falling back to Vendor's default payment term."
                    )
            
            # Fallback to Vendor's default Payment Terms if missing or mapping failed
            if not payment_term_id:
                payment_field = vendor.get("property_supplier_payment_term_id")
                payment_term_id = payment_field[0] if isinstance(payment_field, list) else None

            # --- Step 5: Build order lines (resolve each row — already validated in Step 4a) ---
            order_lines: list[dict] = []
            row_errors: list[str] = []
            ambiguities: list[dict] = []
            rows_processed = len(rows)
            rows_failed = 0

            for row in rows:
                row_num = row.get("_row", "?")
                vendor_code = str(row.get("x_vendor_code") or "").strip()
                color = str(row.get("attribute_value_ids") or "").strip()
                
                mapping_key = f"{vendor_code}::{color}" if color else vendor_code

                # 1. Check user mappings first to override lookup
                if user_mappings and mapping_key in user_mappings:
                    product = user_mappings[mapping_key]
                    order_lines.append(self._build_line(row, product))
                    continue

                # 2. Product lookup: Vendor Style Number + Color (never by name)
                try:
                    product = self._product_service.find_variant(vendor_code, color)
                except AmbiguousProductError as exc:
                    self._logger.warning(
                        f"Row {row_num}: Multiple EXACT matching products found. Triggering resolution UI."
                    )
                    ambiguities.append({
                        "row": row_num,
                        "original_code": vendor_code,
                        "color": color,
                        "mapping_key": mapping_key,
                        "candidates": exc.matches
                    })
                    row_errors.append(
                        f"Row {row_num}:\n"
                        "Multiple matching products were found in Odoo. Please map manually."
                    )
                    rows_failed += 1
                    continue
                except (ProductNotFoundError, ColorNotFoundError) as exc:
                    self._logger.warning(f"Row {row_num}: Exact match failed - Vendor: {vendor_code}, Color: {color}")
                    
                    candidates = self._product_service.search_similar_products(vendor_code, color)
                    if candidates:
                        ambiguities.append({
                            "row": row_num,
                            "original_code": vendor_code,
                            "color": color,
                            "mapping_key": mapping_key,
                            "candidates": candidates
                        })
                        row_errors.append(
                            f"Row {row_num}:\n"
                            f"Product not found exactly, but {len(candidates)} similar products exist."
                        )
                    else:
                        row_errors.append(
                            f"Row {row_num}:\n"
                            f"Product not found in Odoo database.\n"
                            f"Vendor Style Number: {vendor_code}   Color: {color}"
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
                    ambiguities=ambiguities,
                    rows_processed=rows_processed,
                    rows_failed=rows_failed,
                )
                self._log_summary(result, vendor_name=vendor_name)
                return result
            self._logger.info(f"{len(order_lines)} product(s) validated.")

            # --- Step 7: Create the Purchase Order ---
            try:
                order_id, order_name = self._po_service.create_order(
                    partner_id, 
                    order_lines,
                    x_country=x_country_key,
                    payment_term_id=payment_term_id,
                    date_order=rows[0].get("date_order"),
                    x_ship_via=ship_via_key,
                    x_sample_date=rows[0].get("x_sample_date"),
                )
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
            self._logger.info(f"Purchase Order {order_name} created successfully.")
            result = ImportResult(
                success=True,
                file_path=file_path,
                order_id=order_id,
                order_name=order_name,
                rows_processed=rows_processed,
                rows_failed=0,
            )
            self._log_summary(result, vendor_name=vendor_name)

            # --- Step 8a: Record fingerprint in manifest ---
            if self._manifest is not None:
                try:
                    self._manifest.record(
                        fingerprint=fingerprint,
                        po_id=order_id,
                        vendor=vendor_name,
                        filename=Path(file_path).name,
                    )
                except RuntimeError as exc:
                    # The PO was created successfully. Warn but do not mask the
                    # success — the operator can manually reconcile the manifest.
                    self._logger.warning(
                        f"PO #{order_id} was created but could not be recorded "
                        f"in the import manifest: {exc}. The file may be "
                        "importable again if the manifest is not repaired."
                    )

            return result

        finally:
            processor.close()

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
        po_line = result.order_name if result.order_name else (f"#{result.order_id}" if result.order_id else "None")
        
        self._logger.info(
            f"Import Summary | File: {Path(result.file_path).name} | "
            f"Vendor: {vendor_name} | Result: {outcome} | "
            f"Passed: {result.rows_processed} | Failed: {result.rows_failed} | "
            f"PO: {po_line}"
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
            Keys: ``product_id``, ``name``, ``x_color``, ``product_qty``,
            ``price_unit``, ``date_planned``, ``product_uom``.
        """
        line = {
            "product_id": product["id"],
            "name": str(row.get("x_vendor_code") or ""),
            "x_color": str(row.get("attribute_value_ids") or "").strip(),
            "product_qty": float(row.get("product_qty") or 0),
            "price_unit": float(row.get("price_unit") or 0),
            "date_planned": str(row.get("date_planned") or ""),
            "product_uom": product["uom_id"][0],
        }
        
        if row.get("x_size"):
            line["x_size"] = str(row.get("x_size")).strip()
            
        return line
