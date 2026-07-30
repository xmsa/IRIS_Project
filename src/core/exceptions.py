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


class NotFitError(RuntimeError):
    def __init__(self, model_name="Model"):
        msg: str = f"{model_name} has not been fitted yet. Please call 'fit()' method first."
        super().__init__(msg)


class FittedError(RuntimeError):
    def __init__(self, model_name="Model"):
        msg: str = f"{model_name} has already been fitted. Cannot fit again."
        super().__init__(msg)


class CustomAttributeError(AttributeError):
    def __init__(self, attribute,  file):
        msg: str = f"Object of type {file} does not have '{attribute}' attribute"
        super().__init__(msg)


class NotSupportModelException(Exception):
    def __init__(self, model: str = "Model"):
        message: str = f"{model} format not supported"
        super().__init__(message.format(Model=model))
