

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.enums import EnvironmentEnum

from .api import APISettings
from .base import ENV_PATH, Base
from .logger import LogsSettings
from .minio import MinIOSettings
from .mlflow import MlflowSettings
from .paths import PathsSettings
from .storage import StorageSettings


class Settings(Base):
    """
    Application global settings.

    This is the only entry point for configuration.
    """

    project_name: str = "Project Name"
    version: str = "0.1.0"
    python_version: str = "3.12"
    environment: EnvironmentEnum = EnvironmentEnum.DEVELOPMENT

    paths: PathsSettings = Field(default_factory=PathsSettings)
    minio: MinIOSettings = Field(default_factory=MinIOSettings)
    api: APISettings = Field(default_factory=APISettings)
    logger: LogsSettings = Field(default_factory=LogsSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    mlflow: MlflowSettings = Field(default_factory=MlflowSettings)

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
        case_sensitive=False,
    )

    def model_post_init(self, __context,) -> None:
        """
        Dependency injection.

        We connect settings together here.
        """
        self.api.static_dir = self.paths.web_dir/self.api.static_dir
        self.api.templates_dir = self.paths.web_dir/self.api.templates_dir
        if self.logger.dir is None:
            self.logger.dir = self.paths.logger_dir

        if self.storage.filepath is None:
            self.storage.filepath = self.paths.main_db

        if self.mlflow.filepath is None:
            self.mlflow.filepath = self.paths.mlflow_db
        if self.mlflow.artifact_uri is None:
            self.mlflow.artifact_uri = self.minio.endpoint_url
        if self.mlflow.s3_endpoint_url is None:
            self.mlflow.s3_endpoint_url = self.minio.mlflow_artifact_bucket

        self.paths.create_directories()
        self.paths.create_directories(
            [
                self.logger.dir
            ]
        )

    @property
    def header(self) -> str:
        header: str = (
            f"📊 {self.project_name} V{self.version} "
            f"(Python {self.python_version}, {self.environment.value})"
        )
        return header

    def summary(self) -> None:
        """Print a clean summary of all settings."""
        print(f"\n{'='*80}")
        print(f"{self.header:^80}")

        print(f"{'='*80}\n")

        self.paths._summary()
        self.minio._summary()
        self.api._summary()
        self.logger._summary()
        self.storage._summary()
        self.mlflow._summary()

        print(f"{'='*80}\n")


settings = Settings()
paths_settings: PathsSettings = settings.paths
minio_settings: MinIOSettings = settings.minio
api_settings: APISettings = settings.api
logger_settings: LogsSettings = settings.logger
storage_settings: StorageSettings = settings.storage
mlflow_settings: MlflowSettings = settings.mlflow
