from pathlib import Path

import pandas as pd
from pandas import DataFrame

from core.exceptions import NotSupportFormatException
from core.logger import app_logger


class DataLoader:
    """Loads data from various file formats into pandas DataFrame."""

    @staticmethod
    def _from_csv(filepath: Path) -> DataFrame:
        """Load CSV file into DataFrame."""
        df: DataFrame = pd.read_csv(filepath)
        app_logger.info(f"CSV file loaded: {filepath}")
        return df

    @staticmethod
    def from_file(filepath: Path) -> DataFrame:
        """Load data from file based on extension."""
        if filepath.suffix == ".csv":
            return DataLoader._from_csv(filepath)

        app_logger.error(f"Unsupported format: {filepath.suffix}")
        raise NotSupportFormatException(
            f"Format {filepath.suffix} not supported")
