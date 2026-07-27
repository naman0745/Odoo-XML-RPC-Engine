"""
config/app_config.py
Manages the application's persistent settings via an external JSON file.
"""
import json
import os
from pathlib import Path

class AppConfig:
    def __init__(self):
        self.master_dir = Path.home() / "Documents" / "PurchaseOrder_Importer"
        self.config_path = self.master_dir / "config.json"
        self.ensure_master_exists()
        
    def ensure_master_exists(self):
        """Ensure the global config file exists."""
        if not self.master_dir.exists():
            self.master_dir.mkdir(parents=True, exist_ok=True)
            
        if not self.config_path.exists():
            self.reset_to_defaults()

    def _load(self) -> dict:
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return self.reset_to_defaults()

    def _save(self, data: dict) -> None:
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def reset_to_defaults(self) -> dict:
        default_data = {
            "workspace_root": str(self.master_dir),
            "theme": "light",
            "last_username": ""
        }
        self._save(default_data)
        return default_data

    def get_workspace_path(self) -> Path:
        data = self._load()
        # Fallback to master_dir if invalid path representation
        path_str = data.get("workspace_root", str(self.master_dir))
        return Path(path_str)

    def set_workspace_path(self, new_val: Path) -> None:
        data = self._load()
        data["workspace_root"] = str(new_val)
        self._save(data)

    def get_theme(self) -> str:
        data = self._load()
        return data.get("theme", "light")

    def set_theme(self, theme: str) -> None:
        data = self._load()
        data["theme"] = theme
        self._save(data)

    def get_last_username(self) -> str:
        data = self._load()
        return data.get("last_username", "")

    def set_last_username(self, username: str) -> None:
        data = self._load()
        data["last_username"] = username
        self._save(data)

