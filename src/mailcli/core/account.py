"""Account commands."""

import re
from typing import Any

from ..infra import Config, get_config
from ..infra.config import get_config_path
from ..infra.connections import diagnose_account as do_diagnose


def account_list() -> list[dict[str, Any]]:
    """List all configured accounts."""
    config = get_config()
    accounts = []
    for name, account in config.accounts.items():
        accounts.append(
            {
                "name": name,
                "email": account.email,
                "imap": f"{account.imap_host}:{account.imap_port}",
                "smtp": f"{account.smtp_host}:{account.smtp_port}",
                "is_default": name == config.default_account,
            }
        )
    return accounts


def account_set_default(name: str) -> dict[str, Any]:
    """Set default account."""
    config = get_config()
    if name not in config.accounts:
        raise ValueError(f"Account '{name}' not found")

    config_path = get_config_path()
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found at {config_path}")

    raw = config_path.read_text(encoding="utf-8")
    replacement = f'default_account = "{name}"'
    if re.search(r"^\s*default_account\s*=.*$", raw, flags=re.MULTILINE):
        updated = re.sub(
            r"^\s*default_account\s*=.*$",
            replacement,
            raw,
            count=1,
            flags=re.MULTILINE,
        )
    else:
        updated = f"{replacement}\n\n{raw}"

    config_path.write_text(updated, encoding="utf-8")

    return {
        "status": "ok",
        "message": f"Default account set to '{name}'",
        "account": name,
    }


def diagnose_account(name: str) -> list[dict[str, Any]]:
    """Diagnose account connectivity."""
    config = get_config()
    if name not in config.accounts:
        raise ValueError(f"Account '{name}' not found")
    account = config.accounts[name]
    results = do_diagnose(account)
    return [result.to_dict() for result in results]
