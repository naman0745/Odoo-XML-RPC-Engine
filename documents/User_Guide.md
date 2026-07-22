# Purchase Order Importer: User Guide

Welcome to the Purchase Order Importer! This application automates extracting Purchase Orders (POs) from standardized Excel sheets directly into your Odoo ERP system.

## 1. First Launch
No complex setup is required. The moment you first open the application, it will transparently locate your `Documents/` directory and configure a master workspace named **`PO_workspace`**.

Inside that folder, it creates two essential destinations:
- **Incoming Orders:** (Place new files here).
- **Processed Orders:** (The system moves finished files here automatically).

## 2. The Dashboard & Incoming Orders
When you open the PO Importer, the main "Scan View" appears. The application scans the `Incoming Orders` folder natively and populates a queue of any available `.xlsx` files waiting beneath.

- **To Import:** Select the file from the list and hit "Ready to Import."
- **To View Files on PC:** Click the folder icon at the top right to physically open the destination on your Microsoft Windows machine.

## 3. The Import Workflow
Once you click **Start Import**, the system locks the UI structurally so you don't accidentally click it twice, and begins talking to the server natively in the background.

Depending on network speed, this takes about 3 seconds per file.

If everything processes cleanly, the system surfaces a **Success Screen**, illustrating:
- The actual resulting **Odoo Purchase Order ID** (e.g., `PO10034`).
- A message confirming if the file was relocated natively to your `Processed Orders` archive effectively.

## 4. Duplicate Detection (Idempotency)
You don't need to manually verify if you already uploaded an excel sheet to Odoo! 

The system writes an invisible "fingerprint" (using cryptographic file mapping) down into an internal log alongside every successful import. If you—or another employee using the same computer—attempts to upload the identical file twice, the PO Importer actively blocks the move, preventing duplicating charges against the ERP backend. And don't worry—if you change even one single cell in the Excel workbook, the system sees it as a brand new purchase sequence.

## 5. Common Errors & Troubleshooting

- **[CONNECTION_ERROR] "Connecting to Odoo"**
  - **Why:** The system is unable to authenticate.
  - **Solution:** Verify your internet connection is live. If the company server is down for maintenance, you must wait and restart the application completely once back online.

- **[IMPORT_ERROR] "Executing Import"**
  - **Why:** The spreadsheet has missing required cells (like a Vendor Code left blank), or non-existent items requested.
  - **Solution:** An explicit error string will populate in the app explaining the row breaking the system. Open the workbook, adjust the cell specifically outlined, save it, and just press retry on the application.

- **Warning: PO Created, but Workbook Could Not Be Moved!**
  - **Why:** This means the Purchase Order **successfully arrived in Odoo**, however, an antivirus hook or Microsoft Excel actively had the spreadsheet open while you used the app, preventing the application from dragging it to the `Processed Orders` archive natively.
  - **Solution:** Since the PO successfully transferred, manually close Excel and drag the file over to `Processed Orders` yourself via File Explorer. Ensure you do not process it again!
