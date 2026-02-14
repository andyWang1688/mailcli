"""Envelope business logic."""

from typing import Any

from ..infra import AccountConfig, get_config
from ..infra.connections import IMAPAdapter


def envelope_list(
    account_name: str, folder: str = "INBOX", limit: int = 50
) -> list[dict[str, Any]]:
    """List envelopes from a folder."""
    config = get_config()
    account = config.get_account(account_name)

    adapter = IMAPAdapter(account)
    adapter.connect()
    try:
        envelopes = adapter.list_envelopes(folder, limit)
    finally:
        adapter.disconnect()

    return envelopes


def envelope_search(
    account_name: str, query: str, folder: str = "INBOX"
) -> list[dict[str, Any]]:
    """Search envelopes by query."""
    config = get_config()
    account = config.get_account(account_name)

    adapter = IMAPAdapter(account)
    adapter.connect()
    try:
        envelopes = adapter.search_envelopes(query, folder)
    finally:
        adapter.disconnect()

    return envelopes
