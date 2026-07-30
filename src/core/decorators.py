
from functools import _Wrapped, wraps
from typing import Any, Callable

import numpy as np
from numpy import ndarray
from pandas import DataFrame, Series

from .enums import EncoderEnum
from .exceptions import CustomAttributeError, FittedError, NotFitError


def dataframe_to_numpy(func) -> _Wrapped:
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
    def decorator(func) -> _Wrapped:
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
