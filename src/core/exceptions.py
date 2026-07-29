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


class NotSupportFormatException(Exception):
    """
    Exception raised when the dataset format is not supported or path is invalid.
    """

    def __init__(self, message: str = "Dataset format not supported or path is invalid") -> None:
        self.message: str = message
        super().__init__(self.message)
