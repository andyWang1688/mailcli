"""Integration tests for mailcli CLI."""

import os
import sys
import tempfile
from pathlib import Path

import pytest


def test_cli_help():
    """Test CLI help command."""
    import subprocess

    result = subprocess.run(
        [sys.executable, "-m", "mailcli", "--help"],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": "src"},
    )
    assert result.returncode == 0
    assert "Mail CLI" in result.stdout
    assert "account" in result.stdout
    assert "folder" in result.stdout
    assert "envelope" in result.stdout
    assert "message" in result.stdout
    assert "attachment" in result.stdout
    assert "flag" in result.stdout
    assert "template" in result.stdout


def test_cli_account_help():
    """Test account command help."""
    import subprocess

    result = subprocess.run(
        [sys.executable, "-m", "mailcli", "account", "--help"],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": "src"},
    )
    assert result.returncode == 0
    assert "list" in result.stdout
    assert "default" in result.stdout
    assert "diagnose" in result.stdout


def test_cli_envelope_help():
    """Test envelope command help."""
    import subprocess

    result = subprocess.run(
        [sys.executable, "-m", "mailcli", "envelope", "--help"],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": "src"},
    )
    assert result.returncode == 0
    assert "list" in result.stdout
    assert "search" in result.stdout


def test_cli_folder_help():
    """Test folder command help."""
    import subprocess

    result = subprocess.run(
        [sys.executable, "-m", "mailcli", "folder", "--help"],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": "src"},
    )
    assert result.returncode == 0
    assert "list" in result.stdout
    assert "create" in result.stdout
    assert "delete" in result.stdout
    assert "expunge" in result.stdout
    assert "purge" in result.stdout


def test_cli_message_help():
    """Test message command help."""
    import subprocess

    result = subprocess.run(
        [sys.executable, "-m", "mailcli", "message", "--help"],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": "src"},
    )
    assert result.returncode == 0
    assert "read" in result.stdout
    assert "write" in result.stdout
    assert "send" in result.stdout
    assert "export" in result.stdout
    assert "reply" in result.stdout
    assert "forward" in result.stdout
    assert "copy" in result.stdout
    assert "move" in result.stdout
    assert "delete" in result.stdout


def test_cli_attachment_help():
    """Test attachment command help."""
    import subprocess

    result = subprocess.run(
        [sys.executable, "-m", "mailcli", "attachment", "--help"],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": "src"},
    )
    assert result.returncode == 0
    assert "list" in result.stdout
    assert "download" in result.stdout


def test_cli_template_help():
    """Test template command help."""
    import subprocess

    result = subprocess.run(
        [sys.executable, "-m", "mailcli", "template", "--help"],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": "src"},
    )
    assert result.returncode == 0
    assert "list-providers" in result.stdout
    assert "render" in result.stdout


def test_cli_account_list_no_config():
    """Test account list without configuration."""
    import subprocess

    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            [sys.executable, "-m", "mailcli", "account", "list"],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": "src", "HOME": tmpdir},
        )
        assert result.returncode != 0
        assert "Error" in result.stderr or "Configuration Error" in result.stderr


def test_cli_output_format_json():
    """Test JSON output format."""
    import subprocess

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
""".strip(),
            encoding="utf-8",
        )

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "mailcli",
                "--output",
                "json",
                "account",
                "list",
            ],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": "src", "HOME": tmpdir},
        )
        assert result.returncode == 0

        import json

        data = json.loads(result.stdout)
        assert "name" in data[0] or "email" in data[0]


def test_config_file_not_found_error():
    """Test config file not found error."""
    from src.mailcli.infra.config import get_config

    with tempfile.TemporaryDirectory() as tmpdir:
        original_home = os.environ.get("HOME")
        try:
            os.environ["HOME"] = tmpdir
            with pytest.raises(FileNotFoundError):
                get_config()
        finally:
            if original_home:
                os.environ["HOME"] = original_home
            else:
                os.environ.pop("HOME", None)


def test_account_config_validation():
    """Test account config validation."""
    from src.mailcli.infra.config import AccountConfig, Config

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
    assert account.imap_host == "imap.example.com"
    assert account.imap_port == 993
    assert account.smtp_host == "smtp.example.com"
    assert account.smtp_port == 465
    assert account.use_ssl is True
    assert account.auth_raw is None

    config = Config(accounts={"test": account}, default_account="test")
    assert len(config.accounts) == 1
    assert config.default_account == "test"


def test_output_formatter():
    """Test output formatter."""
    from src.mailcli.infra.output import OutputFormatter

    formatter = OutputFormatter("plain")
    result = formatter.format({"test": "value"})
    assert "test" in result
    assert "value" in result

    formatter_json = OutputFormatter("json")
    result_json = formatter_json.format({"test": "value"})
    assert '"test"' in result_json
    assert '"value"' in result_json


def test_error_classes():
    """Test error classes."""
    from src.mailcli.infra.errors import (
        AuthenticationError,
        ConfigError,
        ConnectionError,
        MailCliError,
        TimeoutError,
    )

    assert issubclass(AuthenticationError, MailCliError)
    assert issubclass(ConfigError, MailCliError)
    assert issubclass(ConnectionError, MailCliError)
    assert issubclass(TimeoutError, MailCliError)

    with pytest.raises(MailCliError):
        raise MailCliError("Test error")

    with pytest.raises(AuthenticationError):
        raise AuthenticationError("Auth failed")

    with pytest.raises(ConfigError):
        raise ConfigError("Config error")

    with pytest.raises(ConnectionError):
        raise ConnectionError("Connection failed")

    with pytest.raises(TimeoutError):
        raise TimeoutError("Timeout")
