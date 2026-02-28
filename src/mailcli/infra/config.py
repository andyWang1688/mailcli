"""Configuration management."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ImportError:
    import tomli as tomllib


@dataclass
class AccountConfig:
    """Account configuration."""

    name: str
    email: str
    imap_host: str
    imap_port: int
    smtp_host: str
    smtp_port: int
    auth_raw: str | None = None
    auth_cmd: str | None = None
    use_ssl: bool = True


@dataclass
class Config:
    """Main configuration."""

    accounts: dict[str, AccountConfig]
    default_account: str | None = None
    quirks: dict[str, Any] | None = None

    def get_account(self, name: str | None = None) -> AccountConfig:
        """Get account by name or default."""
        if name is None:
            name = self.default_account
        if name not in self.accounts:
            raise ValueError(f"Account '{name}' not found")
        return self.accounts[name]


def get_config() -> Config:
    """Load configuration from default path."""
    config_path = get_config_path()

    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found at {config_path}\n"
            f"Please create it or copy from config/config.example.toml"
        )

    try:
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
    except Exception as e:
        raise ValueError(f"Failed to load configuration: {e}")

    accounts = {}
    for name, acc in data.get("accounts", {}).items():
        auth_cfg = acc.get("auth", {})
        accounts[name] = AccountConfig(
            name=name,
            email=acc["email"],
            imap_host=acc["imap"]["host"],
            imap_port=acc["imap"]["port"],
            smtp_host=acc["smtp"]["host"],
            smtp_port=acc["smtp"]["port"],
            auth_raw=auth_cfg.get("raw"),
            auth_cmd=auth_cfg.get("cmd"),
            use_ssl=acc.get("use_ssl", True),
        )

    return Config(
        accounts=accounts,
        default_account=data.get("default_account"),
        quirks=data.get("quirks"),
    )


def get_config_path() -> Path:
    """Return default config file path."""
    return Path.home() / ".config" / "mailcli" / "config.toml"
