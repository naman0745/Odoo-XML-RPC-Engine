# 📦 Purchase Order Importer v3.0

A desktop-native utility designed to automate the high-throughput migration of Excel Purchase Orders into Odoo ERP via XML-RPC. Built for speed and reliability, this tool removes manual friction from purchasing workflows.

## ⚡ The Workflow
This application is designed as a **conveyer belt** for Purchase Orders:
1. **Drop:** Place `.xlsx` purchase orders into the application's workspace directory.
2. **Process:** The app automatically validates the Excel layout, checks for duplications, and pushes the data to Odoo. 
3. **Finish:** Successfully imported files are automatically organized into completed directories. Failed files remain in place for correction.

## ⚙️ Quick Start Guide

### 1. Installation
The system is built entirely on standard Python 3 paradigms.
```bash
git clone https://github.com/naman0745/Odoo-XML-RPC-Engine.git
cd Odoo-XML-RPC-Engine
pip install -r requirements.txt
```

### 2. Configuration
Before running any module, configure the authentication backend by creating a `.env` file in the root project directory:
```env
ODOO_URL=http://your-odoo-instance.com
ODOO_DB=your_database_name
```

### 3. Execution
To launch the primary desktop GUI:
```bash
python -m gui.app
```
*(Once launched, simply click on "Change Folder" to select your desired workspace directory and start importing).*
