"""Folder business logic."""

from typing import Any

from ..infra import get_config
from ..infra.connections import IMAPAdapter


def folder_list(account_name: str) -> list[dict[str, Any]]:
    """List folders for an account."""
    config = get_config()
    account = config.get_account(account_name)

    adapter = IMAPAdapter(account)
    adapter.connect()
    try:
        return adapter.list_folders()
    finally:
        adapter.disconnect()
