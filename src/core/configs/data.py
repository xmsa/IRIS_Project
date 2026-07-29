
from pathlib import Path

from core.settings import paths_settings
from schemas.data import (
    DatasetConfigSchema,
    PreprocessingConfigSchema,
)


class DataConfigs:
    def __init__(self) -> None:
        data_config_path: Path = paths_settings.data_config_dir
        dataset_config_path: Path = data_config_path/"dataset.yml"
        preprocessing_config_path: Path = data_config_path/"preprocessing.yml"
        self.dataset: DatasetConfigSchema = DatasetConfigSchema.from_yaml(
            dataset_config_path)
        self.preprocessing: PreprocessingConfigSchema = PreprocessingConfigSchema.from_yaml(
            preprocessing_config_path)

        if not self.preprocessing.scaler.use_cols:
            self.preprocessing.scaler.use_cols = self.dataset.numerical_columns
        if not self.preprocessing.encoder.use_cols:
            self.preprocessing.encoder.use_cols = self.dataset.categorical_columns

    @property
    def encoder_filepath(self) -> Path:
        dir_path: Path = paths_settings.encoder_artifact_dir
        filename: str = self.preprocessing.encoder.filename
        dataset_version: str = self.dataset.version

        return dir_path/f"{filename}_data_{dataset_version}.skops"

    @property
    def scaler_filepath(self) -> Path:
        dir_path: Path = paths_settings.scaler_artifact_dir
        filename: str = self.preprocessing.scaler.filename
        dataset_version: str = self.dataset.version

        return dir_path/f"{filename}_data_{dataset_version}.skops"
