from pathlib import Path
from typing import List, Optional

from pydantic import Field, computed_field

from .base import ROOT_DIR, Base


class PathsSettings(Base):
    """
    Centralized project paths.

    All paths are generated lazily from ROOT_DIR.
    """

    root_dir: Path = Field(
        default=ROOT_DIR,
        title="Project Root Directory",
        description=(
            "Root directory of the project. All other directories and file paths "
            "are resolved relative to this location."
        ),
        examples=["/home/user/project"],
    )

    web_dir_name: str = Field(
        default="web",
        title="web page and static file Directory Name",
        description="",
        examples=["web"],
    )

    logger_dir_name: str = Field(
        default="logs",
        title="",
        description="",
        examples=["logs"],
    )

    data_dir_name: str = Field(
        default="data",
        title="Data Directory Name",
        description="Name of the top-level directory used to store project datasets.",
        examples=["data"],
    )

    raw_dir_name: str = Field(
        default="raw",
        title="Raw Data Directory Name",
        description="Name of the directory containing original, unprocessed datasets.",
        examples=["raw"],
    )

    processed_dir_name: str = Field(
        default="processed",
        title="Processed Data Directory Name",
        description="Name of the directory used for processed and transformed datasets.",
        examples=["processed"],
    )

    config_dir_name: str = Field(
        default="configs",
        title="Configuration Directory Name",
        description="Name of the directory containing all project configuration files.",
        examples=["configs"],
    )

    model_config_dir_name: str = Field(
        default="models",
        title="Model Configuration Directory Name",
        description="Name of the directory containing machine learning model configuration files.",
        examples=["models"],
    )

    data_config_dir_name: str = Field(
        default="data",
        title="Data Configuration Directory Name",
        description="Name of the directory containing dataset and preprocessing configuration files.",
        examples=["data"],
    )

    report_dir_name: str = Field(
        default="reports",
        title="Reports Directory Name",
        description="Name of the directory used to store generated reports.",
        examples=["reports"],
    )

    gx_report_dir_name: str = Field(
        default="GX",
        title="Great Expectations Report Directory",
        description="Name of the directory containing Great Expectations validation reports.",
        examples=["GX"],
    )

    optuna_report_dir_name: str = Field(
        default="optuna",
        title="Optuna Report Directory",
        description="Name of the directory containing Optuna optimization reports.",
        examples=["optuna"],
    )

    storage_dir_name: str = Field(
        default="storage",
        title="Storage Directory Name",
        description="Name of the directory used to store databases and persistent application files.",
        examples=["storage"],
    )

    mlflow_db_name: str = Field(
        default="mlflow.db",
        title="MLflow Database Filename",
        description="Filename of the SQLite database used by MLflow.",
        examples=["mlflow.db"],
    )

    optuna_db_name: str = Field(
        default="optuna.db",
        title="Optuna Database Filename",
        description="Filename of the SQLite database used to persist Optuna studies.",
        examples=["optuna.db"],
    )

    main_db_name: str = Field(
        default="application.db",
        title="Application Database Filename",
        description="Filename of the primary SQLite database used by the application.",
        examples=["application.db"],
    )

    @computed_field
    @property
    def logger_dir(self) -> Path:
        return self.root_dir / self.logger_dir_name

    @computed_field
    @property
    def web_dir(self) -> Path:
        return self.root_dir / self.web_dir_name

    # ----- Data -----

    @computed_field
    @property
    def data_dir(self) -> Path:
        return self.root_dir / self.data_dir_name

    @computed_field
    @property
    def raw_data_dir(self) -> Path:
        return self.data_dir / self.raw_dir_name

    @computed_field
    @property
    def processed_data_dir(self) -> Path:
        return self.data_dir / self.processed_dir_name

    # ----- Configs -----
    @computed_field
    @property
    def configs_dir(self) -> Path:
        return self.root_dir / self.config_dir_name

    @computed_field
    @property
    def models_config_dir(self) -> Path:
        return self.configs_dir / self.model_config_dir_name

    @computed_field
    @property
    def data_config_dir(self) -> Path:
        return self.configs_dir / self.data_config_dir_name

    # ----- Reports -----

    @computed_field
    @property
    def reports_dir(self) -> Path:
        return self.root_dir / self.report_dir_name

    @computed_field
    @property
    def gx_reports_dir(self) -> Path:
        return self.reports_dir / self.gx_report_dir_name

    @computed_field
    @property
    def optuna_reports_dir(self) -> Path:
        return self.reports_dir / self.optuna_report_dir_name

    # ----- Storage -----
    @computed_field
    @property
    def storage_dir(self) -> Path:
        return self.root_dir / self.storage_dir_name

    @computed_field
    @property
    def mlflow_db(self) -> Path:
        return self.storage_dir / self.mlflow_db_name

    @computed_field
    @property
    def optuna_db(self) -> Path:
        return self.storage_dir / self.optuna_db_name

    @computed_field
    @property
    def main_db(self) -> Path:
        return self.storage_dir / self.main_db_name

    # ----- Helpers -----

    @property
    def directories(self) -> List[Path]:
        return [
            self.logger_dir,
            self.web_dir,
            self.data_dir,
            self.raw_data_dir,
            self.processed_data_dir,
            self.configs_dir,
            self.models_config_dir,
            self.data_config_dir,
            self.reports_dir,
            self.gx_reports_dir,
            self.optuna_reports_dir,
            self.storage_dir,
        ]

    def create_directories(self, dirs: Optional[List[Path]] = None) -> None:
        if dirs is None:
            dirs = self.directories
        for directory in dirs:
            directory.mkdir(parents=True, exist_ok=True)

    def ensure_files(self) -> None:
        for file in (
            self.mlflow_db,
            self.optuna_db,
            self.main_db
        ):
            file.parent.mkdir(parents=True, exist_ok=True)
            file.touch(exist_ok=True)

    def _summary(self) -> None:
        """Print paths summary."""
        print("📁 PATHS:")
        print(f"  ROOT:                   {self.root_dir}/")
        print(f"    ├── LOGGER (default): {self.logger_dir_name}/")
        print(f"    ├── WEB:              {self.web_dir_name}/")
        print(f"    ├── DATA:             {self.data_dir_name}/")
        print(f"    │     ├── PROCESSED:  {self.processed_dir_name}/")
        print(f"    │     └── RAW:        {self.raw_dir_name}/")
        print(f"    ├── DATABASES:        {self.storage_dir_name}/")
        print(f"    │     ├── Mlflow:     {self.mlflow_db_name}")
        print(f"    │     ├── Optuna:     {self.optuna_db_name}")
        print(f"    │     └── Main:       {self.main_db_name}")
        print(f"    ├── CONFIGS:          {self.config_dir_name}/")
        print(f"    │     ├── MODELS:     {self.model_config_dir_name}/")
        print(f"    │     └── DATA:       {self.data_config_dir_name}/")
        print(f"    └── REPORTS:          {self.report_dir_name}/")
        print(f"          ├── GX:         {self.gx_report_dir_name}/")
        print(f"          └── Optuna:     {self.optuna_report_dir_name}/")
        print()
