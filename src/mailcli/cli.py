"""Mail CLI entrypoint."""

from __future__ import annotations

import click
import sys
import traceback

from .infra.config import Config
from .infra.output import OutputFormatter
from .infra.errors import ConfigError, MailCliError


def handle_errors(ctx: click.Context, func) -> None:
    """Wrap command execution with error handling."""
    try:
        func()
    except ConfigError as e:
        if ctx.obj["output_format"] == "json":
            formatter = OutputFormatter("json")
            formatter.print(
                {
                    "error": "config_error",
                    "message": str(e),
                }
            )
        else:
            click.echo(f"Configuration Error: {e}", err=True)
            sys.exit(1)
    except MailCliError as e:
        error_name = type(e).__name__.replace("Error", " Error")
        if ctx.obj["output_format"] == "json":
            formatter = OutputFormatter("json")
            formatter.print(
                {
                    "error": type(e).__name__,
                    "message": str(e),
                }
            )
        else:
            click.echo(f"{error_name}: {e}", err=True)
            sys.exit(1)
    except Exception as e:
        if ctx.obj.get("debug", False):
            traceback.print_exc()
        if ctx.obj["output_format"] == "json":
            formatter = OutputFormatter("json")
            formatter.print(
                {
                    "error": "unexpected_error",
                    "message": f"Unexpected error: {e}",
                }
            )
        else:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)


@click.group()
@click.option(
    "--output",
    type=click.Choice(["plain", "json"]),
    default="plain",
    help="Output format",
)
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.pass_context
def main(ctx: click.Context, output: str, debug: bool) -> None:
    """Mail CLI - Email management from terminal."""
    ctx.ensure_object(dict)
    ctx.obj["output_format"] = output
    ctx.obj["debug"] = debug
    ctx.obj["formatter"] = OutputFormatter(output)


@main.group()
@click.pass_context
def account(ctx: click.Context) -> None:
    """Account configuration and management."""
    pass


@main.group()
@click.pass_context
def folder(ctx: click.Context) -> None:
    """Folder management."""
    pass


@main.group()
@click.pass_context
def envelope(ctx: click.Context) -> None:
    """Envelope operations (list, search)."""
    pass


@main.group()
@click.pass_context
def message(ctx: click.Context) -> None:
    """Message operations (read, write, send)."""
    pass


@main.group()
@click.pass_context
def attachment(ctx: click.Context) -> None:
    """Attachment operations."""
    pass


@main.group()
@click.pass_context
def flag(ctx: click.Context) -> None:
    """Flag operations."""
    pass


@account.command("list")
@click.pass_context
def account_list_cmd(ctx: click.Context) -> None:
    """List all configured accounts."""
    from .core import account_list

    def _execute():
        accounts = account_list()
        formatter = ctx.obj["formatter"]
        formatter.print(accounts)

    handle_errors(ctx, _execute)


@account.command("default")
@click.argument("name")
@click.pass_context
def account_set_default_cmd(ctx: click.Context, name: str) -> None:
    """Set default account."""
    from .core import account_set_default

    def _execute():
        result = account_set_default(name)
        formatter = ctx.obj["formatter"]
        formatter.print(result)

    handle_errors(ctx, _execute)


@account.command("diagnose")
@click.argument("name")
@click.pass_context
def account_diagnose_cmd(ctx: click.Context, name: str) -> None:
    """Diagnose account connectivity."""
    from .core import diagnose_account

    def _execute():
        results = diagnose_account(name)
        formatter = ctx.obj["formatter"]
        formatter.print(results)

    handle_errors(ctx, _execute)


@folder.command("list")
@click.option("--account", "-a", help="Account name")
@click.pass_context
def folder_list_cmd(ctx: click.Context, account: str | None) -> None:
    """List folders."""
    from .core import folder_list

    def _execute():
        account_name = account
        if not account_name:
            from .infra import get_config

            config = get_config()
            account_name = config.default_account
            if not account_name:
                raise ConfigError(
                    "No account specified and no default account set. "
                    "Use --account to specify an account."
                )

        folders = folder_list(account_name)
        formatter = ctx.obj["formatter"]
        formatter.print(folders)

    handle_errors(ctx, _execute)


@envelope.command("list")
@click.option("--account", "-a", help="Account name")
@click.option("--folder", "-f", default="INBOX", help="Folder name")
@click.option("--limit", "-l", default=50, help="Limit number of envelopes")
@click.pass_context
def envelope_list_cmd(
    ctx: click.Context, account: str | None, folder: str, limit: int
) -> None:
    """List envelopes."""
    from .core import envelope_list

    def _execute():
        account_name = account
        if not account_name:
            from .infra import get_config

            config = get_config()
            account_name = config.default_account
            if not account_name:
                raise ConfigError(
                    "No account specified and no default account set. "
                    "Use --account to specify an account."
                )

        envelopes = envelope_list(account_name, folder, limit)
        formatter = ctx.obj["formatter"]
        formatter.print(envelopes)

    handle_errors(ctx, _execute)


@envelope.command("search")
@click.option("--account", "-a", help="Account name")
@click.option("--folder", "-f", default="INBOX", help="Folder name")
@click.argument("query")
@click.pass_context
def envelope_search_cmd(
    ctx: click.Context, account: str | None, folder: str, query: str
) -> None:
    """Search envelopes."""
    from .core import envelope_search

    def _execute():
        account_name = account
        if not account_name:
            from .infra import get_config

            config = get_config()
            account_name = config.default_account
            if not account_name:
                raise ConfigError(
                    "No account specified and no default account set. "
                    "Use --account to specify an account."
                )

        envelopes = envelope_search(account_name, query, folder)
        formatter = ctx.obj["formatter"]
        formatter.print(envelopes)

    handle_errors(ctx, _execute)


@message.command("read")
@click.option("--account", "-a", help="Account name")
@click.option("--folder", "-f", default="INBOX", help="Folder name")
@click.argument("msg_id")
@click.pass_context
def message_read_cmd(
    ctx: click.Context, account: str | None, folder: str, msg_id: str
) -> None:
    """Read a message."""
    from .core import message_read

    def _execute():
        account_name = account
        if not account_name:
            from .infra import get_config

            config = get_config()
            account_name = config.default_account
            if not account_name:
                raise ConfigError(
                    "No account specified and no default account set. "
                    "Use --account to specify an account."
                )

        message = message_read(account_name, msg_id, folder)
        formatter = ctx.obj["formatter"]
        formatter.print(message)

    handle_errors(ctx, _execute)


@message.command("send")
@click.option("--account", "-a", help="Account name")
@click.option("--to", "-t", required=True, help="Recipient email")
@click.option("--subject", "-s", required=True, help="Subject")
@click.option("--body", "-b", required=True, help="Message body")
@click.pass_context
def message_send_cmd(
    ctx: click.Context, account: str | None, to: str, subject: str, body: str
) -> None:
    """Send a simple text message."""
    from .core import message_send

    def _execute():
        account_name = account
        if not account_name:
            from .infra import get_config

            config = get_config()
            account_name = config.default_account
            if not account_name:
                raise ConfigError(
                    "No account specified and no default account set. "
                    "Use --account to specify an account."
                )

        result = message_send(account_name, to, subject, body)
        formatter = ctx.obj["formatter"]
        formatter.print(result)

    handle_errors(ctx, _execute)


@attachment.command("list")
@click.option("--account", "-a", help="Account name")
@click.option("--folder", "-f", default="INBOX", help="Folder name")
@click.argument("msg_id")
@click.pass_context
def attachment_list_cmd(
    ctx: click.Context, account: str | None, folder: str, msg_id: str
) -> None:
    """List attachments from a message."""
    from .core import attachment_list

    def _execute():
        account_name = account
        if not account_name:
            from .infra import get_config

            config = get_config()
            account_name = config.default_account
            if not account_name:
                raise ConfigError(
                    "No account specified and no default account set. "
                    "Use --account to specify an account."
                )

        attachments = attachment_list(account_name, msg_id, folder)
        formatter = ctx.obj["formatter"]
        formatter.print(attachments)

    handle_errors(ctx, _execute)


@attachment.command("download")
@click.option("--account", "-a", help="Account name")
@click.option("--folder", "-f", default="INBOX", help="Folder name")
@click.option("--output", "-o", default=".", help="Output directory")
@click.argument("msg_id")
@click.argument("filename")
@click.pass_context
def attachment_download_cmd(
    ctx: click.Context,
    account: str | None,
    folder: str,
    output: str,
    msg_id: str,
    filename: str,
) -> None:
    """Download an attachment."""
    from .core import attachment_download

    def _execute():
        account_name = account
        if not account_name:
            from .infra import get_config

            config = get_config()
            account_name = config.default_account
            if not account_name:
                raise ConfigError(
                    "No account specified and no default account set. "
                    "Use --account to specify an account."
                )

        result = attachment_download(account_name, msg_id, filename, output, folder)
        formatter = ctx.obj["formatter"]
        formatter.print(result)

    handle_errors(ctx, _execute)
