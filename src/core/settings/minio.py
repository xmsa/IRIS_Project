from typing import Optional

from pydantic import Field, SecretStr, computed_field

from .base import Base


class MinIOSettings(Base):
    """MinIO configuration."""

    domain: str = Field(
        default="localhost",
        title="MinIO Domain",
        description=(
                "Hostname or IP address of the MinIO server used for object storage."
        ),
        examples=["localhost", "minio.example.com"],
    )

    s3_port: int = Field(
        default=9000,
        ge=1,
        le=65535,
        title="S3 API Port",
        description=(
            "Network port exposed by the MinIO S3-compatible API."
        ),
        examples=[9000],
    )

    console_port: int = Field(
        default=9001,
        ge=1,
        le=65535,
        title="Web Console Port",
        description=(
            "Network port used to access the MinIO web management console."
        ),
        examples=[9001],
    )

    access_key: str = Field(
        default="access_key",
        min_length=3,
        title="Access Key",
        description=(
            "Access key used to authenticate requests to the MinIO server."
        ),
        examples=["minioadmin"],
    )

    secret_key: SecretStr = Field(
        default=SecretStr("secret_key"),
        title="Secret Key",
        description=(
            "Secret key paired with the access key for authenticating against MinIO."
        ),
        examples=["minioadmin"],
    )

    secure: bool = Field(
        default=False,
        title="Secure Connection",
        description=(
            "Enables HTTPS communication with the MinIO server when set to True."
        ),
        examples=[False],
    )

    # ----- buckets -----
    dvc_bucket: str = Field(
        default="trial-dvc-store",
        title="DVC Bucket",
        description=(
            "Name of the bucket used by DVC to store versioned datasets and artifacts."
        ),
        examples=["project-dvc-store"],
    )

    artifact_bucket: str = Field(
        default="trial-artifact-store",
        title="MLflow Artifact Bucket",
        description=(
            "Name of the bucket used to store MLflow artifacts, trained models, and related files."
        ),
        examples=["project-artifacts"],
    )

    airflow_bucket: str = Field(
        default="trial-airflow-store",
        title="Airflow Bucket",
        description=(
            "Name of the bucket used for Airflow assets, logs, or intermediate workflow files."
        ),
        examples=["project-airflow"],
    )

    @computed_field
    @property
    def protocol(self) -> str:
        return "https" if self.secure else "http"

    @computed_field
    @property
    def endpoint(self) -> str:
        return f"{self.domain}:{self.s3_port}"

    @computed_field
    @property
    def endpoint_url(self) -> str:
        return f"{self.protocol}://{self.endpoint}"

    @computed_field
    @property
    def buckets(self) -> tuple[str, ...]:
        return (
            self.dvc_bucket,
            self.artifact_bucket,
            self.airflow_bucket,
        )

    @property
    def get_secret_key(self) -> str:
        return f"{self.secret_key.get_secret_value()}"

    def connection_string(
        self,
        bucket: Optional[str] = None,
    ) -> str:
        """
        Build MinIO URI.

        Example:
            minio://access:secret@localhost:9000/artifacts
        """

        bucket = bucket or self.artifact_bucket

        return (
            f"minio://"
            f"{self.access_key}:"
            f"{self.get_secret_key}@"
            f"{self.endpoint}/"
            f"{bucket}"
        )

    @computed_field
    @property
    def mlflow_artifact_uri(self) -> str:
        return self.endpoint_url

    @computed_field
    @property
    def mlflow_artifact_bucket(self) -> str:
        return f"s3://{self.artifact_bucket}"

    def _summary(self) -> None:
        """Print MinIO summary."""
        print("🗃️  MINIO:")
        print(f"   DOMAIN:          {self.domain}")
        print(f"   ACCESS KEY:      {self.access_key}")
        print(f"   SECRET KEY:      {'*' * len(self.get_secret_key)}")
        print("   PORTS:")
        print(f"     ├── S3 API:    {self.s3_port}")
        print(f"     └── Web UI:    {self.console_port}")
        print("   BUCKETS:")
        print(f"     ├── DVC:       {self.dvc_bucket}")
        print(f"     ├── Artifact:  {self.artifact_bucket}")
        print(f"     └── Airflow:   {self.airflow_bucket}")
        print()
