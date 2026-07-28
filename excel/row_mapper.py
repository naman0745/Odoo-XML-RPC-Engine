# Configuration for mapping Excel headers to internal field names.
# Format: "Excel Column Name": "internal_field_name"
COLUMN_MAPPING = {
    "Order Date":              "date_order",
    "Vendor":                  "vendor",
    "Country":                 "x_country",
    "Payment Terms":           "payment_term_id",
    "Ship Via":                "x_ship_via",
    "TOP Sample Date":         "x_sample_date",    # optional column
    "Due Date":                "date_planned",
    "Vendor Code":             "x_vendor_code",
    "Vendor Style Number":     "x_vendor_code",    # alias — same internal field
    "Color":                   "attribute_value_ids",
    "Size":                    "x_size",            # optional column
    "Quantity":                "product_qty",
    "Unit Price":              "price_unit",
    "Product Unit of Measure": "product_uom",
}

# Internal field names whose source columns are optional.  When the column is
# absent from the workbook the mapper will still emit the key with None so
# that downstream code can safely call row.get("x_sample_date") etc. without
# a KeyError.
OPTIONAL_INTERNAL_FIELDS: set[str] = {
    "x_sample_date",   # TOP Sample Date
    "x_size",          # Size
}


def map_row(row: dict, mapping: dict = COLUMN_MAPPING) -> dict:
    """
    Converts a raw Excel row dict (header → cell value) to an internal dict
    (internal field name → value).

    Mandatory columns that are present in *mapping* but absent from *row* are
    simply omitted (the validator will catch the gap).  Optional columns that
    are absent from *row* are always emitted as ``None`` so callers can safely
    access them without a ``KeyError``.

    The alias rule (Vendor Code / Vendor Style Number → x_vendor_code) is
    handled correctly: the first alias found wins and the second is skipped to
    avoid overwriting a good value with ``None``.

    Args:
        row:     Raw row dict produced by ``ExcelReader.get_rows()``.
        mapping: Column-to-field mapping (defaults to ``COLUMN_MAPPING``).

    Returns:
        dict with internal keys ready for validation and Odoo upload.
    """
    mapped_row: dict = {}

    for excel_col, internal_field in mapping.items():
        if excel_col in row:
            # Only overwrite if the internal field has not been set yet
            # (handles the Vendor Code / Vendor Style Number alias pair).
            if internal_field not in mapped_row:
                mapped_row[internal_field] = row[excel_col]
        else:
            # Column absent from workbook: emit None for optional fields so
            # callers never raise KeyError; skip for mandatory fields (the
            # validator will flag the missing column).
            if internal_field in OPTIONAL_INTERNAL_FIELDS:
                mapped_row.setdefault(internal_field, None)

    return mapped_row
