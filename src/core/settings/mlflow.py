from pathlib import Path
from typing import Optional

from pydantic import computed_field

from .base import Base


class MlflowSettings(Base):
    filepath: Optional[Path] = None
    host: str = "localhost"
    port: int = 5000
    experiment_name: str = "Mlflow Experiment"
    optuna_experiment_name: str = "Optuna Study"

    s3_endpoint_url: Optional[str] = None
    artifact_uri: Optional[str] = None

    @computed_field
    @property
    def url(self) -> str:
        """Get MLflow server URL"""
        return f"http://{self.host}:{self.port}"

    @computed_field
    @property
    def tracking_uri(self) -> str:
        """
        SQLite database connection URI.
        Example:
            sqlite:///storage/mlflow.db
        """
        if self.filepath is None:
            raise ValueError("filepath must be set to generate tracking_uri")
        return f"sqlite:///{self.filepath}"

    def _summary(self) -> None:
        """Print MLflow settings summary"""
        print("🎯 MLflow Settings:")
        print(f"  URL: {self.url}")
        print(f"  TRACKING_URI: {self.tracking_uri}")
        print(f"  Storage file: {self.filepath}")
        print(f"  Experiment name: {self.experiment_name}")
        print(f"  Optuna experiment name: {self.optuna_experiment_name}")
        print(f"  S3 Endpoint URL: {self.s3_endpoint_url}")
        print(f"  Artifact URI: {self.artifact_uri}")
        print()
