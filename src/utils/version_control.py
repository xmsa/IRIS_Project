import hashlib
import json
import subprocess
from _hashlib import HASH
from pathlib import Path
from typing import Optional


class VersionControl:
    """Utility class for Git and DVC version management."""

    @staticmethod
    def git_commit_id(short: bool = False) -> Optional[str]:
        """Get current Git commit hash."""
        try:
            cmd: list[str] = ["git", "rev-parse", "HEAD"]
            if short:
                cmd.insert(2, "--short")
            return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    @staticmethod
    def database_hash_with_dvc(
        filepath: Path,
        use_dvc_cache: bool = True,
        short: bool = False,
    ) -> Optional[str]:
        """
        Get file hash from DVC cache if available, otherwise compute directly.

        Args:
            filepath: Path to the file
            dvc_filepath: Optional custom path to .dvc file
            use_dvc_cache: If True, try to read from DVC .dvc file first

        Returns:
            Hash as string, or None if error
        """
        # Try to get hash from .dvc file if requested
        if use_dvc_cache:
            dvc_hash: Optional[str] = VersionControl._hash_from_dvc_file(
                filepath)
            if dvc_hash:
                return dvc_hash

        # Fallback: compute hash directly
        dvc_hash = VersionControl._hash_from_file(filepath)
        if short and dvc_hash:
            return dvc_hash[:8]
        return dvc_hash

    @staticmethod
    def _hash_from_dvc_file(filepath: Path) -> Optional[str]:
        """
        Extract hash from .dvc file.

        The .dvc file contains the MD5 hash of the tracked file in 'outs' section.
        """
        try:
            # Determine the .dvc file path
            # Default: same name as file with .dvc extension
            filepath_obj = Path(filepath)
            dvc_path: Path = filepath_obj.parent / f"{filepath_obj.name}.dvc"

            if not dvc_path.exists():
                return None

            # Read and parse .dvc file
            with dvc_path.open('r', encoding='utf-8') as f:
                data: dict = json.load(f)

            # The hash is in 'outs' section
            for out in data.get('outs', []):
                # Check if this output matches our file
                out_path = out.get('path', '')
                if out_path == Path(filepath).name or out_path == str(Path(filepath)):
                    # Return MD5 hash (or other hash types)
                    return out.get('md5') or out.get('hash')

            return None

        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            return None

    @staticmethod
    def _hash_from_file(filepath: Path) -> Optional[str]:
        """Compute SHA256 hash of a file directly."""
        try:
            filepath_obj = Path(filepath)
            if not filepath_obj.exists():
                return None

            sha256: HASH = hashlib.sha256()
            with open(filepath_obj, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()

        except (FileNotFoundError, IOError):
            return None

    @staticmethod
    def is_dvc_tracked(filepath: Path) -> bool:
        """Check if a file is tracked by DVC."""
        return VersionControl._hash_from_dvc_file(filepath) is not None

    @staticmethod
    def get_dvc_info(filepath: Path) -> dict:
        """
        Get complete DVC information for a file.

        Returns:
            dict with keys: 'hash', 'tracked', 'dvc_filepath', 'size'
        """
        dvc_path: Path = filepath.parent / f"{filepath.name}.dvc"

        info: dict = {
            'hash': VersionControl.database_hash_with_dvc(filepath),
            'tracked': False,
            'dvc_filepath': str(dvc_path) if dvc_path.exists() else None,
            'size': filepath.stat().st_size if filepath.exists() else None,
            'file_exists': filepath.exists()
        }

        # Check if tracked by DVC
        if info['hash']:
            # Check if hash came from .dvc file
            dvc_hash: Optional[str] = VersionControl._hash_from_dvc_file(
                filepath)
            if dvc_hash:
                info['tracked'] = True
                info['dvc_hash'] = dvc_hash

        return info
