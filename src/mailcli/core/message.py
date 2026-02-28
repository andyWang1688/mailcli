"""Message business logic."""

from __future__ import annotations

from email.message import EmailMessage
from pathlib import Path
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


def message_write(
    to: str,
    subject: str,
    body: str,
    output_path: str,
    cc: str | None = None,
) -> dict[str, Any]:
    """Write a local draft message to .eml file."""
    msg = EmailMessage()
    msg["To"] = to
    if cc:
        msg["Cc"] = cc
    msg["Subject"] = subject
    msg.set_content(body)

    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(msg.as_bytes())

    return {
        "status": "ok",
        "action": "write",
        "path": str(target),
        "size": target.stat().st_size,
    }


def message_export(
    account_name: str,
    msg_id: str,
    output_path: str,
    folder: str = "INBOX",
) -> dict[str, Any]:
    """Export a remote message to local .eml file."""
    config = get_config()
    account = config.get_account(account_name)

    target = Path(output_path)
    if target.is_dir() or output_path.endswith("/"):
        target = target / f"message-{msg_id}.eml"
    if target.suffix.lower() != ".eml":
        target = target.with_suffix(".eml")
    target.parent.mkdir(parents=True, exist_ok=True)

    adapter = IMAPAdapter(account)
    adapter.connect()
    try:
        raw_email = adapter.fetch_message_raw(msg_id, folder)
    finally:
        adapter.disconnect()

    target.write_bytes(raw_email)
    return {
        "status": "ok",
        "action": "export",
        "id": msg_id,
        "folder": folder,
        "path": str(target),
        "size": target.stat().st_size,
    }


def message_reply(
    account_name: str,
    msg_id: str,
    body: str,
    folder: str = "INBOX",
    reply_all: bool = False,
) -> dict[str, Any]:
    """Reply to a message by ID."""
    original = message_read(account_name, msg_id, folder)

    recipient = original.get("from", "")
    subject = _prefixed_subject("Re:", str(original.get("subject", "")))
    quoted = _quoted_original(original)
    full_body = f"{body}\n\n{quoted}" if body else quoted

    cc = original.get("cc") if reply_all else None
    return message_send_with_cc(account_name, recipient, subject, full_body, cc)


def message_forward(
    account_name: str,
    msg_id: str,
    to: str,
    body: str,
    folder: str = "INBOX",
) -> dict[str, Any]:
    """Forward a message by ID."""
    original = message_read(account_name, msg_id, folder)
    subject = _prefixed_subject("Fwd:", str(original.get("subject", "")))
    quoted = _quoted_original(original)
    full_body = f"{body}\n\n{quoted}" if body else quoted
    return message_send(account_name, to, subject, full_body)


def message_copy(
    account_name: str,
    msg_id: str,
    destination_folder: str,
    source_folder: str = "INBOX",
) -> dict[str, Any]:
    """Copy message between folders."""
    config = get_config()
    account = config.get_account(account_name)

    adapter = IMAPAdapter(account)
    adapter.connect()
    try:
        return adapter.copy_message(msg_id, destination_folder, source_folder)
    finally:
        adapter.disconnect()


def message_move(
    account_name: str,
    msg_id: str,
    destination_folder: str,
    source_folder: str = "INBOX",
) -> dict[str, Any]:
    """Move message between folders."""
    config = get_config()
    account = config.get_account(account_name)

    adapter = IMAPAdapter(account)
    adapter.connect()
    try:
        return adapter.move_message(msg_id, destination_folder, source_folder)
    finally:
        adapter.disconnect()


def message_delete(
    account_name: str,
    msg_id: str,
    folder: str = "INBOX",
    expunge: bool = True,
) -> dict[str, Any]:
    """Delete message in folder."""
    config = get_config()
    account = config.get_account(account_name)

    adapter = IMAPAdapter(account)
    adapter.connect()
    try:
        return adapter.delete_message(msg_id, folder, expunge=expunge)
    finally:
        adapter.disconnect()


def message_send_with_cc(
    account_name: str,
    to: str,
    subject: str,
    body: str,
    cc: str | None = None,
) -> dict[str, Any]:
    """Send message with optional cc."""
    config = get_config()
    account = config.get_account(account_name)

    adapter = SMTPAdapter(account)
    adapter.connect()
    try:
        return adapter.send_message(to, subject, body, cc=cc)
    finally:
        adapter.disconnect()


def _prefixed_subject(prefix: str, subject: str) -> str:
    """Build subject with prefix while avoiding duplicate prefix."""
    lowered = subject.lower().strip()
    if lowered.startswith(prefix.lower()):
        return subject
    return f"{prefix} {subject}".strip()


def _quoted_original(message: dict[str, Any]) -> str:
    """Build quoted text block for reply/forward."""
    date = str(message.get("date", "")).strip() or "unknown date"
    sender = str(message.get("from", "")).strip() or "unknown sender"
    body = str(message.get("body", "")).replace("\r\n", "\n")
    quoted_lines = [f"> {line}" for line in body.split("\n")]
    quoted_text = "\n".join(quoted_lines)
    return f"On {date}, {sender} wrote:\n{quoted_text}".strip()
