# 📦 Purchase Order Importer v3.0

An internal, desktop-native utility designed to automate the high-throughput migration of Excel Purchase Orders into Odoo ERP via XML-RPC. Built for speed and reliability, this tool removes manual friction from purchasing workflows.

---

## ⚡ The Workflow
This application is designed as a **conveyer belt** for Purchase Orders:
1. **Drop:** Place `.xlsx` purchase orders into your designated `Incoming Orders` folder.
2. **Process:** The app automatically validates the Excel layout, checks for duplications, and pushes the data to Odoo. 
3. **Finish:** Successfully imported files are automatically moved to the `Processed Orders` folder. Failed files remain in place for correction.

---

## ✨ Key Features

### 🚀 High-Throughput User Experience
- **Workflow Accelerator (Conveyer Belt):** Automatically queues the next pending file sequentially without requiring you to return to the main menu.
- **Power User Navigation:** Full-keyboard traversal (`Enter` / `Esc`) bypasses the need for manual mouse targeting.
- **In-App Error Recovery:** Seamlessly launch Windows Excel directly from failure screens to immediately correct faulty rows.

### 🛡️IronClad Architecture
- **Idempotency & Duplicate Protection:** Uses cryptographically secure content hashes and manifests to implicitly reject duplicate files, even if the filename is changed.
- **Sequential Error Resolution:** Accurately distinguishes between structural errors (invalid product vendor-code) and variation errors (missing color strings) to tell users exactly what to fix.
- **Background Threading:** The GUI remains completely responsive with visual progress indicators, never locking up during heavy remote network writes.
- **Fail-Safe Integrity:** Rigid `try...finally` resource handlers guarantee that your filesystem natively cleans up temporary memory locks to resolve OS permission crashes.

---

## 📁 Folder Structure
```text
PO_import/
├── config/             # Environment, credentials, and app version truth
├── connection/         # Raw Odoo XML-RPC gateway
├── controllers/        # Application orchestrators (Business Logic)
├── documents/          # Standardized project manuals and test files
├── excel/              # Excel mapping, openpyxl readers, and data extraction
├── filesystem/         # File locators, fingerprinting, and OS-level movement
├── gui/                # Native Tkinter views and UX protocols
├── services/           # Granular Odoo model handlers (Partner, Product, PO)
├── tests/              # Pytest battery asserting reliability mechanics
└── utils/              # System-wide loggers
```

---

## ⚙️ Quick Start Guide

### 1. Installation
The system is built entirely on standard Python 3 paradigms.
```bash
git clone <repository_url>
cd PO_import
pip install -r requirements.txt
```
*(Note: If a pre-packaged binary has been given to you, extraction isn't needed. Double-click `PurchaseOrderImporter.exe` to run natively).*

### 2. Configuration
Before running any module, configure the authentication backend inside `config/settings.py`:
```python
ODOO_URL = "http://your-odoo-instance.com"
ODOO_DB = "your_database_name"
ODOO_USERNAME = "admin"
ODOO_PASSWORD = "secret_password"
```

### 3. Execution
To run the primary desktop GUI:
```bash
python -m gui.app
```

To bypass the GUI for headless batch execution:
```bash
python main.py path/to/target/purchase_order.xlsx
```

---

## 🛠️ Building the Executable
This project includes a fully defined `build.spec` for `PyInstaller` to compile the system into a `.exe` dependency-free executable for Windows:
```bash
pip install pyinstaller
pyinstaller build.spec
```
The final binary will appear in the `./dist/` directory.

---

## ⚠️ Troubleshooting & Known Limitations
- **Timeout Limitations:** Heavy internet degradation mid-import may cause XML-RPC commands to permanently timeout without triggering a graceful disconnect. The GUI may present as permanently importing. Restart the app.
- **Mapped Columns Only:** The `RowMapper` only extracts specific columns (Vendor Code, Quantity, Unit Price). Ad-hoc columns pushed by purchasing won't appear on the Odoo end.
- **Blank Workbooks:** Attempting to scan purely blank files will crash with an assertion loop rather than a graceful UI error. Ensure templates have header definitions.
