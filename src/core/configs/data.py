
from pathlib import Path

from core.enums import EncoderEnum
from core.settings import paths_settings
from schemas.data import (
    DatasetConfigSchema,
    EncoderConfigSchema,
    PreprocessingConfigSchema,
    ScalerConfigSchema,
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

        self.scaler_configs: ScalerConfigSchema = self.preprocessing.scaler
        self.encoder_configs: EncoderConfigSchema = self.preprocessing.encoder

        if not self.scaler_configs.use_cols:
            self.scaler_configs.use_cols = self.dataset.numerical_columns
        if not self.encoder_configs.use_cols:
            self.encoder_configs.use_cols = self.dataset.categorical_columns

        if self.scaler_configs.filepath is None:
            self.scaler_configs.filepath = self.scaler_filepath
        if self.encoder_configs.filepath is None:
            self.encoder_configs.filepath = self.encoder_filepath

        if self.encoder_configs.type == EncoderEnum.ONEHOT:
            self.encoder_configs.params["sparse_output"] = False

        if self.scaler_configs.metadata == dict():

            self.scaler_configs.metadata = {
                "type": self.scaler_configs.type,
                "dataset_version": self.dataset.version,
                "dataset_hash": self.dataset.hash,
                "params": self.scaler_configs.params,
                "use_cols": self.scaler_configs.use_cols,
                "version": self.scaler_configs.version,
            }

        if self.encoder_configs.metadata == dict():

            self.encoder_configs.metadata = {
                "type": self.encoder_configs.type,
                "dataset_version": self.dataset.version,
                "dataset_hash": self.dataset.hash,
                "params": self.encoder_configs.params,
                "use_cols": self.encoder_configs.use_cols,
                "version": self.encoder_configs.version,
            }

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
