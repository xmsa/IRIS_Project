import logging
from enum import Enum
from typing import Dict, Optional

from sklearn.preprocessing import (
    LabelEncoder,
    MinMaxScaler,
    OneHotEncoder,
    RobustScaler,
    StandardScaler,
)

from .types import EncoderType, ScalerType


class BaseEnum(str, Enum):
    @classmethod
    def from_string(cls, value: str) -> "BaseEnum":
        value_lower: str = value.lower()
        for member in cls:
            if member.value == value_lower:
                return member
        raise ValueError(f"Unknown value: {value}")


class EnvironmentEnum(BaseEnum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class LogCategory(BaseEnum):
    APPLICATION = "Application"
    API = "API"
    DATABASE = "Database"
    REPORT = "Report"
    MINIO = "MinIO"
    MLFLOW = "Mlflow"


class LogLevel(BaseEnum):
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


class DatasetEnum(BaseEnum):
    TRAIN = "Train"
    TEST = "Test"
    VAL = "Val"


class ArtifactSourceEnum(BaseEnum):
    MLFLOW = "mlflow"
    LOCAL = "local"


class ScalerEnum(BaseEnum):
    STANDARD = "standard"
    MINMAX = "minmax"
    ROBUST = "robust"

    def get(self, **kwargs) -> ScalerType:
        scalers: Dict = {
            ScalerEnum.STANDARD: StandardScaler,
            ScalerEnum.MINMAX: MinMaxScaler,
            ScalerEnum.ROBUST: RobustScaler,
        }

        scaler_class: Optional[ScalerType] = scalers.get(self)
        if scaler_class is None:
            raise ValueError(f"Unknown scaler type: {self}")

        return scaler_class(**kwargs)


class EncoderEnum(BaseEnum):
    LABEL = "label"
    ONEHOT = "onehot"

    def get(self, **kwargs) -> EncoderType:
        encoder: Dict = {
            EncoderEnum.LABEL: LabelEncoder,
            EncoderEnum.ONEHOT: OneHotEncoder,
        }

        scaler_class: Optional[EncoderType] = encoder.get(self)
        if scaler_class is None:
            raise ValueError(f"Unknown scaler type: {self}")

        return scaler_class(**kwargs)
