"""Attachment business logic."""

from pathlib import Path
from typing import Any

from ..infra import get_config
from ..infra.connections import IMAPAdapter


def attachment_list(
    account_name: str, msg_id: str, folder: str = "INBOX"
) -> list[dict[str, Any]]:
    """List attachments from a message."""
    config = get_config()
    account = config.get_account(account_name)

    adapter = IMAPAdapter(account)
    adapter.connect()
    try:
        attachments = adapter.get_attachments(msg_id, folder)
    finally:
        adapter.disconnect()

    return attachments


def attachment_download(
    account_name: str,
    msg_id: str,
    filename: str,
    output_dir: str,
    folder: str = "INBOX",
) -> dict[str, Any]:
    """Download an attachment."""
    import email
    import imaplib
    import smtplib

    config = get_config()
    account = config.get_account(account_name)

    adapter = IMAPAdapter(account)
    adapter.connect()

    try:
        adapter.select_folder(folder)
        typ, data = adapter.connection.fetch(msg_id, "(RFC822)")

        if typ != "OK":
            raise ConnectionError(f"Failed to fetch message {msg_id}")

        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        file_path = output_path / filename

        found = False
        for part in msg.walk():
            content_disposition = str(part.get("Content-Disposition", ""))

            if "attachment" in content_disposition:
                part_filename = part.get_filename()
                if part_filename == filename:
                    payload = part.get_payload(decode=True)
                    if payload:
                        file_path.write_bytes(payload)
                        found = True
                        break

        if not found:
            raise ValueError(f"Attachment '{filename}' not found in message {msg_id}")

        return {
            "status": "ok",
            "message": f"Downloaded '{filename}' to '{file_path}'",
            "path": str(file_path),
            "size": file_path.stat().st_size,
        }

    finally:
        adapter.disconnect()
