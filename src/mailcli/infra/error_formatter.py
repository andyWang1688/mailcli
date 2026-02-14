"""Error handling improvements for CLI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ErrorResponse:
    """Standard error response structure."""

    error_type: str
    message: str
    details: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "error": self.error_type,
            "message": self.message,
            "details": self.details,
        }


def format_error(error_type: str, message: str, details: Optional[str] = None) -> str:
    """Format error message for CLI output."""
    return f"Error: {message}"


def format_error_json(
    error_type: str, message: str, details: Optional[str] = None
) -> dict:
    """Format error as JSON for CLI output."""
    return ErrorResponse(
        error_type=error_type, message=message, details=details
    ).to_dict()
