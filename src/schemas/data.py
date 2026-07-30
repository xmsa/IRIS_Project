from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TypeAlias, Union

import numpy as np
from numpy import ndarray
from pydantic import ConfigDict, Field

from core.enums import ArtifactSourceEnum, DatasetEnum, EncoderEnum, ScalerEnum
from core.exceptions import DatasetHashMismatchError
from core.settings import paths_settings
from utils.version_control import VersionControl

from .base import BaseConfigModel


class DatasetConfigSchema(BaseConfigModel):
    """Dataset configuration."""

    version: str = Field(
        default="v1",
        min_length=1,
        title="Dataset Version",
        description="Version identifier of the dataset.",
        examples=["v1", "v2"],
    )

    name: str = Field(
        ...,
        min_length=1,
        title="Dataset Name",
        description="Unique name of the dataset.",
        examples=["iris", "customer_churn"],
    )

    filetype: str = Field(
        ...,
        min_length=1,
        title="Dataset File Type",
        description="Dataset file extension without the dot.",
        examples=["csv", "parquet", "xlsx"],
    )

    feature_columns: List[str] = Field(
        ...,
        min_length=1,
        title="Feature Columns",
        description="List of feature columns used as model inputs.",
        examples=[["age", "salary", "gender"]],
    )

    target_column: str = Field(
        ...,
        min_length=1,
        title="Target Column",
        description="Column used as the prediction target.",
        examples=["price", "label"],
    )

    categorical_columns: List[str] = Field(
        default_factory=list,
        title="Categorical Columns",
        description="Categorical feature columns.",
        examples=[["gender", "city"]],
    )

    numerical_columns: List[str] = Field(
        default_factory=list,
        title="Numerical Columns",
        description="Numerical feature columns.",
        examples=[["age", "salary"]],
    )

    hash: Optional[str] = Field(
        default=None,
        title="Dataset Hash",
        description="Checksum or hash used to verify dataset integrity.",
        examples=["f83d5f8c23a4c7e6"],
    )

    @property
    def filename(self) -> str:
        return f"{self.name}_{self.version}.{self.filetype}"

    @property
    def filepath(self) -> Path:
        return paths_settings.raw_data_dir/self.filename

    @property
    def get_all_columns(self) -> List[str]:
        return [*self.feature_columns, self.target_column]

    def model_post_init(self, __context,) -> None:
        dataset_hash: str = VersionControl.database_hash_with_dvc(
            self.filepath)

        if self.hash is None:
            self.hash = dataset_hash
        elif self.hash != dataset_hash:
            raise DatasetHashMismatchError(
                "Dataset integrity check failed. "
                f"Expected hash '{self.hash}', "
                f"but computed '{dataset_hash}' "
                f"for file '{self.filepath}'."
            )


class ScalerConfigSchema(BaseConfigModel):
    """Scaler configuration."""

    name: str = Field(
        default="standard_scaler",
        min_length=1,
        title="Scaler Name",
        description="Name used when saving the scaler.",
        examples=["standard_scaler"],
    )

    type: ScalerEnum = Field(
        default=ScalerEnum.STANDARD,
        title="Scaler Type",
        description="Scaler implementation.",
        examples=[ScalerEnum.STANDARD],
    )

    params: Dict[str, Any] = Field(
        default_factory=dict,
        title="Scaler Parameters",
        description="Additional keyword arguments passed to the scaler.",
        examples=[
            {"with_mean": True, "with_std": True},
            {"feature_range": [0, 1]}
        ],

    )

    use_cols: List[str] = Field(
        default_factory=list,
        title="Scaler Columns",
        description="Columns that should be scaled.",
        examples=[
            ["age", "salary"],
            [
                "sepal_length",
                "sepal_width",
                "petal_length",
                "petal_width",
            ]
        ],
    )

    version: str = Field(
        default="v1",
        min_length=1,
        title="Scaler Version",
        description="Version of the scaler configuration.",
        examples=["v1"],
    )

    filepath: Optional[Path] = Field(
        default=None,
        title="Scaler file path(skops format)",
        description="Path to the scaler file (e.g., StandardScaler, MinMaxScaler) for loading or saving",
        examples=["./artifacts/scaler/<name>.skops"],
    )

    metadata: Dict = Field(
        default_factory=dict,
        title="Scaler metadata",
        description="Additional metadata for the scaler including parameters, features, and statistics",
        examples=[
            {
                # for MinMaxScaler
                "type": "minmax",
                "dataset_version": "dataset_version",
                "dataset_hash": "Dataset Hash",
                "version": "Scaler version",
                "params": {
                    "feature_range": [0, 1]
                },
                "use_cols": [
                    "sepal_length",
                    "sepal_width",
                    "petal_length",
                    "petal_width",
                ],
            }
        ]

    )

    @property
    def filename(self) -> str:
        return f"{self.type.value}_{self.name}_{self.version}"


class EncoderConfigSchema(BaseConfigModel):
    """Encoder configuration."""

    name: str = Field(
        default="label_encoder",
        min_length=1,
        title="Encoder Name",
        description="Name used when saving the encoder.",
        examples=["label_encoder"],
    )

    type: EncoderEnum = Field(
        default=EncoderEnum.LABEL,
        title="Encoder Type",
        description="Encoding algorithm.",
        examples=[EncoderEnum.LABEL],
    )

    params: Dict[str, Any] = Field(
        default_factory=dict,
        title="Encoder Parameters",
        description="Additional keyword arguments passed to the encoder.",
        examples=[
            {
                "sparse_output": False,  # use for onehot
            }
        ],
    )

    use_cols: List[str] = Field(
        default_factory=list,
        title="Encoder Columns",
        description="Columns that should be encoded.",
        examples=[
            ["gender", "city"],
            ["target"]
        ],
    )

    version: str = Field(
        default="v1",
        min_length=1,
        title="Encoder Version",
        description="Version of the encoder configuration.",
        examples=["v1"],
    )

    metadata: Dict = Field(
        default_factory=dict,
        title="Encoder metadata",
        description="Additional metadata for the encoder including parameters, features, and statistics",
        examples=[
            {
                # for Encoder
                "type": "onehot",
                "dataset_version": "dataset_version",
                "dataset_hash": "Dataset Hash",
                "version": "Encoder version",
                "params": {
                    "sparse_output": False
                },
                "use_cols": ["target"],
            }
        ]
    )

    filepath: Optional[Path] = Field(
        default=None,
        min_length=1,
        title="Encoder file path(Skops file)",
        description="Path to the encoder file (e.g., LabelEncoder, OneHotEncoder) for loading or saving",
        examples=["./artifacts/encoder/<name>.skops"],
    )

    @property
    def filename(self) -> str:
        return f"{self.type.value}_{self.name}_{self.version}"


TransformerSchemaType: TypeAlias = Union[
    ScalerConfigSchema,
    EncoderConfigSchema
]


class PreprocessingConfigSchema(BaseConfigModel):
    """Preprocessing pipeline configuration."""

    scaler: ScalerConfigSchema = Field(
        ...,
        title="Scaler Configuration",
        description="Configuration used for feature scaling.",
    )

    encoder: EncoderConfigSchema = Field(
        ...,
        title="Encoder Configuration",
        description="Configuration used for categorical encoding.",
    )
    artifact_source: ArtifactSourceEnum = Field(
        default=ArtifactSourceEnum.LOCAL,
        title="Artifact Source",
        description=(
            "Specifies where preprocessing artifacts such as encoders and scalers "
            "are loaded from."
        ),
        examples=["local"],
    )

    split_data: bool = Field(
        default=True,
        title="Split Dataset",
        description="Whether to split the dataset into training and testing sets.",
        examples=[True],
    )

    shuffle_data: bool = Field(
        default=True,
        title="Shuffle Dataset",
        description="Shuffle samples before splitting.",
        examples=[True],
    )

    test_size: Optional[float] = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        title="Test Size",
        description="Fraction of samples reserved for the test dataset.",
        examples=[0.2],
    )

    random_state: int = Field(
        default=42,
        ge=0,
        title="Random State",
        description="Seed used to make preprocessing reproducible.",
        examples=[42],
    )


class DatasetSplitSchema(BaseConfigModel):
    """Train/test dataset."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    type: DatasetEnum = Field(
        ...,
        title="Dataset Split",
        description="Indicates whether this data belongs to the train or test split.",
        examples=[DatasetEnum.TRAIN],
    )

    X: ndarray = Field(
        ...,
        title="Feature Matrix",
        description="Feature matrix with shape (n_samples, n_features).",
    )

    y: ndarray = Field(
        default=np.array(np.nan),
        title="Target Values",
        description="Target labels. Can be empty for inference datasets.",
    )

    @property
    def shape(self) -> Tuple[int, int]:
        """Return the shape of the feature matrix."""
        return self.X.shape
