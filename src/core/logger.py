import logging
from logging import Formatter, StreamHandler
from logging import Logger as Default_Logger
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, TextIO

from .enums import LogCategory, LogLevel
from .settings import LogsSettings, logger_settings


class LoggerFactory:
    """
    A professional, scalable and clean logging system using Enum for both
    categories and message levels, supporting rotating files + console output.
    """

    def __init__(
        self,
        setting: Optional[LogsSettings] = None
    ) -> None:
        if setting is None:
            settings: LogsSettings = logger_settings

        if settings.dir:
            self.log_dir: Path = settings.dir

        self.max_bytes: int = settings.max_bytes
        self.backup_count: int = settings.backup_count
        self.default_level: LogLevel = settings.level

        self.loggers: dict[LogCategory, Default_Logger] = {}

        self.file_formatter = Formatter(settings.file_pattern)
        self.console_formatter = Formatter(settings.console_pattern)

        # Pre-create loggers for all categories
        for category in LogCategory:
            self.loggers[category] = self._create_logger(category)

    # -------------------------------------------

    def _create_logger(self, category: LogCategory) -> Default_Logger:
        """Create logger with rotating file + console output."""

        logger: Default_Logger = logging.getLogger(category.value)
        logger.setLevel(self.default_level.value)
        logger.propagate = False
        if not logger.handlers:
            # FILE HANDLER (Rotating)
            file_handler = RotatingFileHandler(
                filename=self.log_dir / f"{category.value}.log",
                maxBytes=self.max_bytes,
                backupCount=self.backup_count,
                encoding="utf-8",
            )
            file_handler.setFormatter(self.file_formatter)

            # CONSOLE HANDLER
            console_handler: StreamHandler[TextIO] = StreamHandler()
            console_handler.setFormatter(self.console_formatter)

            logger.addHandler(file_handler)
            logger.addHandler(console_handler)

        return logger

    # -------------------------------------------

    def get(self, category: LogCategory) -> Default_Logger:
        """Retrieve logger; create if does not exist."""
        if category not in self.loggers:
            self.loggers[category] = self._create_logger(category)
        return self.loggers[category]

    # -------------------------------------------

    def log(self, category: LogCategory, level: LogLevel, message: str) -> None:
        """Unified logging interface using Enum types."""
        logger: Default_Logger = self.get(category)
        logger.log(level.to_int, message)


class Logger:
    def __init__(self) -> None:
        logger_factory = LoggerFactory()

        # Create loggers for different categories
        self.app: Default_Logger = logger_factory.get(LogCategory.APPLICATION)
        self.report: Default_Logger = logger_factory.get(LogCategory.REPORT)
        self.api: Default_Logger = logger_factory.get(LogCategory.API)
        self.database: Default_Logger = logger_factory.get(
            LogCategory.DATABASE)
        self.minio: Default_Logger = logger_factory.get(LogCategory.MINIO)
        self.mlflow: Default_Logger = logger_factory.get(LogCategory.MLFLOW)


logger = Logger()
app_logger: Default_Logger = logger.app
report_logger: Default_Logger = logger.report
api_logger: Default_Logger = logger.api
database_logger: Default_Logger = logger.database
minio_logger: Default_Logger = logger.minio
mlflow_logger: Default_Logger = logger.mlflow
