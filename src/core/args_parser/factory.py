from typing import Any, Dict

import click

from .api import ApiCommand
from .app import AppCommand
from .base import BaseCommand
from .data import DataCommand
from .minio import MinioCommand
from .storage import StorageCommand


class CLI:
    """Main CLI application factory"""

    def __init__(self):
        self.group = click.Group(name='cli')
        self.commands: Dict[str, BaseCommand] = {}
        self._register_commands()

    def _register_commands(self) -> None:
        """Register all commands"""
        commands: dict = {
            'app': AppCommand(),
            'api': ApiCommand(),
            'minio': MinioCommand(),
            'storage': StorageCommand(),
            'data': DataCommand(),
        }

        for name, command in commands.items():
            command.register(self.group)
            self.commands[name] = command

    def get_group(self) -> click.Group:
        """Return the CLI group"""
        return self.group

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        self.group()


cli = CLI()
