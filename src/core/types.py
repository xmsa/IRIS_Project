from typing import TypeAlias, Union

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import (
    LabelEncoder,
    MinMaxScaler,
    OneHotEncoder,
    RobustScaler,
    StandardScaler,
)
from sklearn.svm import SVC

EncoderType: TypeAlias = LabelEncoder | OneHotEncoder
ScalerType: TypeAlias = MinMaxScaler | RobustScaler | StandardScaler
ProcessorType: TypeAlias = EncoderType | ScalerType

ModelType: TypeAlias = Union[
    SVC,
    RandomForestClassifier,
]

MlflowSupportedModel: TypeAlias = ProcessorType | ModelType
SkopsObjectType: TypeAlias = Union[ProcessorType, ModelType]
