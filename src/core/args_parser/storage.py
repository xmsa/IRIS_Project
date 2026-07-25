

from typing import Optional

import click

from .base import BaseCommand


class StorageCommand(BaseCommand):
    """Handle storage operations"""

    def register(self, cli_group: click.Group) -> None:
        @cli_group.command()
        @click.option('--summary', is_flag=True, help='Show storage settings summary')
        def storage(summary: bool, list_files: bool, path: str,
                    upload: Optional[str], download: Optional[str],
                    delete_file: Optional[str]) -> None:
            self.execute(
                summary=summary,
            )

    def execute(
        self,
            summary: bool = False
    ) -> None:

        if summary:
            self._handle_summary(self.settings.storage, "Storage")
            return
