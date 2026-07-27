import hashlib
import subprocess
from _hashlib import HASH
from pathlib import Path
from typing import Dict, Optional

from core.exceptions import DVCError, GitError, HashCalculationError


class VersionControl:
    """Utility class for Git and DVC version management."""

    @staticmethod
    def git_commit_id(short: bool = False) -> str:
        """Return current Git commit hash."""

        cmd: list[str] = ["git", "rev-parse"]

        if short:
            cmd.append("--short")

        cmd.append("HEAD")

        try:
            result: subprocess.CompletedProcess[str] = subprocess.run(
                cmd, capture_output=True,
                text=True, check=True,
            )
        except FileNotFoundError as exc:
            raise GitError("Git executable was not found.") from exc

        except subprocess.CalledProcessError as exc:
            raise GitError(
                "Current directory is not a Git repository.") from exc

        return result.stdout.strip()

    @staticmethod
    def database_hash_with_dvc(
        filepath: Path,
        use_dvc_cache: bool = True,
        short: bool = False,
    ) -> str:
        """
        Get file hash from DVC cache if available, otherwise compute directly.

        Args:
            filepath: Path to the file
            dvc_filepath: Optional custom path to .dvc file
            use_dvc_cache: If True, try to read from DVC .dvc file first

        Returns:
            Hash as string, or None if error
        """
        if use_dvc_cache:
            dvc_hash: Optional[str] = VersionControl._hash_from_dvc_file(
                filepath)

            if dvc_hash:
                return dvc_hash[:8] if short else dvc_hash

        file_hash: Optional[str] = VersionControl._hash_from_file(filepath)

        if file_hash is None:
            raise FileNotFoundError(
                f"File '{filepath}' does not exist."
            )

        return file_hash[:8] if short else file_hash

    @staticmethod
    def _hash_from_dvc_file(filepath: Path) -> Optional[str]:
        """
        Extract hash from .dvc file.

        The .dvc file contains the MD5 hash of the tracked file in 'outs' section.
        """
        dvc_path: Path = filepath.with_suffix(filepath.suffix + ".dvc")

        if dvc_path.exists():
            try:
                from .file_handler import FileReader
                data: Dict = FileReader.yaml(dvc_path)

            except OSError as exc:
                raise DVCError(f"Cannot read '{dvc_path}'.") from exc

            for out in data.get("outs", []):
                if out.get("path") in (filepath.name, str(filepath)):
                    return out.get("md5") or out.get("hash")

        return None

    @staticmethod
    def _hash_from_file(filepath: Path) -> Optional[str]:
        """Compute md5 hash of a file directly."""

        if filepath.exists():
            try:
                sha256: HASH = hashlib.md5()

                with filepath.open("rb") as f:
                    for chunk in iter(lambda: f.read(8192), b""):
                        sha256.update(chunk)

                return sha256.hexdigest()

            except OSError as exc:
                raise HashCalculationError(
                    f"Unable to read file '{filepath}'."
                ) from exc
        return None

    @staticmethod
    def is_dvc_tracked(filepath: Path) -> bool:
        """Check if a file is tracked by DVC."""
        return VersionControl._hash_from_dvc_file(filepath) is not None

    @staticmethod
    def get_dvc_info(filepath: Path) -> Dict:
        """
        Get complete DVC information for a file.

        Returns:
            dict with keys: 'hash', 'tracked', 'dvc_filepath', 'size'
        """
        dvc_path: Path = filepath.parent / f"{filepath.name}.dvc"
        dvc_hash: Optional[str] = VersionControl._hash_from_dvc_file(filepath)

        info: Dict = {
            "hash": dvc_hash or VersionControl._hash_from_file(filepath),
            "tracked": dvc_hash is not None,
            "dvc_hash": dvc_hash,
            "dvc_filepath": str(dvc_path) if dvc_path.exists() else None,
            "size": filepath.stat().st_size if filepath.exists() else None,
            "file_exists": filepath.exists(),
        }

        return info
