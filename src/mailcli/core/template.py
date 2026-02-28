"""Template business logic."""

from __future__ import annotations

from typing import Any


PROVIDERS: dict[str, dict[str, Any]] = {
    "exmail": {
        "imap_host": "imap.exmail.qq.com",
        "imap_port": 993,
        "smtp_host": "smtp.exmail.qq.com",
        "smtp_port": 465,
        "use_ssl": True,
        "quirks_provider": "exmail",
    },
    "gmail": {
        "imap_host": "imap.gmail.com",
        "imap_port": 993,
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 465,
        "use_ssl": True,
        "quirks_provider": "gmail",
    },
    "m365": {
        "imap_host": "outlook.office365.com",
        "imap_port": 993,
        "smtp_host": "smtp.office365.com",
        "smtp_port": 587,
        "use_ssl": False,
        "quirks_provider": "m365",
    },
}


def template_list_providers() -> list[dict[str, Any]]:
    """List supported provider templates."""
    return [
        {
            "provider": name,
            "imap": f"{cfg['imap_host']}:{cfg['imap_port']}",
            "smtp": f"{cfg['smtp_host']}:{cfg['smtp_port']}",
            "use_ssl": cfg["use_ssl"],
        }
        for name, cfg in PROVIDERS.items()
    ]


def template_render_account(provider: str, account: str, email: str) -> dict[str, Any]:
    """Render TOML snippet for provider account setup."""
    lowered = provider.strip().lower()
    if lowered not in PROVIDERS:
        supported = ", ".join(sorted(PROVIDERS.keys()))
        raise ValueError(f"Unsupported provider '{provider}'. Supported: {supported}")

    cfg = PROVIDERS[lowered]
    snippet = "\n".join(
        [
            f'default_account = "{account}"',
            "",
            f"[accounts.{account}]",
            f'email = "{email}"',
            f"use_ssl = {str(cfg['use_ssl']).lower()}",
            "",
            f"[accounts.{account}.imap]",
            f'host = "{cfg["imap_host"]}"',
            f"port = {cfg['imap_port']}",
            "",
            f"[accounts.{account}.smtp]",
            f'host = "{cfg["smtp_host"]}"',
            f"port = {cfg['smtp_port']}",
            "",
            f"[accounts.{account}.auth]",
            'raw = "your_app_password_or_token"',
            '# cmd = "security find-generic-password -w -s mailcli-token"',
            "",
            "[quirks]",
            f'provider = "{cfg["quirks_provider"]}"',
        ]
    )

    return {
        "provider": lowered,
        "account": account,
        "email": email,
        "snippet": snippet,
    }
