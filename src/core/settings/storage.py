from pathlib import Path
from typing import Optional

from pydantic import computed_field

from .base import Base


class StorageSettings(Base):
    filepath: Optional[Path] = None

    @computed_field
    @property
    def URL(self) -> str:
        """
        SQLite database connection URI.
        Example:
            sqlite:///storage/application.db
        """
        return f"sqlite:///{self.filepath}"

    def _summary(self) -> None:
        print("🎯 Database:")
        print(f"  URI:          {self.URL}")
        print(f"  Storage file: {self.filepath}")
        print()
