# Configuration for mapping Excel headers to internal field names
# Format: "Excel Column Name": "internal_field_name"
COLUMN_MAPPING = {
    "Vendor": "vendor",
    "Vendor Style Number": "x_vendor_code",
    "Vendor Code": "x_vendor_code",
    "Color": "attribute_value_ids",
    "Quantity": "product_qty",
    "Unit Price": "price_unit",
    "Due Date": "date_planned",
}

def map_row(row, mapping=COLUMN_MAPPING):
    """
    Converts a row dictionary from Excel format (Excel headers as keys)
    to internal format (mapped internal names as keys).

    Args:
        row (dict): The raw row data from ExcelReader.
        mapping (dict): The mapping dictionary.

    Returns:
        dict: A new dictionary with internal keys.
    """
    mapped_row = {}
    for excel_col, internal_field in mapping.items():
        # Map the value from the excel column to the internal field
        # Only assign if it actually exists in the row to avoid overwriting 
        # a successful alias match with a None from a missing alias.
        if excel_col in row:
            mapped_row[internal_field] = row[excel_col]

    return mapped_row
