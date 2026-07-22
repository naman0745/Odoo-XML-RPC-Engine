"""
models/ui_models.py
"""
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PendingOrderInfo:
    """Structured data passed to the GUI for displaying pending purchase orders."""
    filename: str
    size_kb: int
    modified_date: str
    full_path: Path
