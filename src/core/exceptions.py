class VersionControlError(Exception):
    """Base exception for version control utilities."""


class GitError(VersionControlError):
    """Git operation failed."""


class HashCalculationError(VersionControlError):
    """Unable to calculate file hash."""


class DVCError(VersionControlError):
    """Unable to read DVC metadata."""


class DatasetHashMismatchError(Exception):
    """Raised when the dataset hash does not match the expected hash."""
