from functools import wraps
from pathlib import Path
from typing import Dict

import yaml

from core import app_logger


class FileValidator:
    @staticmethod
    def is_empty(filepath: Path) -> bool:
        if not filepath.exists():
            return True
        return filepath.stat().st_size == 0

    @staticmethod
    def get_size_mb(filepath: Path) -> float:
        if not filepath.exists():
            return 0.0
        return filepath.stat().st_size / (1024 * 1024)

    @staticmethod
    def check_exists_file(exists: bool, allow_overwrite: bool = False):
        def decorator(func):
            @wraps(func)
            def wrapper(filepath, *args, **kwargs):
                overwrite = kwargs.get('overwrite', allow_overwrite)
                if overwrite:
                    return func(filepath, *args, **kwargs)
                if exists and not filepath.exists():
                    raise FileNotFoundError(f"File not found: {filepath}")
                elif not exists and filepath.exists():
                    raise FileExistsError(f"File already exists: {filepath}")
                return func(filepath, *args, **kwargs)
            return wrapper
        return decorator


def convert_str2path(func):
    @wraps(func)
    def wrapper(filepath, *args, **kwargs):
        if isinstance(filepath, str):
            filepath = Path(filepath)
        return func(filepath, *args, **kwargs)
    return wrapper


class FileWriter:
    @staticmethod
    @convert_str2path
    @FileValidator.check_exists_file(exists=False, allow_overwrite=False)
    def yaml(filepath: Path, content: Dict, overwrite: bool = False) -> None:
        with open(filepath, "w") as f:
            yaml.dump(
                content, f, default_flow_style=False,
                allow_unicode=True, sort_keys=False,
                indent=2
            )

        status: str = "overwritten" if overwrite else "saved"
        app_logger.info(f"Json file {status}: {filepath}")


class FileReader:
    @staticmethod
    @convert_str2path
    @FileValidator.check_exists_file(exists=True)
    def yaml(filepath: Path) -> Dict:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = yaml.safe_load(f)
            app_logger.info(f"Yaml file loaded: {filepath}")

        return content
