"""Unit tests for IMAP and SMTP operations."""

import tempfile

import pytest

from src.mailcli.core.envelope import envelope_list, envelope_search
from src.mailcli.core.folder import folder_list
from src.mailcli.core.message import message_read, message_send
from src.mailcli.core.attachment import attachment_list, attachment_download


@pytest.fixture
def empty_home(monkeypatch):
    """Provide an isolated HOME without mailcli config."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("HOME", tmpdir)
        yield


def test_envelope_list_no_config(empty_home):
    """Test envelope list without configuration."""
    with pytest.raises(FileNotFoundError):
        envelope_list("test_account")


def test_envelope_search_no_config(empty_home):
    """Test envelope search without configuration."""
    with pytest.raises(FileNotFoundError):
        envelope_search("test_account", "test query")


def test_folder_list_no_config(empty_home):
    """Test folder list without configuration."""
    with pytest.raises(FileNotFoundError):
        folder_list("test_account")


def test_message_read_no_config(empty_home):
    """Test message read without configuration."""
    with pytest.raises(FileNotFoundError):
        message_read("test_account", "12345")


def test_message_send_no_config(empty_home):
    """Test message send without configuration."""
    with pytest.raises(FileNotFoundError):
        message_send("test_account", "test@example.com", "Test", "Test body")


def test_attachment_list_no_config(empty_home):
    """Test attachment list without configuration."""
    with pytest.raises(FileNotFoundError):
        attachment_list("test_account", "12345")


def test_attachment_download_no_config(empty_home):
    """Test attachment download without configuration."""
    with pytest.raises(FileNotFoundError):
        attachment_download("test_account", "12345", "test.txt", "/tmp")
