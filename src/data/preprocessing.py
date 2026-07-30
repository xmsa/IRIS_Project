from typing import Optional, Tuple

from numpy import ndarray
from pandas import DataFrame, Series
from sklearn.model_selection import train_test_split

from core import app_logger
from core.configs import (
    data_preprocessing_configs,
    dataset_config,
)
from core.enums import DatasetEnum
from schemas.data import (
    DatasetConfigSchema,
    DatasetSplitSchema,
    PreprocessingConfigSchema,
)


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
