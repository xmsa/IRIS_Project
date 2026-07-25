

from typing import Any, Dict, Optional

import click
import uvicorn

from core.enums import LogLevel

from .base import BaseCommand


class ApiCommand(BaseCommand):
    """Handle API command with Uvicorn"""

    def register(self, cli_group: click.Group) -> None:
        @cli_group.command()
        @click.option('--host', help='Host to bind (overrides default)')
        @click.option('--port', type=int, help='Port to bind (overrides default)')
        @click.option('--reload', is_flag=True, help='Enable auto-reload')
        @click.option('--no-reload', is_flag=True, help='Disable auto-reload')
        @click.option('--summary', is_flag=True, help='Show API settings summary')
        @click.option('--log-level', type=click.Choice(LogLevel, case_sensitive=False),
                      help='Set log level')
        @click.option('--run', is_flag=True, help='Run API')
        def api(run: bool, host: Optional[str], port: Optional[int],
                reload: bool, no_reload: bool, summary: bool,
                log_level: Optional[str]) -> None:
            self.execute(
                run=run,
                host=host,
                port=port,
                reload=reload,
                no_reload=no_reload,
                summary=summary,
                log_level=log_level
            )

    def execute(self, run: bool = False, host: Optional[str] = None,
                port: Optional[int] = None, reload: bool = False,
                no_reload: bool = False, summary: bool = False,
                log_level: Optional[str] = None) -> None:

        if summary:
            self._handle_summary(self.settings.api, "API")
            return

        if not run:
            click.echo("ℹ️  Use --run to start the API server")
            return

        config: dict = self._build_uvicorn_config(
            host, port, reload, no_reload, log_level)

        self._show_startup_info(config)

        uvicorn.run(**config)

    def _build_uvicorn_config(self, host: Optional[str], port: Optional[int],
                              reload: bool, no_reload: bool,
                              log_level: Optional[str]) -> Dict[str, Any]:
        """Build Uvicorn configuration from settings and CLI args"""
        config: dict = self.settings.api.uvicorn_config.copy()

        if host is not None:
            config["host"] = host

        if port is not None:
            config["port"] = port

        if no_reload:
            config["reload"] = False
        elif reload:
            config["reload"] = True

        if log_level is not None:
            config["log_level"] = log_level.lower()

        return config

    def _show_startup_info(self, config: Dict[str, Any]) -> None:
        """Display startup information"""
        click.echo(
            f"🚀 Starting API on http://{config['host']}:{config['port']}")
        if config.get("reload", False):
            click.echo("♻️  Auto-reload enabled")
        click.echo(f"📋 Log level: {config.get('log_level', 'info')}")
