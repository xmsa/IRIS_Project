import json
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple, Union

import skops.io as sio
import yaml

from core import app_logger
from core.types import SkopsObjectType


class FileValidator:
    """Utility class for file validation operations."""

    @staticmethod
    def is_empty(filepath: Path) -> bool:
        return not filepath.exists() or filepath.stat().st_size == 0

    @staticmethod
    def get_size_mb(filepath: Path) -> float:
        return filepath.stat().st_size / (1024 * 1024) if filepath.exists() else 0.0

    @staticmethod
    def check_exists(exists: bool = True, allow_overwrite: bool = False):
        """Decorator to validate file existence before operations."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(filepath: Union[str, Path], *args, **kwargs) -> Any:
                path = Path(filepath) if isinstance(
                    filepath, str) else filepath
                overwrite = kwargs.get('overwrite', allow_overwrite)

                if overwrite:
                    return func(path, *args, **kwargs)

                if exists and not path.exists():
                    raise FileNotFoundError(f"File not found: {path}")
                if not exists and path.exists():
                    raise FileExistsError(f"File already exists: {path}")

                return func(path, *args, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def metadata_checker(metadata: Dict, config: Dict,  ordered_fields=['use_cols']) -> bool:
        def _compare_values(val1: Any, val2: Any, ignore_order: bool = True) -> bool:
            """Compare two values with optional order ignoring for lists."""

            if isinstance(val1, list) and isinstance(val2, list):
                if ignore_order:
                    try:
                        return set(val1) == set(val2)
                    except TypeError:
                        return sorted(val1, key=str) == sorted(val2, key=str)
                else:
                    return val1 == val2

            elif isinstance(val1, dict) and isinstance(val2, dict):
                return _compare_dicts(val1, val2)

            else:
                return val1 == val2

        def _compare_dicts(dict1: Dict, dict2: Dict) -> bool:
            """Recursively compare two dictionaries."""
            if set(dict1.keys()) != set(dict2.keys()):
                return False

            for key in dict1:
                if key in ordered_fields:
                    if not _compare_values(dict1[key], dict2[key], ignore_order=False):
                        return False
                else:
                    if not _compare_values(dict1[key], dict2[key], ignore_order=True):
                        return False
            return True

        return _compare_dicts(metadata, config)


class _BaseFileHandler:
    """Base class for common file operations."""

    _LOG_TEMPLATE = "{action} file {status}: {path}"

    @classmethod
    def _log_operation(cls, path: Path, action: str, status: str = "saved") -> None:
        app_logger.info(cls._LOG_TEMPLATE.format(
            action=action.capitalize(),
            status=status,
            path=path
        ))


@dataclass
class SkopsArtifact:
    obj: SkopsObjectType
    metadata: Optional[Dict] = None


class FileWriter(_BaseFileHandler):
    """Handles file writing operations with metadata support."""

    _WRITE_MODES: Dict[str, Tuple[str, str]] = {
        'json': ('w', 'utf-8'),
        'yaml': ('w', 'utf-8'),
    }

    @staticmethod
    @FileValidator.check_exists(exists=False, allow_overwrite=False)
    def skops(
        filepath: Path,
        skops_artifact: SkopsArtifact,
        overwrite: bool = False,
    ) -> None:

        sio.dump(skops_artifact.obj, filepath)
        FileWriter._log_operation(
            filepath, "model", "overwritten" if overwrite else "saved")

        if skops_artifact.metadata:
            FileWriter.metadata(
                filepath, metadata=skops_artifact.metadata,
                overwrite=overwrite)

    @staticmethod
    @FileValidator.check_exists(exists=False, allow_overwrite=False)
    def metadata(filepath: Path, metadata: Dict, overwrite: bool = False) -> None:
        meta_path: Path = filepath.with_suffix('.meta.json')
        FileWriter.json(meta_path, content=metadata, overwrite=overwrite)
        FileWriter._log_operation(
            filepath, "metadata", "overwritten" if overwrite else "saved")

    @staticmethod
    @FileValidator.check_exists(exists=False, allow_overwrite=False)
    def yaml(filepath: Path, content: Dict, overwrite: bool = False) -> None:
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(content, f, default_flow_style=False,
                      allow_unicode=True, sort_keys=False, indent=2)
        FileWriter._log_operation(
            filepath, "yaml", "overwritten" if overwrite else "saved")

    @staticmethod
    @FileValidator.check_exists(exists=False, allow_overwrite=False)
    def json(filepath: Path, content: Dict[str, Any], overwrite: bool = False, indent: int = 2) -> None:
        with filepath.open("w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=indent)
        FileWriter._log_operation(
            filepath, "json", "overwritten" if overwrite else "saved")


class FileReader(_BaseFileHandler):
    """Handles file reading operations with type hints."""

    @staticmethod
    @FileValidator.check_exists(exists=True)
    def skops(filepath: Path, metadata_config: Optional[Dict]) -> SkopsArtifact:
        obj: SkopsObjectType = sio.load(filepath)
        metadata_loaded: Optional[Dict] = FileReader.metadata(filepath)
        FileReader._log_operation(filepath, "skops object", "loaded")
        if metadata_loaded and metadata_config:
            result: bool = FileValidator.metadata_checker(
                metadata_loaded, metadata_config)
            if not result:
                raise Exception("Metadata and config is not Match")
        elif metadata_loaded is None and metadata_config:
            raise Exception("Cannot loaded Metadata")
        elif metadata_loaded and metadata_config is None:
            print("Metadata is not found and checking")

        skops_artifact: SkopsArtifact = SkopsArtifact(
            obj=obj,
            metadata=metadata_loaded
        )
        return skops_artifact

    @staticmethod
    @FileValidator.check_exists(exists=True)
    def metadata(filepath: Path) -> Optional[Dict]:
        meta_path: Path = filepath.with_suffix('.meta.json')
        try:
            return None if FileValidator.is_empty(meta_path) else FileReader.json(meta_path)
        except FileNotFoundError:
            return None

    @staticmethod
    @FileValidator.check_exists(exists=True)
    def yaml(filepath: Path) -> Dict:
        with open(filepath, 'r', encoding='utf-8') as f:
            content: Dict = yaml.safe_load(f)
            FileReader._log_operation(filepath, "yaml", "loaded")
            return content

    @staticmethod
    @FileValidator.check_exists(exists=True)
    def json(filepath: Path) -> Dict:
        with filepath.open("r", encoding="utf-8") as f:
            content: Dict = json.load(f)
            FileReader._log_operation(filepath, "json", "loaded")
            return content
