
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Type, Union

import numpy as np
from numpy import ndarray
from pandas import DataFrame, Series

from .enums import EncoderEnum
from .exceptions import CustomAttributeError, FittedError, NotFitError


def dataframe_to_numpy(func):
    @wraps(func)
    def wrapper(self, data: DataFrame | ndarray | Series, *args, **kwargs) -> ndarray:
        if isinstance(data, Series) and self.configs.type == EncoderEnum.ONEHOT:
            data = np.array(data)
            data = data.reshape((-1, 1))
        if isinstance(data, DataFrame):
            data = data[self.configs.use_cols]
            data = np.array(data)
        return func(self, data, *args, **kwargs)
    return wrapper


def require_fit(fitted=True) -> Callable:
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            if not hasattr(self, '_is_fit'):
                raise CustomAttributeError(
                    attribute="_is_fit",
                    file=type(self).__name__,
                )
            _type: str = self._type if hasattr(self, '_type') else "Model"

            if fitted and not self._is_fit:
                raise NotFitError(_type)
            elif not fitted and self._is_fit:
                raise FittedError(_type)
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def ensure_dependencies(deps: Dict[str, Type]) -> Callable:
    """
    Ensure required dependencies are initialized.

    Args:
        deps: Dictionary mapping attribute names to class types
              e.g., {'scaler': Scaler, 'encoder': Encoder}

    Example:
        @ensure_dependencies({'scaler': Scaler, 'encoder': Encoder})
        def process(self, data):
            self.scaler.transform(data)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            for attr_name, class_type in deps.items():
                if getattr(self, attr_name, None) is None:
                    setattr(self, attr_name, class_type())
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def check_exists(exists: bool = True, allow_overwrite: bool = False) -> Callable:
    """Decorator to validate file existence before operations."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(filepath: Union[str, Path], *args, **kwargs) -> Any:
            path: Path = Path(filepath) if isinstance(
                filepath, str) else filepath
            overwrite = kwargs.get('overwrite', allow_overwrite)

            if overwrite:
                return func(path, *args, **kwargs)

            if exists and not path.exists():
                raise FileNotFoundError(f"File not found: {path}")
            if not exists and path.exists():
                raise FileExistsError(f"File already exists: {path}")

            return func(path, *args, **kwargs)
        return wrapper
    return decorator
