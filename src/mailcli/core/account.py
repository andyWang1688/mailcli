"""Account commands."""

from typing import Any

from ..infra import Config, get_config
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
