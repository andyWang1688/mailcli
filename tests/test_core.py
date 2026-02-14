"""Unit tests for core business logic with mocks."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.mailcli.core.envelope import envelope_list, envelope_search
from src.mailcli.core.folder import folder_list
from src.mailcli.core.message import message_read, message_send
from src.mailcli.core.attachment import attachment_list, attachment_download


@pytest.fixture
def mock_config():
    """Mock configuration."""
    from src.mailcli.infra.config import AccountConfig, Config

    account = AccountConfig(
        name="test-account",
        email="test@example.com",
        imap_host="imap.example.com",
        imap_port=993,
        smtp_host="smtp.example.com",
        smtp_port=465,
        auth_raw="test-password",
        use_ssl=True,
    )
    config = Config(accounts={"test-account": account}, default_account="test-account")
    return config


@pytest.fixture
def mock_imap_response():
    """Mock IMAP response for envelope list."""
    return [
        {
            "id": "1",
            "subject": "Test Email 1",
            "from": "sender1@example.com",
            "to": ["recipient@example.com"],
            "date": "Mon, 12 Feb 2026 10:00:00 +0000",
            "size": 1024,
        },
        {
            "id": "2",
            "subject": "Test Email 2",
            "from": "sender2@example.com",
            "to": ["recipient@example.com"],
            "date": "Mon, 12 Feb 2026 11:00:00 +0000",
            "size": 2048,
        },
    ]


@pytest.fixture
def mock_message():
    """Mock message for read."""
    return {
        "id": "1",
        "subject": "Test Subject",
        "from": "sender@example.com",
        "to": "recipient@example.com",
        "cc": "cc@example.com",
        "date": "Mon, 12 Feb 2026 10:00:00 +0000",
        "body": "This is a test email body.",
        "size": 512,
    }


@pytest.fixture
def mock_attachments():
    """Mock attachments list."""
    return [
        {
            "id": "1",
            "filename": "document.pdf",
            "content_type": "application/pdf",
            "size": 4096,
            "disposition": 'attachment; filename="document.pdf"',
        },
        {
            "id": "1",
            "filename": "image.png",
            "content_type": "image/png",
            "size": 8192,
            "disposition": 'attachment; filename="image.png"',
        },
    ]


def test_envelope_list_success(mock_config, mock_imap_response):
    """Test successful envelope list."""
    mock_adapter = MagicMock()
    mock_adapter.list_envelopes.return_value = mock_imap_response

    with patch("src.mailcli.core.envelope.get_config", return_value=mock_config):
        with patch("src.mailcli.core.envelope.IMAPAdapter", return_value=mock_adapter):
            result = envelope_list("test-account", "INBOX", 50)

            assert len(result) == 2
            assert result[0]["subject"] == "Test Email 1"
            assert result[1]["subject"] == "Test Email 2"
            mock_adapter.connect.assert_called_once()
            mock_adapter.disconnect.assert_called_once()


def test_envelope_search_success(mock_config, mock_imap_response):
    """Test successful envelope search."""
    mock_adapter = MagicMock()
    mock_adapter.search_envelopes.return_value = mock_imap_response

    with patch("src.mailcli.core.envelope.get_config", return_value=mock_config):
        with patch("src.mailcli.core.envelope.IMAPAdapter", return_value=mock_adapter):
            result = envelope_search("test-account", "FROM sender1@example.com")

            assert len(result) == 2
            mock_adapter.search_envelopes.assert_called_once_with(
                "FROM sender1@example.com", "INBOX"
            )


def test_folder_list_success(mock_config):
    """Test successful folder list."""
    mock_adapter = MagicMock()
    mock_adapter.list_folders.return_value = [
        {"name": "收件箱", "server_name": "INBOX"},
        {"name": "已发送", "server_name": "Sent Messages"},
    ]

    with patch("src.mailcli.core.folder.get_config", return_value=mock_config):
        with patch("src.mailcli.core.folder.IMAPAdapter", return_value=mock_adapter):
            result = folder_list("test-account")

            assert len(result) == 2
            assert result[0]["server_name"] == "INBOX"
            assert result[1]["server_name"] == "Sent Messages"
            mock_adapter.connect.assert_called_once()
            mock_adapter.disconnect.assert_called_once()


def test_message_read_success(mock_config, mock_message):
    """Test successful message read."""
    mock_adapter = MagicMock()
    mock_adapter.read_message.return_value = mock_message

    with patch("src.mailcli.core.message.get_config", return_value=mock_config):
        with patch("src.mailcli.core.message.IMAPAdapter", return_value=mock_adapter):
            result = message_read("test-account", "1")

            assert result["id"] == "1"
            assert result["subject"] == "Test Subject"
            assert result["body"] == "This is a test email body."
            mock_adapter.read_message.assert_called_once_with("1", "INBOX")


def test_message_send_success(mock_config):
    """Test successful message send."""
    mock_adapter = MagicMock()
    mock_adapter.send_message.return_value = {
        "status": "ok",
        "message": "Message sent to recipient@example.com",
        "to": "recipient@example.com",
        "subject": "Test Subject",
    }

    with patch("src.mailcli.core.message.get_config", return_value=mock_config):
        with patch("src.mailcli.core.message.SMTPAdapter", return_value=mock_adapter):
            result = message_send(
                "test-account", "recipient@example.com", "Test Subject", "Test Body"
            )

            assert result["status"] == "ok"
            assert result["to"] == "recipient@example.com"
            assert result["subject"] == "Test Subject"
            mock_adapter.send_message.assert_called_once_with(
                "recipient@example.com", "Test Subject", "Test Body"
            )


def test_attachment_list_success(mock_config, mock_attachments):
    """Test successful attachment list."""
    mock_adapter = MagicMock()
    mock_adapter.get_attachments.return_value = mock_attachments

    with patch("src.mailcli.core.attachment.get_config", return_value=mock_config):
        with patch(
            "src.mailcli.core.attachment.IMAPAdapter", return_value=mock_adapter
        ):
            result = attachment_list("test-account", "1")

            assert len(result) == 2
            assert result[0]["filename"] == "document.pdf"
            assert result[1]["filename"] == "image.png"
            mock_adapter.get_attachments.assert_called_once_with("1", "INBOX")


def test_attachment_download_success(mock_config):
    """Test successful attachment download."""
    from src.mailcli.core.attachment import attachment_download

    mock_adapter = MagicMock()
    mock_adapter.get_attachments.return_value = [
        {
            "id": "1",
            "filename": "document.pdf",
            "content_type": "application/pdf",
            "size": 4096,
            "disposition": 'attachment; filename="document.pdf"',
        }
    ]

    def mock_fetch(msg_id, criteria):
        from email.message import EmailMessage

        msg = EmailMessage()
        msg["Content-Type"] = "application/pdf"
        msg["Content-Disposition"] = 'attachment; filename="document.pdf"'
        msg.set_payload(b"fake pdf content")
        return ("OK", [("", msg.as_bytes())])

    mock_adapter.connection.fetch = mock_fetch

    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("src.mailcli.core.attachment.get_config", return_value=mock_config):
            with patch(
                "src.mailcli.core.attachment.IMAPAdapter", return_value=mock_adapter
            ):
                result = attachment_download(
                    "test-account", "1", "document.pdf", tmpdir
                )

                assert result["status"] == "ok"
                assert "document.pdf" in result["path"]
                assert result["size"] > 0


def test_envelope_list_connection_error(mock_config):
    """Test envelope list with connection error."""
    from src.mailcli.infra.errors import ConnectionError

    mock_adapter = MagicMock()
    mock_adapter.connect.side_effect = ConnectionError("Connection failed")

    with patch("src.mailcli.core.envelope.get_config", return_value=mock_config):
        with patch("src.mailcli.core.envelope.IMAPAdapter", return_value=mock_adapter):
            with pytest.raises(ConnectionError):
                envelope_list("test-account")


def test_message_send_authentication_error(mock_config):
    """Test message send with authentication error."""
    from src.mailcli.infra.errors import AuthenticationError

    mock_adapter = MagicMock()
    mock_adapter.connect.side_effect = AuthenticationError("SMTP authentication failed")

    with patch("src.mailcli.core.message.get_config", return_value=mock_config):
        with patch("src.mailcli.core.message.SMTPAdapter", return_value=mock_adapter):
            with pytest.raises(AuthenticationError):
                message_send("test-account", "recipient@example.com", "Test", "Body")


def test_message_send_timeout_error(mock_config):
    """Test message send with timeout error."""
    from src.mailcli.infra.errors import TimeoutError

    mock_adapter = MagicMock()
    mock_adapter.connect.side_effect = TimeoutError("SMTP connection timed out")

    with patch("src.mailcli.core.message.get_config", return_value=mock_config):
        with patch("src.mailcli.core.message.SMTPAdapter", return_value=mock_adapter):
            with pytest.raises(TimeoutError):
                message_send("test-account", "recipient@example.com", "Test", "Body")


def test_envelope_search_with_folder(mock_config, mock_imap_response):
    """Test envelope search with custom folder."""
    mock_adapter = MagicMock()
    mock_adapter.search_envelopes.return_value = mock_imap_response

    with patch("src.mailcli.core.envelope.get_config", return_value=mock_config):
        with patch("src.mailcli.core.envelope.IMAPAdapter", return_value=mock_adapter):
            result = envelope_search("test-account", "test", "Archive")

            mock_adapter.search_envelopes.assert_called_once_with("test", "Archive")


def test_message_read_with_folder(mock_config, mock_message):
    """Test message read with custom folder."""
    mock_adapter = MagicMock()
    mock_adapter.read_message.return_value = mock_message

    with patch("src.mailcli.core.message.get_config", return_value=mock_config):
        with patch("src.mailcli.core.message.IMAPAdapter", return_value=mock_adapter):
            result = message_read("test-account", "1", "Sent")

            assert result["id"] == "1"
            mock_adapter.read_message.assert_called_once_with("1", "Sent")


def test_attachment_not_found(mock_config):
    """Test attachment download when attachment not found."""
    from src.mailcli.core.attachment import attachment_download

    mock_adapter = MagicMock()
    mock_adapter.get_attachments.return_value = []

    def mock_fetch(msg_id, criteria):
        from email.message import EmailMessage

        msg = EmailMessage()
        msg.set_content("No attachments")
        return ("OK", [("", msg.as_bytes())])

    mock_adapter.connection.fetch = mock_fetch

    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("src.mailcli.core.attachment.get_config", return_value=mock_config):
            with patch(
                "src.mailcli.core.attachment.IMAPAdapter", return_value=mock_adapter
            ):
                with pytest.raises(
                    ValueError, match="Attachment 'missing.pdf' not found"
                ):
                    attachment_download("test-account", "1", "missing.pdf", tmpdir)


def test_envelope_list_with_limit(mock_config, mock_imap_response):
    """Test envelope list with custom limit."""
    mock_adapter = MagicMock()
    mock_adapter.list_envelopes.return_value = mock_imap_response

    with patch("src.mailcli.core.envelope.get_config", return_value=mock_config):
        with patch("src.mailcli.core.envelope.IMAPAdapter", return_value=mock_adapter):
            result = envelope_list("test-account", "INBOX", 10)

            assert len(result) == 2
            mock_adapter.list_envelopes.assert_called_once_with("INBOX", 10)


def test_imap_adapter_select_folder():
    """Test IMAP adapter select folder."""
    from src.mailcli.infra.connections import IMAPAdapter
    from src.mailcli.infra.config import AccountConfig

    account = AccountConfig(
        name="test",
        email="test@example.com",
        imap_host="localhost",
        imap_port=993,
        smtp_host="localhost",
        smtp_port=465,
    )

    with patch("imaplib.IMAP4_SSL"):
        with patch("imaplib.IMAP4"):
            adapter = IMAPAdapter(account)
            with patch.object(adapter, "connection"):
                adapter.connection = MagicMock()
                adapter.select_folder("INBOX")
                adapter.connection.select.assert_called_once_with("INBOX")


def test_imap_adapter_select_folder_with_chinese_name():
    """Test IMAP adapter encodes non-ASCII folder names."""
    from src.mailcli.infra.connections import IMAPAdapter
    from src.mailcli.infra.config import AccountConfig

    account = AccountConfig(
        name="test",
        email="test@example.com",
        imap_host="localhost",
        imap_port=993,
        smtp_host="localhost",
        smtp_port=465,
    )

    with patch("imaplib.IMAP4_SSL"):
        with patch("imaplib.IMAP4"):
            adapter = IMAPAdapter(account)
            with patch.object(adapter, "connection"):
                adapter.connection = MagicMock()
                folder_name = "其他文件夹/穆桥"
                adapter.select_folder(folder_name)

                encoded_name = adapter._encode_imap_utf7(folder_name)
                adapter.connection.select.assert_called_once_with(encoded_name)
                assert encoded_name == "&UXZO1mWHTvZZOQ-/&ekZoZQ-"


def test_smtp_adapter_connect_with_ssl():
    """Test SMTP adapter connect with SSL."""
    from src.mailcli.infra.connections import SMTPAdapter
    from src.mailcli.infra.config import AccountConfig

    account = AccountConfig(
        name="test",
        email="test@example.com",
        imap_host="localhost",
        imap_port=993,
        smtp_host="localhost",
        smtp_port=465,
        use_ssl=True,
    )

    with patch("smtplib.SMTP_SSL") as mock_smtp_ssl:
        mock_smtp = MagicMock()
        mock_smtp_ssl.return_value = mock_smtp

        adapter = SMTPAdapter(account)
        adapter.connect()

        mock_smtp_ssl.assert_called_once_with("localhost", 465)


def test_smtp_adapter_connect_without_ssl():
    """Test SMTP adapter connect without SSL."""
    from src.mailcli.infra.connections import SMTPAdapter
    from src.mailcli.infra.config import AccountConfig

    account = AccountConfig(
        name="test",
        email="test@example.com",
        imap_host="localhost",
        imap_port=143,
        smtp_host="localhost",
        smtp_port=587,
        use_ssl=False,
    )

    with patch("smtplib.SMTP") as mock_smtp:
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance

        adapter = SMTPAdapter(account)
        adapter.connect()

        mock_smtp.assert_called_once_with("localhost", 587)


def test_diagnose_result():
    """Test DiagnoseResult dataclass."""
    from src.mailcli.infra.connections import DiagnoseResult

    result = DiagnoseResult(
        name="imap",
        status="ok",
        message="Success",
        details={"host": "example.com"},
    )

    assert result.name == "imap"
    assert result.status == "ok"
    assert result.message == "Success"
    assert result.details == {"host": "example.com"}

    result_dict = result.to_dict()
    assert result_dict["name"] == "imap"
    assert result_dict["status"] == "ok"
    assert result_dict["message"] == "Success"


def test_imap_adapter_parse_envelope_extracts_fields():
    """Test envelope parser returns populated summary fields."""
    from src.mailcli.infra.config import AccountConfig
    from src.mailcli.infra.connections import IMAPAdapter

    account = AccountConfig(
        name="test",
        email="test@example.com",
        imap_host="localhost",
        imap_port=993,
        smtp_host="localhost",
        smtp_port=465,
    )
    adapter = IMAPAdapter(account)

    fetch_data = [
        (
            b"1 (RFC822.SIZE 321 BODY[HEADER] {128}",
            (
                b"Subject: Monthly Report\r\n"
                b"From: Alice <alice@example.com>\r\n"
                b"To: Bob <bob@example.com>\r\n"
                b"Date: Fri, 14 Feb 2026 10:00:00 +0800\r\n\r\n"
            ),
        ),
        b")",
    ]

    envelope = adapter._parse_envelope(b"1", fetch_data)
    assert envelope is not None
    assert envelope["id"] == "1"
    assert envelope["subject"] == "Monthly Report"
    assert "alice@example.com" in envelope["from"]
    assert envelope["to"]
    assert envelope["date"].startswith("Fri, 14 Feb 2026")
    assert envelope["size"] == 321
