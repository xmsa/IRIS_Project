

from typing import Dict

from schemas.base import BaseConfigModel
from schemas.data import (
    DatasetConfigSchema,
    EncoderConfigSchema,
    PreprocessingConfigSchema,
    ScalerConfigSchema,
)

from .data import DataConfigs


class Configs:
    def __init__(self) -> None:
        self.data = DataConfigs()

    def get_all_configs(self) -> Dict[str, BaseConfigModel]:
        """Get all configs as dict"""
        return {
            "dataset": self.data.dataset,
            "preprocessing": self.data.preprocessing,
        }


configs = Configs()

data_configs: DataConfigs = configs.data
dataset_config: DatasetConfigSchema = data_configs.dataset
data_preprocessing_configs: PreprocessingConfigSchema = data_configs.preprocessing
data_scaler_configs: ScalerConfigSchema = data_preprocessing_configs.scaler
data_encoder_configs: EncoderConfigSchema = data_preprocessing_configs.encoder
