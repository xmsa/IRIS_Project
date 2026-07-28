from typing import TypeAlias

from sklearn.preprocessing import (
    LabelEncoder,
    MinMaxScaler,
    OneHotEncoder,
    RobustScaler,
    StandardScaler,
)

EncoderType: TypeAlias = LabelEncoder | OneHotEncoder
ScalerType: TypeAlias = MinMaxScaler | RobustScaler | StandardScaler
MlflowSupportedModel: TypeAlias = EncoderType | ScalerType
