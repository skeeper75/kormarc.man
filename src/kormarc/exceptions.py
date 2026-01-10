"""
KORMARC Parser Exception Classes

This module defines the exception hierarchy for KORMARC parsing errors.
"""

from typing import Any


class KORMARCError(Exception):
    """Base exception for all KORMARC-related errors."""

    def __init__(self, message: str, **context: Any) -> None:
        """Initialize KORMARC error with context information.

        Args:
            message: Error message
            **context: Additional context information (line, column, etc.)
        """
        self.message = message
        self.context = context
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation with context."""
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} ({context_str})"
        return self.message


class ParseError(KORMARCError):
    """Raised when parsing fails due to malformed input."""

    pass


class LeaderParseError(ParseError):
    """Raised when leader parsing fails."""

    pass


class FieldParseError(ParseError):
    """Raised when field parsing fails."""

    pass


class SubfieldParseError(ParseError):
    """Raised when subfield parsing fails."""

    pass


class ValidationError(KORMARCError):
    """Raised when data validation fails."""

    pass


class LeaderValidationError(ValidationError):
    """Raised when leader validation fails."""

    pass


class FieldValidationError(ValidationError):
    """Raised when field validation fails."""

    pass


class ConversionError(KORMARCError):
    """Raised when format conversion fails."""

    pass


class JSONConversionError(ConversionError):
    """Raised when JSON conversion fails."""

    pass


class XMLConversionError(ConversionError):
    """Raised when XML conversion fails."""

    pass


class EncodingError(KORMARCError):
    """Raised when encoding issues occur."""

    pass
