from pathlib import Path
from typing import Any, Dict

from pydantic import BaseModel

from utils.file_handler import FileReader, FileValidator, FileWriter


class BaseConfigModel(BaseModel):
    @classmethod
    def from_dict(cls, data: Dict) -> Any:
        return cls(**data)

    @classmethod
    def from_yaml(cls, filepath: Path) -> Any:
        if FileValidator.is_empty(filepath=filepath):
            return cls()

        config: Dict = FileReader.yaml(filepath)
        return cls(**config)

    def to_yaml(self, filepath:  Path) -> None:
        FileWriter.yaml(filepath, self.model_dump())
