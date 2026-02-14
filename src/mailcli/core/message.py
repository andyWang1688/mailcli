"""Message business logic."""

from typing import Any

from ..infra import get_config
from ..infra.connections import IMAPAdapter, SMTPAdapter


def message_read(
    account_name: str, msg_id: str, folder: str = "INBOX"
) -> dict[str, Any]:
    """Read a message by ID."""
    config = get_config()
    account = config.get_account(account_name)

    adapter = IMAPAdapter(account)
    adapter.connect()
    try:
        message = adapter.read_message(msg_id, folder)
    finally:
        adapter.disconnect()

    return message


def message_send(account_name: str, to: str, subject: str, body: str) -> dict[str, Any]:
    """Send a simple text message."""
    config = get_config()
    account = config.get_account(account_name)

    adapter = SMTPAdapter(account)
    adapter.connect()
    try:
        result = adapter.send_message(to, subject, body)
    finally:
        adapter.disconnect()

    return result
