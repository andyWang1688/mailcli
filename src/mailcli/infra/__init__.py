"""Infrastructure layer."""

from .config import AccountConfig, Config, get_config
from .connections import IMAPAdapter, SMTPAdapter, diagnose_account
from .errors import (
    AuthenticationError,
    ConfigError,
    ConnectionError,
    ErrorResponse,
    MailCliError,
    TimeoutError,
)
from .output import OutputFormatter

__all__ = [
    "Config",
    "get_config",
    "OutputFormatter",
    "AuthenticationError",
    "ConfigError",
    "ConnectionError",
    "ErrorResponse",
    "MailCliError",
    "TimeoutError",
    "AccountConfig",
    "IMAPAdapter",
    "SMTPAdapter",
    "diagnose_account",
]
