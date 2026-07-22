"""
file_manager.py
---------------
Handles post-import movement of workbooks from *Incoming Orders* to
*Processed Orders*.

Usage
-----
    wm           = WorkspaceManager()
    file_manager = FileManager(wm)

    # After a successful import:
    destination  = file_manager.move_to_processed(source_path)
"""

import shutil
import logging
import time
import os
from pathlib import Path

from filesystem.workspace_manager import WorkspaceManager

logger = logging.getLogger(__name__)


class FileManager:
    """
    Moves successfully imported workbooks into the *Processed Orders*
    folder.

    **Never overwrites an existing file.**  When a name collision is
    detected the manager appends an incrementing counter suffix using
    the Windows Explorer convention::

        PO.xlsx  →  PO (1).xlsx  →  PO (2).xlsx  →  …

    Failed imports are intentionally left in *Incoming Orders*; the
    caller (controller / GUI) decides whether to move them.

    Parameters
    ----------
    workspace : WorkspaceManager
        The shared workspace manager that provides the ``processed``
        destination path.  Injected to keep this class decoupled from
        the concrete storage layout.
    """

    def __init__(self, workspace: WorkspaceManager) -> None:
        self._workspace = workspace

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def move_to_processed(self, source: Path) -> Path:
        """
        Move *source* from *Incoming Orders* to *Processed Orders*.

        Parameters
        ----------
        source : Path
            Absolute path to the workbook that was successfully imported.
            Must be an existing file.

        Returns
        -------
        Path
            The final destination path (may include a numeric suffix if
            a file with the same stem already existed).

        Raises
        ------
        FileNotFoundError
            If *source* does not exist at call time.
        IsADirectoryError
            If *source* refers to a directory rather than a file.
        PermissionError
            If insufficient permissions to read source or write to destination.
        OSError
            For other OS-level errors (disk full, network issues, etc.).
        """
        if not source.exists():
            raise FileNotFoundError(
                f"Cannot move '{source.name}': source file not found."
            )
        if not source.is_file():
            raise IsADirectoryError(
                f"Cannot move '{source.name}': source is not a file."
            )

        destination = self._resolve_destination(source.name)
        max_retries = 3
        retry_delay = 0.1  # 100ms

        # Preserve metadata before move
        try:
            stat_info = source.stat()
            original_mtime = stat_info.st_mtime
            original_atime = stat_info.st_atime
        except OSError as e:
            logger.warning(f"Could not read metadata from '{source.name}': {e}")
            original_mtime = None
            original_atime = None

        for attempt in range(max_retries):
            try:
                logger.info(f"Moving '{source.name}' from '{source.parent}' to '{destination.parent}'")
                shutil.move(str(source), str(destination))

                # Restore metadata if available
                if original_mtime is not None and original_atime is not None:
                    try:
                        os.utime(destination, (original_atime, original_mtime))
                        logger.debug(f"Restored metadata for '{destination.name}'")
                    except OSError as e:
                        logger.warning(f"Could not restore metadata for '{destination.name}': {e}")

                logger.info(f"Successfully moved '{source.name}' to '{destination}'")
                return destination
            except PermissionError as e:
                logger.error(f"Permission denied moving '{source.name}': {e}")
                raise PermissionError(
                    f"Cannot move '{source.name}': insufficient permissions. {e}"
                ) from e
            except OSError as e:
                # Check if it's a file exists error (possible race condition)
                if "already exists" in str(e).lower() or destination.exists():
                    if attempt < max_retries - 1:
                        logger.warning(f"Destination '{destination}' already exists (attempt {attempt + 1}/{max_retries}), retrying...")
                        # Recalculate destination with new counter
                        destination = self._resolve_destination(source.name)
                        time.sleep(retry_delay)
                        continue
                    else:
                        logger.error(f"Failed to find available destination after {max_retries} attempts")
                        raise OSError(
                            f"Cannot move '{source.name}': unable to resolve destination after {max_retries} attempts"
                        ) from e
                else:
                    logger.error(f"OS error moving '{source.name}': {e}")
                    raise OSError(
                        f"Cannot move '{source.name}': OS error occurred. {e}"
                    ) from e

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _resolve_destination(self, filename: str) -> Path:
        """
        Return a non-colliding destination path inside *Processed Orders*.

        If ``Processed Orders/filename`` does not exist, returns it
        directly.  Otherwise appends ``(1)``, ``(2)``, … to the stem
        until a free slot is found.

        Parameters
        ----------
        filename : str
            Original filename (e.g. ``"PO.xlsx"``).

        Returns
        -------
        Path
            A path that does not yet exist in *Processed Orders*.
        """
        processed: Path = self._workspace.processed
        candidate: Path = processed / filename

        if not candidate.exists():
            return candidate

        stem: str = Path(filename).stem
        suffix: str = Path(filename).suffix
        counter: int = 1

        while True:
            candidate = processed / f"{stem} ({counter}){suffix}"
            if not candidate.exists():
                return candidate
            counter += 1
