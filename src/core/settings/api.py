from pathlib import Path

from pydantic import Field

from .base import Base


class APISettings(Base):
    """Manages FastAPI application settings."""

    name: str = Field(
        default="IRIS Predictor",
        title="Application Name",
        description="Display name of the FastAPI application.",
        examples=["IRIS Predictor", "Customer Churn API"],
    )

    host: str = Field(
        default="localhost",
        title="Host Address",
        description="Hostname or IP address on which the FastAPI application listens.",
        examples=["localhost", "0.0.0.0"],
    )

    port: int = Field(
        default=8000,
        ge=1024,
        le=65535,
        title="Application Port",
        description="Network port used by the FastAPI application.",
        examples=[8000, 8080],
    )

    debug: bool = Field(
        default=True,
        title="Debug Mode",
        description="Enables debug mode to provide detailed error information during development.",
        examples=[True],
    )

    reload: bool = Field(
        default=True,
        title="Auto Reload",
        description="Automatically reloads the application when source files are modified.",
        examples=[True],
    )

    offline_mode: bool = Field(
        default=False,
        title="Offline Mode",
        description="Runs the application without relying on external services or network resources.",
        examples=[False],
    )

    log_level: str = Field(
        default="info",
        title="Logging Level",
        description="Minimum logging severity level used by the application server.",
        examples=["info", "warning", "error", "debug"],
    )

    static_dir: Path = Field(
        default=Path("static"),
        title="Static Files Directory",
        description="Directory containing static assets such as CSS, JavaScript, and images.",
        examples=["static"],
    )

    templates_dir: Path = Field(
        default=Path("template"),
        title="Templates Directory",
        description="Directory containing HTML templates rendered by the application.",
        examples=["templates"],
    )

    @property
    def uvicorn_config(self) -> dict:
        """Return the Uvicorn server configuration."""
        return {
            "app": "api:app",
            "host": self.host,
            "port": self.port,
            "reload": self.reload,
            "log_level": self.log_level.lower(),
            "access_log": self.debug,
        }

    @property
    def url(self) -> str:
        """Return the application base URL."""
        return f"http://{self.host}:{self.port}"

    def _summary(self) -> None:
        """Print API configuration summary."""
        print("🚀 API:")
        print(f"   NAME:                  {self.name}")
        print(f"   URL:                   {self.url}")
        print(f"   DEBUG:                 {self.debug}")
        print(f"   RELOAD:                {self.reload}")
        print(f"   OFFLINE MODE:          {self.offline_mode}")
        print(f"   LOG LEVEL:             {self.log_level.upper()}")
        print("   Web file:")
        print(f"     ├── STATIC DIR:      {self.static_dir}")
        print(f"     └── TEMPLATES DIR:   {self.templates_dir}")
        print()
