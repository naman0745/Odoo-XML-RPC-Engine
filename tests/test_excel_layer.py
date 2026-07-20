import os
import openpyxl
from excel.excel_reader import ExcelReader
from excel.validators import ExcelValidator
from excel.row_mapper import map_row, COLUMN_MAPPING

def create_test_excel(file_path, data):
    """Helper to create an excel file for testing."""
    wb = openpyxl.Workbook()
    sheet = wb.active

    for r_idx, row in enumerate(data, 1):
        for c_idx, value in enumerate(row, 1):
            sheet.cell(row=r_idx, column=c_idx, value=value)

    wb.save(file_path)

def test_excel_reader():
    print("\n--- Testing ExcelReader ---")
    file_path = "test_reader.xlsx"
    data = [
        ["Vendor Name", "Item No", "Qty"],
        ["Vendor A", "SKU1", 10],
        [None, None, None], # Empty row
        ["Vendor B", "SKU2", 20],
    ]
    create_test_excel(file_path, data)

    try:
        reader = ExcelReader(file_path)
        headers = reader.get_headers()
        print(f"Headers: {headers}")
        assert headers == ["Vendor Name", "Item No", "Qty"]

        rows = reader.get_rows()
        print(f"Rows read: {len(rows)}")
        assert len(rows) == 2
        assert rows[0]["Vendor Name"] == "Vendor A"
        assert rows[1]["Vendor Name"] == "Vendor B"
        print("ExcelReader tests passed!")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

def test_excel_validator():
    print("\n--- Testing ExcelValidator ---")

    # Test file exists
    validator = ExcelValidator("non_existent.xlsx")
    exists, msg = validator.validate_file_exists()
    print(f"File exists test: {exists} - {msg}")
    assert not exists

    # Test duplicate headers and required columns
    file_path = "test_validator.xlsx"
    data = [
        ["Vendor Name", "Vendor Name", "Qty"], # Duplicate
        ["Vendor A", "Vendor A", 10],
    ]
    create_test_excel(file_path, data)

    try:
        validator = ExcelValidator(file_path)
        headers = ["Vendor Name", "Vendor Name", "Qty"]

        # Duplicate check
        ok, msg = validator.validate_no_duplicate_headers(headers)
        print(f"Duplicate headers test: {ok} - {msg}")
        assert not ok

        # Required columns check
        required = ["Vendor Name", "Item No"]
        ok, msg = validator.validate_required_columns(headers, required)
        print(f"Required columns test: {ok} - {msg}")
        assert not ok

        # Empty required cells
        row = {"Vendor Name": None, "Item No": "SKU1"}
        ok, msg = validator.validate_no_empty_required_cells(row, ["Vendor Name"])
        print(f"Empty required cell test: {ok} - {msg}")
        assert not ok

        print("ExcelValidator tests passed!")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

def test_row_mapper():
    print("\n--- Testing RowMapper ---")
    row = {
        "Vendor Name": "ACME Corp",
        "Item No": "12345",
        "Qty": 5,
        "Unit Price": 10.0,
        "Extra Col": "Ignore Me"
    }

    mapped = map_row(row)
    print(f"Mapped row: {mapped}")

    assert mapped["vendor"] == "ACME Corp"
    assert mapped["sku"] == "12345"
    assert mapped["quantity"] == 5
    assert mapped["price"] == 10.0
    assert "Extra Col" not in mapped

    # Test missing column
    row_missing = {"Vendor Name": "ACME Corp"}
    mapped_missing = map_row(row_missing)
    assert mapped_missing["sku"] is None

    print("RowMapper tests passed!")

if __name__ == "__main__":
    try:
        test_excel_reader()
        test_excel_validator()
        test_row_mapper()
        print("\nALL EXCEL LAYER TESTS PASSED SUCCESSFULLY!")
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
    except Exception as e:
        print(f"\nAN UNEXPECTED ERROR OCCURRED: {e}")
