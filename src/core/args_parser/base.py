

from abc import ABC, abstractmethod
from typing import Any

import click

from core.settings import Settings, settings


class BaseCommand(ABC):
    """Base class for all CLI commands"""

    def __init__(self) -> None:
        self.settings: Settings = settings

    @abstractmethod
    def register(self, cli_group: click.Group) -> None:
        """Register command with the CLI group"""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> None:
        """Execute the command"""
        pass

    def _handle_summary(self, settings_obj: Any, title: str) -> None:
        """Handle summary display for any settings object"""
        if hasattr(settings_obj, '_summary'):
            click.echo(f"=== {title} Settings ===")
            settings_obj._summary()
        else:
            click.echo(f"⚠️  Summary not available for {title}")
