import logging
from enum import Enum


class EnvironmentEnum(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class LogCategory(str, Enum):
    APPLICATION = "Application"
    API = "API"
    DATABASE = "Database"
    REPORT = "Report"
    MINIO = "MinIO"
    MLFLOW = "Mlflow"


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    @property
    def to_int(self) -> int:
        return {
            self.DEBUG: logging.DEBUG,
            self.INFO: logging.INFO,
            self.WARNING: logging.WARNING,
            self.ERROR: logging.ERROR,
            self.CRITICAL: logging.CRITICAL,
        }[self]
