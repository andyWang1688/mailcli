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


def folder_create(account_name: str, name: str) -> dict[str, Any]:
    """Create a folder for an account."""
    config = get_config()
    account = config.get_account(account_name)

    adapter = IMAPAdapter(account)
    adapter.connect()
    try:
        return adapter.create_folder(name)
    finally:
        adapter.disconnect()


def folder_delete(account_name: str, name: str) -> dict[str, Any]:
    """Delete a folder for an account."""
    config = get_config()
    account = config.get_account(account_name)

    adapter = IMAPAdapter(account)
    adapter.connect()
    try:
        return adapter.delete_folder(name)
    finally:
        adapter.disconnect()


def folder_expunge(account_name: str, name: str = "INBOX") -> dict[str, Any]:
    """Expunge deleted messages from a folder."""
    config = get_config()
    account = config.get_account(account_name)

    adapter = IMAPAdapter(account)
    adapter.connect()
    try:
        return adapter.expunge_folder(name, purge=False)
    finally:
        adapter.disconnect()


def folder_purge(account_name: str, name: str = "INBOX") -> dict[str, Any]:
    """Purge all messages from a folder."""
    config = get_config()
    account = config.get_account(account_name)

    adapter = IMAPAdapter(account)
    adapter.connect()
    try:
        return adapter.expunge_folder(name, purge=True)
    finally:
        adapter.disconnect()
