"""
workspace_manager.py
--------------------
Manages the application's standard folder layout inside the user's
Documents directory.

Default workspace structure
---------------------------
~/Documents/
    Purchase Order Importer/
        Incoming Orders/
        Processed Orders/
        Logs/
        Config/

Usage
-----
    wm = WorkspaceManager()
    wm.ensure_workspace()          # idempotent — safe to call every startup

    source_dir = wm.incoming       # pathlib.Path
"""

from pathlib import Path
from config.app_config import AppConfig


class WorkspaceManager:
    """
    Owns the canonical folder layout for the Purchase Order Importer.

    The workspace root is always created inside the current user's
    *Documents* folder.  All sub-directories are defined here and
    nowhere else; other components depend on this class for paths.

    Parameters
    ----------
    workspace_name : str
        Name of the top-level workspace folder (default:
        ``"Purchase Order Importer"``).
    base_dir : Path | None
        Parent directory that will contain the workspace root.
        Defaults to ``Path.home() / "Documents"``.  Pass a custom
        path in tests to avoid touching the real filesystem.
    """

    _SUB_DIRS: tuple[str, ...] = (
        "Incoming Orders",
        "Processed Orders",
        "Logs",
        "Config",
    )

    def __init__(
        self,
        base_dir: Path | None = None,
    ) -> None:
        if base_dir is not None:
            self._root: Path = base_dir
        else:
            self._root: Path = AppConfig().get_workspace_path()

    # ------------------------------------------------------------------
    # Public path properties
    # ------------------------------------------------------------------

    @property
    def root(self) -> Path:
        """Workspace root: ``<Documents>/Purchase Order Importer``."""
        return self._root

    @property
    def incoming(self) -> Path:
        """Folder for workbooks awaiting import."""
        return self._root / "Incoming Orders"

    @property
    def processed(self) -> Path:
        """Folder for successfully imported workbooks."""
        return self._root / "Processed Orders"

    @property
    def logs(self) -> Path:
        """Folder for application log files."""
        return self._root / "Logs"

    @property
    def config(self) -> Path:
        """Folder for user-editable configuration files."""
        return self._root / "Config"

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def ensure_workspace(self) -> None:
        """
        Create the workspace root and all sub-directories if they do
        not already exist.

        This method is **idempotent**: calling it multiple times (e.g.
        on every application startup) is safe and has no side-effects
        when the directories are already present.  It will also
        re-create any sub-directory that has been accidentally deleted.
        """
        # Check if root already contains workspace structure to prevent recursive creation
        # This handles the case where user selects a folder that's already a workspace subdirectory
        existing_subdirs = [d.name for d in self._root.iterdir()] if self._root.is_dir() else []
        has_workspace_structure = any(sub in existing_subdirs for sub in self._SUB_DIRS)

        if has_workspace_structure:
            # Root already contains workspace structure, don't create nested folders
            return

        for sub in self._SUB_DIRS:
            (self._root / sub).mkdir(parents=True, exist_ok=True)
