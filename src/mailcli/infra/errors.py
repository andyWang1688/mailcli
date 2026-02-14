"""Error handling."""

from __future__ import annotations

from dataclasses import dataclass


class MailCliError(Exception):
    """Base exception for mailcli errors."""

    pass


class ConfigError(MailCliError):
    """Configuration related errors."""

    pass


class AuthenticationError(MailCliError):
    """Authentication failed."""

    pass


class ConnectionError(MailCliError):
    """Connection related errors."""

    pass


class TimeoutError(MailCliError):
    """Timeout errors."""

    pass


@dataclass
class ErrorResponse:
    """Standard error response structure."""

    error_type: str
    message: str
    details: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "error": self.error_type,
            "message": self.message,
            "details": self.details,
        }
