"""Unit tests for mailcli."""

import os
import tempfile
from pathlib import Path

import pytest

from src.mailcli.infra.config import AccountConfig, Config, get_config
from src.mailcli.infra.output import OutputFormatter


def test_output_formatter_plain():
    """Test plain output formatting."""
    formatter = OutputFormatter("plain")
    result = formatter.format({"test": "data"})
    assert result == "{'test': 'data'}"


def test_output_formatter_json():
    """Test JSON output formatting."""
    formatter = OutputFormatter("json")
    result = formatter.format({"test": "data"})
    assert '"test": "data"' in result


def test_account_config_dataclass():
    """Test AccountConfig dataclass."""
    account = AccountConfig(
        name="test",
        email="test@example.com",
        imap_host="imap.example.com",
        imap_port=993,
        smtp_host="smtp.example.com",
        smtp_port=465,
    )
    assert account.name == "test"
    assert account.email == "test@example.com"
    assert account.use_ssl is True


def test_config_from_dict():
    """Test Config creation from dictionary."""
    accounts = {
        "test": AccountConfig(
            name="test",
            email="test@example.com",
            imap_host="imap.example.com",
            imap_port=993,
            smtp_host="smtp.example.com",
            smtp_port=465,
        )
    }
    config = Config(accounts=accounts, default_account="test")
    assert len(config.accounts) == 1
    assert config.default_account == "test"


def test_config_get_account():
    """Test getting account from Config."""
    accounts = {
        "test": AccountConfig(
            name="test",
            email="test@example.com",
            imap_host="imap.example.com",
            imap_port=993,
            smtp_host="smtp.example.com",
            smtp_port=465,
        )
    }
    config = Config(accounts=accounts, default_account="test")
    account = config.get_account()
    assert account.name == "test"


def test_config_get_account_by_name():
    """Test getting account by name from Config."""
    accounts = {
        "test1": AccountConfig(
            name="test1",
            email="test1@example.com",
            imap_host="imap1.example.com",
            imap_port=993,
            smtp_host="smtp1.example.com",
            smtp_port=465,
        ),
        "test2": AccountConfig(
            name="test2",
            email="test2@example.com",
            imap_host="imap2.example.com",
            imap_port=993,
            smtp_host="smtp2.example.com",
            smtp_port=465,
        ),
    }
    config = Config(accounts=accounts, default_account="test1")
    account = config.get_account("test2")
    assert account.name == "test2"


def test_config_get_account_not_found():
    """Test getting non-existent account from Config."""
    accounts = {
        "test": AccountConfig(
            name="test",
            email="test@example.com",
            imap_host="imap.example.com",
            imap_port=993,
            smtp_host="smtp.example.com",
            smtp_port=465,
        )
    }
    config = Config(accounts=accounts)
    with pytest.raises(ValueError, match="Account 'notfound' not found"):
        config.get_account("notfound")


def test_config_file_not_found():
    """Test loading config when file doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_home = Path.home()
        try:
            os.environ["HOME"] = tmpdir
            with pytest.raises(FileNotFoundError):
                get_config()
        finally:
            os.environ["HOME"] = str(original_home)


def test_get_config_supports_auth_cmd(monkeypatch):
    """Test loading auth.cmd from config file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / ".config" / "mailcli"
        config_dir.mkdir(parents=True)
        config_path = config_dir / "config.toml"
        config_path.write_text(
            """
default_account = "test"

[accounts.test]
email = "test@example.com"

[accounts.test.imap]
host = "imap.example.com"
port = 993

[accounts.test.smtp]
host = "smtp.example.com"
port = 465

[accounts.test.auth]
cmd = "printf token"
""".strip(),
            encoding="utf-8",
        )

        monkeypatch.setenv("HOME", tmpdir)
        cfg = get_config()
        assert cfg.accounts["test"].auth_raw is None
        assert cfg.accounts["test"].auth_cmd == "printf token"
