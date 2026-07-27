from excel.excel_reader import ExcelReader
from excel.validators import ExcelValidator
from excel.row_mapper import map_row, COLUMN_MAPPING


# Columns that must exist in the workbook header row.
REQUIRED_COLUMNS: list[str] = [
    "Vendor",
    "Vendor Style Number",
    "Color",
    "Quantity",
    "Unit Price",
    "Due Date",
]

# Internal field names that must be present in the PO header row (row 2).
# These are validated once per file, not per line.
HEADER_REQUIRED_FIELDS: list[str] = [
    "vendor",
]

# Internal field names that must not be empty on every individual order line.
LINE_REQUIRED_FIELDS: list[str] = [
    "x_vendor_code",
    "attribute_value_ids",
    "product_qty",
    "price_unit",
    "date_planned",
]


class ExcelProcessor:
    """
    Encapsulates all Excel I/O: reading, validation, and row mapping.

    Responsibility
    --------------
    Hide ``ExcelReader``, ``ExcelValidator``, and ``map_row`` from the
    ``ImportController``. The controller receives clean, validated,
    mapped Python dicts and never touches Excel internals.

    This class does not communicate with Odoo and has no knowledge of
    business rules beyond the structural requirements of the workbook.

    Usage
    -----
    processor = ExcelProcessor(file_path)
    ok, errors = processor.validate_file()
    if ok:
        rows = processor.get_mapped_rows()
        for row in rows:
            ok, msg = processor.validate_row(row)
    """

    def __init__(self, file_path: str) -> None:
        """
        Parameters
        ----------
        file_path : str
            Absolute or relative path to the ``.xlsx`` workbook to process.
        """
        self.file_path = file_path
        self._validator = ExcelValidator(file_path)
        # ExcelReader opens the workbook on construction; defer until needed.
        self._reader: ExcelReader | None = None

    # ------------------------------------------------------------------
    # File-level validation
    # ------------------------------------------------------------------

    def validate_file(self) -> tuple[bool, list[str]]:
        """
        Run all structural validations on the workbook.

        Checks are run in dependency order — if the file does not exist,
        subsequent checks are skipped and a single error is returned.

        Returns
        -------
        tuple[bool, list[str]]
            ``(True, [])`` if all checks pass.
            ``(False, [error, ...])`` listing every problem found.
        """
        # --- File must exist before we can open it at all ---
        ok, msg = self._validator.validate_file_exists()
        if not ok:
            return False, [msg]

        ok, msg = self._validator.validate_worksheet_exists()
        if not ok:
            return False, [msg]

        ok, msg = self._validator.validate_not_empty()
        if not ok:
            return False, [msg]

        # --- Header-level checks ---
        errors: list[str] = []
        headers = self._get_reader().get_headers()

        ok, msg = self._validator.validate_no_duplicate_headers(headers)
        if not ok:
            errors.append(msg)

        has_vendor_code = "Vendor Code" in headers
        has_vendor_style = "Vendor Style Number" in headers
        
        if not (has_vendor_code or has_vendor_style):
            errors.append("Missing required columns: Vendor Code or Vendor Style Number")

        other_required = [col for col in REQUIRED_COLUMNS if col != "Vendor Style Number"]
        ok, msg = self._validator.validate_required_columns(
            headers, other_required
        )
        if not ok:
            errors.append(msg)

        return len(errors) == 0, errors

    # ------------------------------------------------------------------
    # Row retrieval
    # ------------------------------------------------------------------

    def get_mapped_rows(self) -> list[dict]:
        """
        Read all non-blank data rows and convert them to internal field names.

        Each returned dict uses the internal keys defined in ``COLUMN_MAPPING``
        (e.g. ``"vendor"``, ``"vendor_code"``, ``"color"``), plus
        ``"_row"`` (the 1-based Excel row number for error reporting).

        Returns
        -------
        list[dict]
            Mapped rows ready for the controller to process.
        """
        raw_rows = self._get_reader().get_rows()
        mapped = []
        for raw in raw_rows:
            mapped_row = map_row(raw, COLUMN_MAPPING)
            # Preserve the original row number for error messages.
            mapped_row["_row"] = raw.get("_row")
            mapped.append(mapped_row)
        return mapped

    # ------------------------------------------------------------------
    # Header-row validation
    # ------------------------------------------------------------------

    def validate_header(self, header_row: dict) -> tuple[bool, str]:
        """
        Check that all PO-level required fields are present in the header row.

        The header row (row 2 in the workbook) contains PO-level data such as
        the vendor name that applies to the whole file.  This must be called
        once before iterating over order lines.

        Parameters
        ----------
        header_row : dict
            The first mapped data row (index 0 of ``get_mapped_rows()``).

        Returns
        -------
        tuple[bool, str]
            ``(True, "...")`` if valid, ``(False, "...")`` with a description
            of the missing fields otherwise.
        """
        return self._validator.validate_no_empty_required_cells(
            header_row, HEADER_REQUIRED_FIELDS
        )

    # ------------------------------------------------------------------
    # Per-row (order line) validation
    # ------------------------------------------------------------------

    def validate_row(self, row: dict) -> tuple[bool, str]:
        """
        Check that all required *line-level* fields in a mapped row are
        non-empty.  Header-level fields (e.g. ``vendor``) are deliberately
        excluded here — they are validated once via ``validate_header()``.

        Parameters
        ----------
        row : dict
            A mapped row dict as returned by ``get_mapped_rows()``.

        Returns
        -------
        tuple[bool, str]
            ``(True, "...")`` if valid, ``(False, "...")`` with a description
            of the missing fields otherwise.
        """
        ok, msg = self._validator.validate_no_empty_required_cells(
            row, LINE_REQUIRED_FIELDS
        )
        if not ok:
            return ok, msg

        ok, msg = self._validator.validate_positive_number(
            row, "product_qty", "Quantity"
        )
        if not ok:
            return ok, msg

        ok, msg = self._validator.validate_non_negative_number(
            row, "price_unit", "Unit Price"
        )
        if not ok:
            return ok, msg

        return self._validator.validate_and_normalize_date(
            row, "date_planned", "Due Date"
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_reader(self) -> ExcelReader:
        """Lazy-initialise ``ExcelReader`` (opens the workbook once)."""
        if self._reader is None:
            self._reader = ExcelReader(self.file_path)
        return self._reader

    def close(self) -> None:
        """Close the underlying ExcelReader to release file locks."""
        if self._reader is not None:
            self._reader.close()
