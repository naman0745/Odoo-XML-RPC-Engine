"""
folder_scanner.py
-----------------
Discovers pending Purchase Order workbooks in the *Incoming Orders*
folder.

Usage
-----
    wm      = WorkspaceManager()
    scanner = FolderScanner(wm)
    files   = scanner.get_pending_files()   # list[Path], sorted A→Z
"""

from pathlib import Path

from filesystem.workspace_manager import WorkspaceManager

# File extensions treated as importable workbooks (lower-case).
_SUPPORTED_EXTENSIONS: frozenset[str] = frozenset({".xlsx", ".xls"})


class FolderScanner:
    """
    Scans the *Incoming Orders* folder for importable Excel workbooks.

    The scanner applies the following exclusion rules in order:

    1. **Directories** — ``entry.is_file()`` must be ``True``.
    2. **Hidden files** — names starting with ``.`` are skipped.
    3. **Temporary Excel lock files** — names starting with ``~$`` are
       skipped (created by Excel/LibreOffice while a workbook is open).
    4. **Unsupported extensions** — only ``.xlsx`` and ``.xls`` pass.
    5. **Invalid filesystem entries** — any ``OSError`` raised while
       inspecting an entry is caught and that entry is silently skipped.

    Parameters
    ----------
    workspace : WorkspaceManager
        The shared workspace manager that provides the ``incoming``
        path.  Injected to keep this class decoupled from the concrete
        storage layout.
    """

    def __init__(self, workspace: WorkspaceManager) -> None:
        self._workspace = workspace

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_pending_files(self) -> list[Path]:
        """
        Return a sorted list of importable workbooks found in the
        *Incoming Orders* folder.

        Returns
        -------
        list[Path]
            Absolute ``Path`` objects sorted alphabetically by filename
            (case-insensitive).  Returns an empty list when the folder
            does not exist or contains no qualifying files.
        """
        incoming: Path = self._workspace.incoming

        if not incoming.is_dir():
            return []

        pending: list[Path] = []

        for entry in incoming.iterdir():
            try:
                if self._is_importable(entry):
                    pending.append(entry)
            except OSError:
                # Skip entries that cannot be inspected (e.g. broken
                # symlinks, permission errors, race-condition deletions).
                continue

        # Stable, case-insensitive alphabetical sort so the processing
        # order is deterministic and predictable for the user.
        pending.sort(key=lambda p: p.name.lower())
        return pending

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_importable(entry: Path) -> bool:
        """
        Return ``True`` only when *entry* is a regular file with a
        supported extension that is not a temporary or hidden file.

        Parameters
        ----------
        entry : Path
            A filesystem entry returned by ``Path.iterdir()``.
        """
        # Rule 1: must be a regular file (excludes directories, symlinks
        # to directories, etc.)
        if not entry.is_file():
            return False

        name: str = entry.name

        # Rule 2: skip hidden files (Unix-style dot-files).
        if name.startswith("."):
            return False

        # Rule 3: skip Excel/LibreOffice temporary lock files.
        if name.startswith("~$"):
            return False

        # Rule 4: extension must be in the supported set.
        if entry.suffix.lower() not in _SUPPORTED_EXTENSIONS:
            return False

        return True
