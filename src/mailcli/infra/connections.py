"""IMAP and SMTP connection adapters."""

from __future__ import annotations

import imaplib
import smtplib
import socket
import ssl
import re
import base64
import subprocess
from dataclasses import dataclass
from typing import Any

from .config import AccountConfig
from .errors import AuthenticationError, ConfigError, ConnectionError, TimeoutError


@dataclass
class DiagnoseResult:
    """Diagnostic result."""

    name: str
    status: str
    message: str
    details: dict[str, Any] | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "details": self.details,
        }


class IMAPAdapter:
    """IMAP connection adapter."""

    def __init__(self, account: AccountConfig) -> None:
        self.account = account
        self.connection: imaplib.IMAP4 | None = None

    def select_folder(self, folder: str = "INBOX") -> None:
        """Select a folder."""
        if not self.connection:
            raise ConnectionError("Not connected to IMAP server")
        server_folder = (
            self._encode_imap_utf7(folder) if self._has_non_ascii(folder) else folder
        )
        typ, _ = self.connection.select(server_folder)
        if typ != "OK":
            raise ConnectionError(f"Folder '{folder}' not found or not accessible")

    def create_folder(self, folder: str) -> dict[str, Any]:
        """Create a folder."""
        if not self.connection:
            raise ConnectionError("Not connected to IMAP server")

        server_folder = (
            self._encode_imap_utf7(folder) if self._has_non_ascii(folder) else folder
        )
        typ, data = self.connection.create(server_folder)
        if typ != "OK":
            detail = self._decode_imap_status(data)
            raise ConnectionError(f"Failed to create folder '{folder}': {detail}")
        return {"status": "ok", "folder": folder, "action": "create"}

    def delete_folder(self, folder: str) -> dict[str, Any]:
        """Delete a folder."""
        if not self.connection:
            raise ConnectionError("Not connected to IMAP server")

        server_folder = (
            self._encode_imap_utf7(folder) if self._has_non_ascii(folder) else folder
        )
        typ, data = self.connection.delete(server_folder)
        if typ != "OK":
            detail = self._decode_imap_status(data)
            raise ConnectionError(f"Failed to delete folder '{folder}': {detail}")
        return {"status": "ok", "folder": folder, "action": "delete"}

    def expunge_folder(
        self, folder: str = "INBOX", purge: bool = False
    ) -> dict[str, Any]:
        """Expunge deleted messages, optionally purge all messages."""
        if not self.connection:
            raise ConnectionError("Not connected to IMAP server")

        self.select_folder(folder)
        if purge:
            typ, data = self.connection.store("1:*", "+FLAGS", "(\\Deleted)")
            if typ != "OK":
                detail = self._decode_imap_status(data)
                raise ConnectionError(f"Failed to mark messages as deleted: {detail}")

        typ, data = self.connection.expunge()
        if typ != "OK":
            detail = self._decode_imap_status(data)
            raise ConnectionError(f"Failed to expunge folder '{folder}': {detail}")

        removed = len(data or [])
        return {
            "status": "ok",
            "folder": folder,
            "action": "purge" if purge else "expunge",
            "removed": removed,
        }

    def fetch_message_raw(self, msg_id: str, folder: str = "INBOX") -> bytes:
        """Fetch raw message bytes by ID."""
        if not self.connection:
            raise ConnectionError("Not connected to IMAP server")

        self.select_folder(folder)
        typ, data = self.connection.fetch(msg_id, "(RFC822)")
        if typ != "OK" or not data or not isinstance(data[0], tuple):
            raise ConnectionError(f"Failed to fetch message {msg_id}")

        raw_email = data[0][1]
        if not isinstance(raw_email, bytes):
            raise ConnectionError(f"Unexpected message payload for {msg_id}")
        return raw_email

    def copy_message(
        self, msg_id: str, destination_folder: str, source_folder: str = "INBOX"
    ) -> dict[str, Any]:
        """Copy message to destination folder."""
        if not self.connection:
            raise ConnectionError("Not connected to IMAP server")

        self.select_folder(source_folder)
        destination = (
            self._encode_imap_utf7(destination_folder)
            if self._has_non_ascii(destination_folder)
            else destination_folder
        )
        typ, data = self.connection.copy(msg_id, destination)
        if typ != "OK":
            detail = self._decode_imap_status(data)
            raise ConnectionError(
                f"Failed to copy message {msg_id} to '{destination_folder}': {detail}"
            )
        return {
            "status": "ok",
            "id": msg_id,
            "from_folder": source_folder,
            "to_folder": destination_folder,
            "action": "copy",
        }

    def move_message(
        self, msg_id: str, destination_folder: str, source_folder: str = "INBOX"
    ) -> dict[str, Any]:
        """Move message by copy + delete + expunge."""
        copy_result = self.copy_message(msg_id, destination_folder, source_folder)
        self.delete_message(msg_id, source_folder, expunge=True)
        return {
            "status": "ok",
            "id": msg_id,
            "from_folder": source_folder,
            "to_folder": destination_folder,
            "action": "move",
            "copied": copy_result["status"] == "ok",
        }

    def delete_message(
        self, msg_id: str, folder: str = "INBOX", expunge: bool = True
    ) -> dict[str, Any]:
        """Mark message deleted and optionally expunge."""
        if not self.connection:
            raise ConnectionError("Not connected to IMAP server")

        self.select_folder(folder)
        typ, data = self.connection.store(msg_id, "+FLAGS", "(\\Deleted)")
        if typ != "OK":
            detail = self._decode_imap_status(data)
            raise ConnectionError(f"Failed to mark message {msg_id} deleted: {detail}")

        expunged = False
        if expunge:
            typ, data = self.connection.expunge()
            if typ != "OK":
                detail = self._decode_imap_status(data)
                raise ConnectionError(
                    f"Failed to expunge deleted message {msg_id}: {detail}"
                )
            expunged = True

        return {
            "status": "ok",
            "id": msg_id,
            "folder": folder,
            "action": "delete",
            "expunged": expunged,
        }

    def update_flags(
        self,
        msg_id: str,
        flags: list[str],
        action: str = "add",
        folder: str = "INBOX",
    ) -> dict[str, Any]:
        """Add or remove IMAP flags."""
        if not self.connection:
            raise ConnectionError("Not connected to IMAP server")
        if action not in {"add", "remove"}:
            raise ValueError("action must be 'add' or 'remove'")

        imap_flags = [self._normalize_flag(flag) for flag in flags]
        self.select_folder(folder)
        operator = "+FLAGS" if action == "add" else "-FLAGS"
        typ, data = self.connection.store(msg_id, operator, f"({' '.join(imap_flags)})")
        if typ != "OK":
            detail = self._decode_imap_status(data)
            raise ConnectionError(
                f"Failed to {action} flags on message {msg_id}: {detail}"
            )

        return {
            "status": "ok",
            "id": msg_id,
            "folder": folder,
            "action": action,
            "flags": flags,
        }

    def list_folders(self) -> list[dict[str, str]]:
        """List available folders from IMAP server."""
        if not self.connection:
            raise ConnectionError("Not connected to IMAP server")

        typ, data = self.connection.list()
        if typ != "OK" or not data:
            return []

        folders: list[dict[str, str]] = []
        for item in data:
            raw_line = (
                item.decode("utf-8", errors="ignore")
                if isinstance(item, bytes)
                else str(item)
            )
            raw_name = self._extract_mailbox_name(raw_line)
            display_name = self._decode_imap_utf7(raw_name)
            folders.append(
                {
                    "name": display_name,
                    "server_name": raw_name,
                }
            )

        return folders

    def list_envelopes(
        self, folder: str = "INBOX", limit: int = 50
    ) -> list[dict[str, Any]]:
        """List envelopes from a folder."""
        if not self.connection:
            raise ConnectionError("Not connected to IMAP server")

        self.select_folder(folder)
        typ, data = self.connection.search(None, "ALL")

        if typ != "OK":
            return []

        envelope_ids = data[0].split()
        envelopes = []

        for msg_id in reversed(envelope_ids[:limit]):
            typ, data = self.connection.fetch(msg_id, "(RFC822.SIZE BODY.PEEK[HEADER])")

            if typ != "OK":
                continue

            envelope = self._parse_envelope(msg_id, data)
            if envelope:
                envelopes.append(envelope)

        return envelopes

    def search_envelopes(
        self, criteria: str, folder: str = "INBOX"
    ) -> list[dict[str, Any]]:
        """Search envelopes by criteria."""
        if not self.connection:
            raise ConnectionError("Not connected to IMAP server")

        self.select_folder(folder)
        typ, data = self.connection.search(None, criteria)

        if typ != "OK":
            return []

        envelope_ids = data[0].split()
        envelopes = []

        for msg_id in reversed(envelope_ids):
            typ, data = self.connection.fetch(msg_id, "(RFC822.SIZE BODY.PEEK[HEADER])")

            if typ != "OK":
                continue

            envelope = self._parse_envelope(msg_id, data)
            if envelope:
                envelopes.append(envelope)

        return envelopes

    def read_message(self, msg_id: str, folder: str = "INBOX") -> dict[str, Any]:
        """Read a message by ID."""
        raw_email = self.fetch_message_raw(msg_id, folder)
        return self._parse_message(raw_email, msg_id)

    def get_attachments(
        self, msg_id: str, folder: str = "INBOX"
    ) -> list[dict[str, Any]]:
        """Get attachments from a message."""
        raw_email = self.fetch_message_raw(msg_id, folder)
        return self._parse_attachments(raw_email, msg_id)

    def _parse_envelope(
        self, msg_id: bytes | str, fetch_data: Any
    ) -> dict[str, Any] | None:
        """Parse envelope from IMAP fetch response."""
        try:
            message_id = (
                msg_id.decode("utf-8", errors="ignore")
                if isinstance(msg_id, bytes)
                else str(msg_id)
            )

            metadata_text = ""
            header_bytes: bytes | None = None

            if isinstance(fetch_data, list):
                for part in fetch_data:
                    if not isinstance(part, tuple):
                        continue
                    if len(part) > 0 and isinstance(part[0], bytes):
                        metadata_text = part[0].decode("utf-8", errors="ignore")
                    if len(part) > 1 and isinstance(part[1], bytes):
                        header_bytes = part[1]
                    break

            if not header_bytes:
                return {
                    "id": message_id,
                    "subject": "",
                    "from": "",
                    "to": [],
                    "date": "",
                    "size": 0,
                }

            import email
            from email.header import decode_header

            msg = email.message_from_bytes(header_bytes)

            def decode_value(value: str | None) -> str:
                if not value:
                    return ""
                parts = []
                for segment, encoding in decode_header(value):
                    if isinstance(segment, bytes):
                        try:
                            parts.append(
                                segment.decode(encoding or "utf-8", errors="ignore")
                            )
                        except (LookupError, UnicodeDecodeError):
                            parts.append(segment.decode("utf-8", errors="ignore"))
                    else:
                        parts.append(str(segment))
                return "".join(parts).strip()

            to_values = [
                decode_value(addr)
                for addr in msg.get_all("To", [])
                if decode_value(addr)
            ]

            size = 0
            size_match = re.search(
                r"RFC822\.SIZE\s+(\d+)", metadata_text, re.IGNORECASE
            )
            if size_match:
                size = int(size_match.group(1))

            return {
                "id": message_id,
                "subject": decode_value(msg.get("Subject")),
                "from": decode_value(msg.get("From")),
                "to": to_values,
                "date": decode_value(msg.get("Date")),
                "size": size,
            }

        except Exception:
            return None

    def _extract_mailbox_name(self, list_line: str) -> str:
        """Extract mailbox name from IMAP LIST response line."""
        match = re.search(r'"([^"]+)"\s*$', list_line)
        if match:
            return match.group(1)
        parts = list_line.rsplit(" ", 1)
        if len(parts) == 2:
            return parts[1].strip('"')
        return list_line

    def _decode_imap_utf7(self, mailbox_name: str) -> str:
        """Decode IMAP modified UTF-7 mailbox names."""
        result: list[str] = []
        index = 0
        length = len(mailbox_name)

        while index < length:
            if mailbox_name[index] != "&":
                result.append(mailbox_name[index])
                index += 1
                continue

            end = mailbox_name.find("-", index)
            if end == -1:
                result.append(mailbox_name[index])
                index += 1
                continue

            if end == index + 1:
                result.append("&")
                index = end + 1
                continue

            modified = mailbox_name[index + 1 : end].replace(",", "/")
            padding = "=" * ((4 - len(modified) % 4) % 4)
            try:
                decoded = base64.b64decode(modified + padding).decode("utf-16-be")
                result.append(decoded)
            except Exception:
                result.append(mailbox_name[index : end + 1])

            index = end + 1

        return "".join(result)

    def _encode_imap_utf7(self, mailbox_name: str) -> str:
        """Encode folder names to IMAP modified UTF-7."""
        result: list[str] = []
        buffer: list[str] = []

        def flush_buffer() -> None:
            if not buffer:
                return
            raw_utf16 = "".join(buffer).encode("utf-16-be")
            encoded = base64.b64encode(raw_utf16).decode("ascii").rstrip("=")
            encoded = encoded.replace("/", ",")
            result.append(f"&{encoded}-")
            buffer.clear()

        for char in mailbox_name:
            codepoint = ord(char)
            is_printable_ascii = 0x20 <= codepoint <= 0x7E

            if is_printable_ascii and char != "&":
                flush_buffer()
                result.append(char)
            elif char == "&":
                flush_buffer()
                result.append("&-")
            else:
                buffer.append(char)

        flush_buffer()
        return "".join(result)

    def _has_non_ascii(self, value: str) -> bool:
        """Return True when string contains non-ASCII chars."""
        return any(ord(char) > 127 for char in value)

    def _decode_imap_status(self, data: Any) -> str:
        """Decode IMAP status payload into readable text."""
        if not data:
            return "no server detail"
        if isinstance(data, list):
            values: list[str] = []
            for item in data:
                if isinstance(item, bytes):
                    values.append(item.decode("utf-8", errors="ignore"))
                else:
                    values.append(str(item))
            return " | ".join(values)
        if isinstance(data, bytes):
            return data.decode("utf-8", errors="ignore")
        return str(data)

    def _normalize_flag(self, flag: str) -> str:
        """Normalize user-facing flags to IMAP flags."""
        mapping = {
            "seen": "\\Seen",
            "flagged": "\\Flagged",
            "deleted": "\\Deleted",
        }
        key = flag.strip().lower().lstrip("\\")
        if key not in mapping:
            raise ValueError(
                f"Unsupported flag '{flag}'. Supported flags: seen, flagged, deleted"
            )
        return mapping[key]

    def _resolve_auth_secret(self) -> str | None:
        """Resolve auth secret from auth.raw or auth.cmd."""
        if self.account.auth_raw:
            return self.account.auth_raw
        if not self.account.auth_cmd:
            return None

        try:
            result = subprocess.run(
                self.account.auth_cmd,
                shell=True,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            stderr = (e.stderr or "").strip()
            detail = f": {stderr}" if stderr else ""
            raise ConfigError(f"Failed to execute auth.cmd{detail}")

        token = result.stdout.strip()
        if not token:
            raise ConfigError("auth.cmd returned empty output")
        return token

    def _parse_message(self, raw_email: bytes, msg_id: str) -> dict[str, Any]:
        """Parse message from raw email."""
        import email
        from email.header import decode_header

        msg = email.message_from_bytes(raw_email)

        def decode_str(value: str | None) -> str:
            """Decode header string."""
            if not value:
                return ""
            decoded = []
            for part, encoding in decode_header(value):
                if isinstance(part, bytes):
                    try:
                        decoded.append(
                            part.decode(encoding or "utf-8", errors="ignore")
                        )
                    except (LookupError, UnicodeDecodeError):
                        decoded.append(part.decode("utf-8", errors="ignore"))
                else:
                    decoded.append(str(part))
            return "".join(decoded)

        def get_body(msg: Any) -> str:
            """Extract body from message."""
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition", ""))

                    if (
                        content_type == "text/plain"
                        and "attachment" not in content_disposition
                    ):
                        payload = part.get_payload(decode=True)
                        if payload:
                            charset = part.get_content_charset() or "utf-8"
                            try:
                                body += payload.decode(charset, errors="ignore")
                            except (LookupError, UnicodeDecodeError):
                                body += payload.decode("utf-8", errors="ignore")
            elif msg.get_content_type() == "text/plain":
                payload = msg.get_payload(decode=True)
                if payload:
                    charset = msg.get_content_charset() or "utf-8"
                    try:
                        body = payload.decode(charset, errors="ignore")
                    except (LookupError, UnicodeDecodeError):
                        body = payload.decode("utf-8", errors="ignore")

            return body

        return {
            "id": msg_id,
            "subject": decode_str(msg.get("Subject")),
            "from": decode_str(msg.get("From")),
            "to": decode_str(msg.get("To")),
            "cc": decode_str(msg.get("Cc")),
            "date": decode_str(msg.get("Date")),
            "body": get_body(msg),
            "size": len(raw_email),
        }

    def _parse_attachments(self, raw_email: bytes, msg_id: str) -> list[dict[str, Any]]:
        """Parse attachments from raw email."""
        import email

        msg = email.message_from_bytes(raw_email)
        attachments = []

        for part in msg.walk():
            content_disposition = str(part.get("Content-Disposition", ""))

            if "attachment" in content_disposition:
                filename = part.get_filename()
                if filename:
                    content_type = part.get_content_type() or "application/octet-stream"
                    size = len(part.get_payload(decode=True) or b"")

                    attachments.append(
                        {
                            "id": msg_id,
                            "filename": filename,
                            "content_type": content_type,
                            "size": size,
                            "disposition": content_disposition,
                        }
                    )

        return attachments

    def connect(self) -> None:
        """Connect to IMAP server."""
        try:
            if self.account.use_ssl:
                self.connection = imaplib.IMAP4_SSL(
                    self.account.imap_host,
                    self.account.imap_port,
                )
            else:
                self.connection = imaplib.IMAP4(
                    self.account.imap_host,
                    self.account.imap_port,
                )

            secret = self._resolve_auth_secret()
            if secret:
                self.connection.login(self.account.email, secret)

        except imaplib.IMAP4.error as e:
            raise AuthenticationError(f"IMAP authentication failed: {e}")
        except socket.timeout:
            raise TimeoutError("IMAP connection timed out")
        except (socket.error, ssl.SSLError) as e:
            raise ConnectionError(f"IMAP connection failed: {e}")
        except ConfigError:
            raise

    def disconnect(self) -> None:
        """Disconnect from IMAP server."""
        if self.connection:
            try:
                self.connection.close()
                self.connection.logout()
            except Exception:
                pass
            self.connection = None


class SMTPAdapter:
    """SMTP connection adapter."""

    def __init__(self, account: AccountConfig) -> None:
        self.account = account
        self.connection: smtplib.SMTP | None = None

    def connect(self) -> None:
        """Connect to SMTP server."""
        try:
            if self.account.use_ssl:
                self.connection = smtplib.SMTP_SSL(
                    self.account.smtp_host,
                    self.account.smtp_port,
                )
            else:
                self.connection = smtplib.SMTP(
                    self.account.smtp_host,
                    self.account.smtp_port,
                )

            secret = self._resolve_auth_secret()
            if secret:
                self.connection.login(self.account.email, secret)

        except smtplib.SMTPAuthenticationError as e:
            raise AuthenticationError(f"SMTP authentication failed: {e}")
        except socket.timeout:
            raise TimeoutError("SMTP connection timed out")
        except (socket.error, ssl.SSLError) as e:
            raise ConnectionError(f"SMTP connection failed: {e}")
        except ConfigError:
            raise

    def _resolve_auth_secret(self) -> str | None:
        """Resolve auth secret from auth.raw or auth.cmd."""
        if self.account.auth_raw:
            return self.account.auth_raw
        if not self.account.auth_cmd:
            return None

        try:
            result = subprocess.run(
                self.account.auth_cmd,
                shell=True,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            stderr = (e.stderr or "").strip()
            detail = f": {stderr}" if stderr else ""
            raise ConfigError(f"Failed to execute auth.cmd{detail}")

        token = result.stdout.strip()
        if not token:
            raise ConfigError("auth.cmd returned empty output")
        return token

    def disconnect(self) -> None:
        """Disconnect from SMTP server."""
        if self.connection:
            try:
                self.connection.quit()
            except Exception:
                pass
            self.connection = None

    def send_message(
        self,
        to: str | list[str],
        subject: str,
        body: str,
        cc: str | list[str] | None = None,
    ) -> dict[str, Any]:
        """Send a simple text message."""
        from email.message import EmailMessage

        if not self.connection:
            raise ConnectionError("Not connected to SMTP server")
        connection = self.connection

        to_list = [to] if isinstance(to, str) else to
        cc_list = []
        if cc:
            cc_list = [cc] if isinstance(cc, str) else cc

        msg = EmailMessage()
        msg["From"] = self.account.email
        msg["To"] = ", ".join(to_list)
        if cc_list:
            msg["Cc"] = ", ".join(cc_list)
        msg["Subject"] = subject
        msg.set_content(body)

        try:
            connection.send_message(msg)
            recipients = to_list + cc_list
            return {
                "status": "ok",
                "message": f"Message sent to {', '.join(recipients)}",
                "to": to_list,
                "cc": cc_list,
                "subject": subject,
            }
        except smtplib.SMTPException as e:
            raise ConnectionError(f"Failed to send message: {e}")


def diagnose_account(account: AccountConfig) -> list[DiagnoseResult]:
    """Diagnose account connectivity."""
    results = []

    results.append(_diagnose_imap(account))
    results.append(_diagnose_smtp(account))

    return results


def _diagnose_imap(account: AccountConfig) -> DiagnoseResult:
    """Diagnose IMAP connectivity."""
    details = {
        "host": account.imap_host,
        "port": account.imap_port,
        "ssl": account.use_ssl,
    }

    try:
        socket.create_connection((account.imap_host, account.imap_port), timeout=5)
        details["network"] = "ok"
    except socket.timeout:
        return DiagnoseResult(
            name="imap_network",
            status="failed",
            message=f"Cannot connect to {account.imap_host}:{account.imap_port} (timeout)",
            details=details,
        )
    except (socket.error, OSError) as e:
        return DiagnoseResult(
            name="imap_network",
            status="failed",
            message=f"Cannot connect to {account.imap_host}:{account.imap_port}: {e}",
            details=details,
        )

    try:
        adapter = IMAPAdapter(account)
        adapter.connect()
        adapter.disconnect()
        return DiagnoseResult(
            name="imap",
            status="ok",
            message=f"Successfully connected to IMAP at {account.imap_host}:{account.imap_port}",
            details=details,
        )
    except AuthenticationError as e:
        return DiagnoseResult(
            name="imap",
            status="failed",
            message=f"IMAP authentication failed: {e}",
            details=details,
        )
    except ConnectionError as e:
        return DiagnoseResult(
            name="imap",
            status="failed",
            message=f"IMAP connection failed: {e}",
            details=details,
        )
    except TimeoutError as e:
        return DiagnoseResult(
            name="imap",
            status="failed",
            message=f"IMAP connection timed out: {e}",
            details=details,
        )


def _diagnose_smtp(account: AccountConfig) -> DiagnoseResult:
    """Diagnose SMTP connectivity."""
    details = {
        "host": account.smtp_host,
        "port": account.smtp_port,
        "ssl": account.use_ssl,
    }

    try:
        socket.create_connection((account.smtp_host, account.smtp_port), timeout=5)
        details["network"] = "ok"
    except socket.timeout:
        return DiagnoseResult(
            name="smtp_network",
            status="failed",
            message=f"Cannot connect to {account.smtp_host}:{account.smtp_port} (timeout)",
            details=details,
        )
    except (socket.error, OSError) as e:
        return DiagnoseResult(
            name="smtp_network",
            status="failed",
            message=f"Cannot connect to {account.smtp_host}:{account.smtp_port}: {e}",
            details=details,
        )

    try:
        adapter = SMTPAdapter(account)
        adapter.connect()
        adapter.disconnect()
        return DiagnoseResult(
            name="smtp",
            status="ok",
            message=f"Successfully connected to SMTP at {account.smtp_host}:{account.smtp_port}",
            details=details,
        )
    except AuthenticationError as e:
        return DiagnoseResult(
            name="smtp",
            status="failed",
            message=f"SMTP authentication failed: {e}",
            details=details,
        )
    except ConnectionError as e:
        return DiagnoseResult(
            name="smtp",
            status="failed",
            message=f"SMTP connection failed: {e}",
            details=details,
        )
    except TimeoutError as e:
        return DiagnoseResult(
            name="smtp",
            status="failed",
            message=f"SMTP connection timed out: {e}",
            details=details,
        )
