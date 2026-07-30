from typing import Optional, Tuple, Union

import numpy as np
from numpy import ndarray
from pandas import DataFrame
from pandas.api.types import is_numeric_dtype

from core import app_logger
from core.configs import dataset_config
from core.decorators import ensure_dependencies
from core.enums import DatasetEnum
from core.exceptions import NotFitError
from schemas.data import DatasetSplitSchema

from .loader import DataLoader
from .preprocessing import Encoder, Scaler, Splitter


class DataPipeline:
    """End-to-end data pipeline for training and prediction."""

    def __init__(self) -> None:
        """Initialize pipeline with lazy-loaded transformers."""
        self.scaler: Optional[Scaler] = None
        self.encoder: Optional[Encoder] = None
        app_logger.info("DataPipeline initialized")

    @ensure_dependencies({'scaler': Scaler, 'encoder': Encoder})
    def training(self) -> Tuple[DatasetSplitSchema, DatasetSplitSchema]:
        """Prepare training data: load, scale, encode, and split."""
        app_logger.info("Starting training pipeline")

        df: DataFrame = DataLoader.from_file(dataset_config.filepath)
        feature, target = Splitter.feature_target(df, load_target=True)
        if target is None:
            app_logger.error("Target is None")
            raise ValueError("Target cannot be None")

        X: ndarray = self.scaler.fit_transform(feature)  # type: ignore
        app_logger.debug(f"Scaled features: {X.shape}")

        if is_numeric_dtype(target.dtype):
            y: ndarray = np.array(target)
            app_logger.debug("Target is numeric")
        else:
            y = self.encoder.fit_transform(target)  # type: ignore
            app_logger.debug(f"Encoded target: {y.shape}")

        train_set, test_set = Splitter.train_test(X, y)
        app_logger.info(
            f"Train: {len(train_set.X)}, Test: {len(test_set.X)} samples")
        return train_set, test_set

    @ensure_dependencies({'scaler': Scaler, 'encoder': Encoder})
    def predictor(self, data: Union[DataFrame, ndarray]) -> DatasetSplitSchema:
        """Transform data for prediction using fitted scaler."""
        app_logger.debug("Preparing prediction data")
        X: ndarray = self.scaler.transform(data)  # type: ignore
        return DatasetSplitSchema(type=DatasetEnum.PREDICTOR, X=X)

    @ensure_dependencies({'scaler': Scaler, 'encoder': Encoder})
    def inverse_predictor(self, data: ndarray) -> Optional[ndarray]:
        """Inverse transform encoded predictions to original format."""
        app_logger.debug("Inverse transforming predictions")
        try:
            result: ndarray = self.encoder.inverse_transform(  # type: ignore
                data
            )
            app_logger.info("Inverse transform successful")
            return result
        except NotFitError as e:
            app_logger.error(f"Encoder not fitted: {e}")
            raise e
        except Exception as e:
            app_logger.error(f"Inverse transform failed: {e}")
            raise e
