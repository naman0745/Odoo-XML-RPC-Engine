import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Determine the directory where the executable (or script) is located
if getattr(sys, 'frozen', False):
    # Running as a PyInstaller bundle
    app_path = Path(sys.executable).parent
    # If it's a macOS .app bundle, the executable is inside Contents/MacOS/
    if sys.platform == 'darwin' and app_path.name == 'MacOS':
        base_dir = app_path.parent.parent.parent
    else:
        base_dir = app_path
else:
    # Running in an unfrozen development environment (e.g. python gui/app.py)
    base_dir = Path(__file__).parent.parent

# Load the .env file explicitly from the base directory
env_path = base_dir / '.env'
load_dotenv(dotenv_path=env_path)

ODOO_URL = os.getenv("ODOO_URL")
ODOO_DB = os.getenv("ODOO_DB")

ODOO_USERNAME = os.getenv("ODOO_USERNAME")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")