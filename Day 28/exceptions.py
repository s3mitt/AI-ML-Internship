"""Custom domain exceptions for Smart Notes CLI."""


class NoteError(Exception):
    """Base exception for all note-related errors."""
    pass


class NoteNotFoundError(NoteError):
    """Raised when a requested note ID is not found in storage."""
    pass


class ValidationError(NoteError):
    """Raised when user input fails validation constraints."""
    pass
