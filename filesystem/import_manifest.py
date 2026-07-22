"""
import_manifest.py
-----------------
Persistent registry of successfully imported Purchase Orders, keyed by
their Order Fingerprint.

Storage
-------
JSON file at ``Config/import_manifest.json`` inside the workspace.
Writes are atomic: data is written to a ``.tmp`` file then renamed so a
crash mid-write never corrupts the manifest.

Usage
-----
    manifest = ImportManifest(workspace.config / "import_manifest.json")

    fp = generate_fingerprint(rows)

    if manifest.is_imported(fp):
        entry = manifest.get_entry(fp)
        # → reject as duplicate

    # … run import …

    manifest.record(fp, po_id=38, vendor="D.R. International", filename="PO1.xlsx")
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

from filesystem.order_fingerprint import FINGERPRINT_VERSION


class ImportManifest:
    """
    Persistent, JSON-backed registry of imported Purchase Order fingerprints.

    Parameters
    ----------
    manifest_path : Path
        Absolute path to ``import_manifest.json``.  The parent directory
        must already exist (``WorkspaceManager.ensure_workspace()`` guarantees
        this in production; tests inject a ``tmp_path``-rooted path).

    Raises
    ------
    RuntimeError
        Raised by :meth:`is_imported`, :meth:`get_entry`, and :meth:`record`
        when the manifest file exists but contains invalid JSON, or when any
        I/O error prevents reading or writing.  Callers **must not** swallow
        this exception — the import pipeline should abort rather than
        silently bypass duplicate detection.
    """

    def __init__(self, manifest_path: Path) -> None:
        self._path = manifest_path

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_imported(self, fingerprint: str) -> bool:
        """
        Return ``True`` if *fingerprint* is already in the manifest.

        Parameters
        ----------
        fingerprint : str
            64-character SHA-256 hex string produced by
            ``order_fingerprint.generate_fingerprint()``.

        Raises
        ------
        RuntimeError
            If the manifest file cannot be read or parsed.
        """
        data = self._load()
        return fingerprint in data

    def get_entry(self, fingerprint: str) -> dict | None:
        """
        Return the full metadata entry for *fingerprint*, or ``None``.

        Parameters
        ----------
        fingerprint : str
            64-character SHA-256 hex string.

        Raises
        ------
        RuntimeError
            If the manifest file cannot be read or parsed.
        """
        data = self._load()
        return data.get(fingerprint)

    def record(
        self,
        fingerprint: str,
        po_id: int,
        vendor: str,
        filename: str,
    ) -> None:
        """
        Persist a new manifest entry for a successfully imported PO.

        Writes are atomic: data is staged to a sibling ``.tmp`` file and
        then renamed over the target path so a crash mid-write leaves the
        previous manifest intact.

        Parameters
        ----------
        fingerprint : str
            64-character SHA-256 hex string.
        po_id : int
            The Odoo ``purchase.order`` ID of the created record.
        vendor : str
            Vendor name as extracted from the workbook.
        filename : str
            Original workbook filename (for human-readable audit trails).

        Raises
        ------
        RuntimeError
            If the manifest cannot be read or written.
        """
        data = self._load()
        data[fingerprint] = {
            "fingerprint_version": FINGERPRINT_VERSION,
            "po_id": po_id,
            "vendor": vendor,
            "filename": filename,
            "imported_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        }
        self._save(data)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load(self) -> dict:
        """
        Load and return the manifest dictionary.

        Returns an empty dict if the file does not exist yet.

        Raises
        ------
        RuntimeError
            If the file exists but is not valid JSON, or if any I/O error
            other than *FileNotFoundError* occurs.
        """
        if not self._path.exists():
            return {}
        try:
            raw = self._path.read_text(encoding="utf-8")
        except OSError as exc:
            raise RuntimeError(
                f"Duplicate protection error: cannot read manifest at "
                f"'{self._path}': {exc}"
            ) from exc
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"Duplicate protection error: manifest at '{self._path}' "
                f"contains invalid JSON: {exc}"
            ) from exc
        if not isinstance(data, dict):
            raise RuntimeError(
                f"Duplicate protection error: manifest at '{self._path}' "
                "has an unexpected format (root must be a JSON object)."
            )
        return data

    def _save(self, data: dict) -> None:
        """
        Write *data* to disk atomically via a sibling temp file.

        Raises
        ------
        RuntimeError
            If the file cannot be written or renamed.
        """
        tmp_path = self._path.with_suffix(".tmp")
        try:
            tmp_path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            os.replace(tmp_path, self._path)
        except OSError as exc:
            # Best-effort cleanup of the temp file.
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass
            raise RuntimeError(
                f"Duplicate protection error: cannot write manifest at "
                f"'{self._path}': {exc}"
            ) from exc
