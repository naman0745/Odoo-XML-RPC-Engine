import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


class ImportLogger:
    """
    Lightweight import logger for console and rotating file output.

    The logger is safe to instantiate multiple times; handlers are attached
    only once for the shared logger name.
    """

    def __init__(
        self,
        log_file: str = "logs/import.log",
        max_bytes: int = 1_000_000,
        backup_count: int = 3,
    ) -> None:
        self._logger = logging.getLogger("po_import")
        self._logger.setLevel(logging.INFO)
        self._logger.propagate = False

        if self._logger.handlers:
            return

        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        formatter = logging.Formatter("[%(levelname)s] %(message)s")

        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)

    def set_log_file(self, log_file: str) -> None:
        """Update the log file path dynamically."""
        for handler in self._logger.handlers[:]:
            if isinstance(handler, RotatingFileHandler):
                self._logger.removeHandler(handler)
                handler.close()
                break
        
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
        )
        formatter = logging.Formatter("[%(levelname)s] %(message)s")
        file_handler.setFormatter(formatter)
        
        # Prepend to handlers so it logs to file first
        self._logger.handlers.insert(0, file_handler)

    def info(self, msg: str) -> None:
        self._logger.info(msg)

    def warning(self, msg: str) -> None:
        self._logger.warning(msg)

    def error(self, msg: str) -> None:
        self._logger.error(msg)
