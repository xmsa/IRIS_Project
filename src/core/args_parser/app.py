

import click

from .base import BaseCommand


class AppCommand(BaseCommand):
    """Handle app command"""

    def register(self, cli_group: click.Group) -> None:
        @cli_group.command()
        @click.option('--summary', is_flag=True, help='Show application settings summary')
        def app(summary: bool) -> None:
            self.execute(summary=summary)

    def execute(self, summary: bool = False) -> None:
        if summary:
            self.settings.summary()
        else:
            click.echo("Running main application...")
