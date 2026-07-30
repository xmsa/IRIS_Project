from pathlib import Path
from typing import Dict, Optional, Tuple, Union

import numpy as np
from numpy import ndarray
from pandas import DataFrame, Series
from sklearn.model_selection import train_test_split

from core.configs import (
    data_encoder_configs,
    data_preprocessing_configs,
    data_scaler_configs,
    dataset_config,
)
from core.decorators import dataframe_to_numpy, require_fit
from core.enums import ArtifactSourceEnum, DatasetEnum
from core.logger import app_logger
from core.types import ProcessorType
from schemas.data import (
    DatasetConfigSchema,
    DatasetSplitSchema,
    EncoderConfigSchema,
    PreprocessingConfigSchema,
    ScalerConfigSchema,
    TransformerSchemaType,
)
from utils.file_handler import FileReader, FileWriter, SkopsArtifact


class Splitter:
    """Handles dataset splitting operations for feature-target separation and train-test splitting."""

    @staticmethod
    def feature_target(df: DataFrame, load_target: bool = True) -> Tuple[DataFrame, Optional[Series]]:
        """Split DataFrame into features and target column."""

        config: DatasetConfigSchema = dataset_config

        app_logger.debug(
            f"Extracting features from columns: {config.feature_columns}")
        feature: DataFrame = df[config.feature_columns]
        app_logger.debug(f"Features shape: {feature.shape}")

        if load_target:
            app_logger.debug(
                f"Extracting target column: {config.target_column}")
            target: Optional[Series] = df[config.target_column]
            app_logger.debug(f"Target shape: {target.shape}")
        else:
            app_logger.info("Target loading disabled (load_target=False)")
            target = None

        app_logger.info(
            f"Successfully split features ({feature.shape[1]} columns) and target")
        return feature, target

    @staticmethod
    def train_test(X: ndarray, y: ndarray) -> Tuple[DatasetSplitSchema, DatasetSplitSchema]:
        """Split arrays into train and test sets with optional stratification."""
        config: PreprocessingConfigSchema = data_preprocessing_configs

        # Validate input
        if len(X) != len(y):
            error_msg = f"X length ({len(X)}) does not match y length ({len(y)})"
            app_logger.error(error_msg)
            raise ValueError(error_msg)

        app_logger.info(
            f"Splitting data with test_size={config.test_size}, "
            f"random_state={config.random_state}, "
            f"shuffle={config.shuffle_data}, "
            f"stratify={config.shuffle_data}"
        )

        app_logger.debug(f"Input X shape: {X.shape}, y shape: {y.shape}")

        # Perform train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=config.test_size,
            random_state=config.random_state,
            shuffle=config.shuffle_data,
            stratify=y if config.shuffle_data else None
        )

        app_logger.info(f"Train set: X={X_train.shape}, y={y_train.shape}")
        app_logger.info(f"Test set: X={X_test.shape}, y={y_test.shape}")

        if config.shuffle_data:
            app_logger.debug(
                f"Data shuffled with random_state={config.random_state} and stratified split")
        else:
            app_logger.debug(
                "Data split without shuffling (stratification disabled)")

        # Create dataset schemas
        train_set = DatasetSplitSchema(
            type=DatasetEnum.TRAIN,
            X=X_train, y=y_train
        )

        test_set = DatasetSplitSchema(
            type=DatasetEnum.TEST,
            X=X_test, y=y_test
        )

        app_logger.debug(
            "Created DatasetSplitSchema objects for TRAIN and TEST")

        return train_set, test_set


class BaseTransformer:
    """
    Base class for all transformers (Scaler and Encoder).
    Handles loading, building, fitting, transforming, and saving transformers.
    """
    _is_fit: bool = False

    def __init__(self, configs: TransformerSchemaType) -> None:
        self.configs: TransformerSchemaType = configs
        self._type: str = self.configs.type.value
        self._artifact_source: ArtifactSourceEnum = data_preprocessing_configs.artifact_source
        self._obj: ProcessorType = self._load_or_build()

    def _load_or_build(self) -> ProcessorType:
        """Load existing transformer or build a new one."""
        try:
            obj: ProcessorType = self._load()
            self._is_fit = True
            app_logger.info(
                f"Successfully loaded {self._type} from {self._artifact_source.value}")
        except (NotImplementedError, FileNotFoundError) as e:
            app_logger.warning(
                f"Could not load from {self._artifact_source.value}, building new transformer: {e}")
            obj = self._build()
            self._is_fit = False
        except Exception as e:
            app_logger.error(f"Error loading transformer: {e}")
            raise e
        return obj

    def _load(self) -> ProcessorType:
        """Load transformer from artifact source."""
        if self._artifact_source == ArtifactSourceEnum.LOCAL:
            skops_artifact: SkopsArtifact = FileReader.skops(
                self.configs.filepath, self.configs.metadata  # type: ignore
            )
            if isinstance(skops_artifact.obj, ProcessorType):
                app_logger.debug(
                    f"Loaded {self._type} from {self.configs.filepath}")
                return skops_artifact.obj
            else:
                app_logger.error("Loaded object is not a ProcessorType")
                raise TypeError("Loaded object is not a ProcessorType")

        elif self._artifact_source == ArtifactSourceEnum.MLFLOW:
            app_logger.error("MLFLOW loading not implemented yet")
            raise NotImplementedError("MLFLOW loading not implemented")
        else:
            raise NotImplementedError(
                f"No loader found for {self._artifact_source}")

    @require_fit(fitted=True)
    def _save(self) -> None:
        """Save transformer to artifact source."""
        if self._obj is None:
            app_logger.error("Cannot save: No object to save")
            raise ValueError("No object to save")

        if self._artifact_source == ArtifactSourceEnum.LOCAL:
            filepath: Optional[Path] = self.configs.filepath
            skops_artifact = SkopsArtifact(
                obj=self._obj,
                metadata=self.configs.metadata
            )
            FileWriter.skops(
                filepath=filepath,  # type: ignore
                skops_artifact=skops_artifact,
                overwrite=True
            )
            app_logger.info(f"Transformer saved to {filepath}")
            app_logger.debug(f"Metadata: {self.configs.metadata}")

        elif self._artifact_source == ArtifactSourceEnum.MLFLOW:
            app_logger.error("MLFLOW saving not implemented yet")
            raise NotImplementedError("MLFLOW saving not implemented")

        app_logger.info(f"Successfully saved {self.model_name}")

    def _build(self) -> ProcessorType:
        """Build a new transformer instance from configuration."""
        params: Dict = self.configs.params
        obj: ProcessorType = self.configs.type.get(**params)
        self._is_fit = False
        app_logger.debug(
            f"Built new {self._type} transformer with params: {params}")
        return obj

    @require_fit(fitted=False)
    @dataframe_to_numpy
    def fit(self, data: Union[DataFrame, ndarray]) -> 'BaseTransformer':
        """Fit the transformer to data and save it."""
        app_logger.info(f"Fitting {self._type} transformer...")
        app_logger.debug(
            f"Data shape: {data.shape if hasattr(data, 'shape') else 'unknown'}")

        self._obj.fit(data)
        self._is_fit = True
        app_logger.info(f"Successfully fitted {self._type}")

        self._save()
        return self

    @require_fit(fitted=True)
    @dataframe_to_numpy
    def transform(self, data: Union[DataFrame, ndarray]) -> ndarray:
        """Transform data using fitted transformer."""
        app_logger.debug(
            f"Transforming data with {self._type}, shape: {data.shape if hasattr(data, 'shape') else 'unknown'}")
        transformed = self._obj.transform(data)
        app_logger.debug(
            f"Transformed data shape: {transformed.shape if hasattr(transformed, 'shape') and isinstance(transformed, ndarray) else 'unknown'}")
        return np.array(transformed)

    def fit_transform(self, data: Union[DataFrame, ndarray]) -> ndarray:
        """Fit transformer and transform data in one step."""
        app_logger.info(f"Performing fit_transform on {self._type}")
        try:
            self.fit(data)
        except RuntimeError as exc:
            app_logger.warning(f"Warning during fit: {exc}")
        return self.transform(data)

    @require_fit(fitted=True)
    def inverse_transform(self, data: ndarray) -> ndarray:
        """Inverse transform data if the transformer supports it."""
        if hasattr(self._obj, 'inverse_transform'):
            app_logger.debug(f"Performing inverse_transform on {self._type}")
            return self._obj.inverse_transform(data)
        else:
            app_logger.error(
                f"{self._type} does not support inverse_transform")
            raise AttributeError(
                f"{self._type} does not support inverse_transform")

    @property
    def model_name(self) -> str:
        """Return the name of the transformer."""
        return self.configs.name

    @property
    def is_fitted(self) -> bool:
        """Check if transformer is fitted."""
        return self._is_fit


class Scaler(BaseTransformer):
    """Scaler transformer for feature scaling."""

    def __init__(self, configs: ScalerConfigSchema = data_scaler_configs) -> None:
        super().__init__(configs)
        app_logger.debug(
            f"Initialized Scaler with config: {configs.type.value}")


class Encoder(BaseTransformer):
    """Encoder transformer for categorical encoding."""

    def __init__(self, configs: EncoderConfigSchema = data_encoder_configs) -> None:
        super().__init__(configs)
        app_logger.debug(
            f"Initialized Encoder with config: {configs.type.value}")
