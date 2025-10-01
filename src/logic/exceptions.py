"""Custom exceptions for TXM ToolBox."""


class TXMError(Exception):
    """Base exception for TXM ToolBox errors."""
    pass


class FileLoadError(TXMError):
    """Raised when file loading fails."""
    pass


class DataProcessingError(TXMError):
    """Raised when data processing fails."""
    pass


class InvalidDataError(TXMError):
    """Raised when data validation fails."""
    pass
