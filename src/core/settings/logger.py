from pathlib import Path
from typing import Optional

from pydantic import Field

from core.enums import LogLevel

from .base import Base


class LogsSettings(Base):
    """Manages application logging settings."""

    dir: Optional[Path] = Field(
        default=None,
        title="Log Directory",
        description=(
            "Directory where log files are stored. If not specified, logs are "
            "written to the default application logging destination."
        ),
        examples=["logs", "/var/log/my-app"],
    )

    max_mb: int = Field(
        default=5,
        ge=1,
        le=100,
        title="Maximum Log File Size",
        description=(
            "Maximum size of a single log file in megabytes before log rotation "
            "is triggered."
        ),
        examples=[5, 10, 50],
    )

    backup_count: int = Field(
        default=5,
        ge=0,
        le=100,
        title="Backup File Count",
        description=(
            "Maximum number of rotated log files to retain before older files "
            "are automatically removed."
        ),
        examples=[3, 5, 10],
    )

    level: LogLevel = Field(
        default=LogLevel.DEBUG,
        title="Logging Level",
        description=(
            "Minimum logging severity level recorded by the application's "
            "logging system."
        ),
        examples=["DEBUG", "INFO", "WARNING"],
    )

    file_pattern: str = Field(
        default="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        title="File Log Format",
        description=(
            "Logging format string applied to log records written to log files."
        ),
        examples=[
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        ],
    )

    console_pattern: str = Field(
        default="%(levelname)s | %(name)s | %(message)s",
        title="Console Log Format",
        description=(
            "Logging format string applied to log records displayed in the console."
        ),
        examples=[
            "%(levelname)s | %(name)s | %(message)s",
        ],
    )

    @property
    def max_bytes(self) -> int:
        """Convert the configured log size from megabytes to bytes."""
        return self.max_mb * 1024 * 1024

    def _summary(self) -> None:
        """Print logging configuration summary."""
        print("📝 LOGGING:")
        print(f"  DIRECTORY:     {self.dir or 'Default'}")
        print(f"  LEVEL:         {self.level.value}")
        print(f"  MAX SIZE:      {self.max_mb} MB")
        print(f"  MAX BYTES:     {self.max_bytes:,}")
        print(f"  BACKUPS:       {self.backup_count}")
        print("  FORMAT:")
        print(f"    ├── FILE:    {self.file_pattern}")
        print(f"    └── CONSOLE: {self.console_pattern}")
        print()
