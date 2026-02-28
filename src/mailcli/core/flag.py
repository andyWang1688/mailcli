"""Flag business logic."""

from __future__ import annotations

from typing import Any

from ..infra import get_config
from ..infra.connections import IMAPAdapter


def flag_add(
    account_name: str, msg_id: str, flag: str, folder: str = "INBOX"
) -> dict[str, Any]:
    """Add one IMAP flag to a message."""
    config = get_config()
    account = config.get_account(account_name)

    adapter = IMAPAdapter(account)
    adapter.connect()
    try:
        return adapter.update_flags(msg_id, [flag], action="add", folder=folder)
    finally:
        adapter.disconnect()


def flag_remove(
    account_name: str,
    msg_id: str,
    flag: str,
    folder: str = "INBOX",
) -> dict[str, Any]:
    """Remove one IMAP flag from a message."""
    config = get_config()
    account = config.get_account(account_name)

    adapter = IMAPAdapter(account)
    adapter.connect()
    try:
        return adapter.update_flags(msg_id, [flag], action="remove", folder=folder)
    finally:
        adapter.disconnect()
