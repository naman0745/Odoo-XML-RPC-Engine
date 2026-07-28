# 📦 Purchase Order Importer

A desktop-native utility that automates the migration of Excel Purchase Orders into Odoo ERP via XML-RPC. Built for speed and reliability, it removes manual friction from purchasing workflows.

## ⚡ The Workflow

This application is a **conveyor belt** for Purchase Orders:
1. **Drop** — Place `.xlsx` purchase orders into the app's incoming workspace folder.
2. **Process** — The app validates the Excel layout, checks for duplicates, and pushes the data to Odoo.
3. **Finish** — Successfully imported files are moved to a completed folder. Failed files stay in place for correction.

## ⚙️ Quick Start

### 1. Install
```bash
git clone https://github.com/naman0745/Odoo-XML-RPC-Engine.git
cd Odoo-XML-RPC-Engine
pip install -r requirements.txt
```

### 2. Run
```bash
python -m gui.app
```

On first launch, enter your Odoo server URL, database name, username, and password in the login screen. Credentials are saved securely in the OS keychain — you won't need to enter them again.

### 3. Import
Select one or more `.xlsx` files from the scan view and click **Process**. The app handles validation, duplicate detection, and Odoo PO creation automatically.

## 🏗️ Building Executables

Standalone executables for Windows, macOS, and Linux are built automatically on every push to `main`. Download the zip files from the releases page.

To build locally:
```bash
pyinstaller --noconfirm --windowed --clean --onefile \
  --name "PurchaseOrderImporter" \
  --hidden-import keyring.backends.Windows \
  --hidden-import keyring.backends.macOS \
  --hidden-import keyring.backends.SecretService \
  gui/app.py
```

## 🗂️ Project Structure

```
├── gui/            # Tkinter UI — views, widgets, controller
├── controllers/    # Import pipeline orchestration
├── services/       # Odoo domain services (partner, product, PO)
├── excel/          # Excel parsing, validation, row mapping
├── filesystem/     # Workspace, file management, duplicate detection
├── connection/     # Odoo XML-RPC authentication client
├── config/         # App configuration and versioning
└── utils/          # Logger, OS utilities
```

## 📋 Requirements

- Python 3.12+
- Odoo instance accessible over HTTP/HTTPS with XML-RPC enabled
- Excel files in `.xlsx` format
