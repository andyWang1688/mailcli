"""Mail CLI entrypoint."""

from __future__ import annotations

import click
import sys
import traceback

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
        if ctx.obj.get("trace", False):
            traceback.print_exc()
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
@click.option("--trace", is_flag=True, help="Print full traceback on errors")
@click.pass_context
def main(ctx: click.Context, output: str, debug: bool, trace: bool) -> None:
    """Mail CLI - Email management from terminal."""
    ctx.ensure_object(dict)
    ctx.obj["output_format"] = output
    ctx.obj["debug"] = debug
    ctx.obj["trace"] = trace
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


@main.group()
@click.pass_context
def template(ctx: click.Context) -> None:
    """Template rendering utilities."""
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


@folder.command("create")
@click.option("--account", "-a", help="Account name")
@click.argument("name")
@click.pass_context
def folder_create_cmd(ctx: click.Context, account: str | None, name: str) -> None:
    """Create folder."""
    from .core import folder_create

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

        result = folder_create(account_name, name)
        formatter = ctx.obj["formatter"]
        formatter.print(result)

    handle_errors(ctx, _execute)


@folder.command("delete")
@click.option("--account", "-a", help="Account name")
@click.argument("name")
@click.pass_context
def folder_delete_cmd(ctx: click.Context, account: str | None, name: str) -> None:
    """Delete folder."""
    from .core import folder_delete

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

        result = folder_delete(account_name, name)
        formatter = ctx.obj["formatter"]
        formatter.print(result)

    handle_errors(ctx, _execute)


@folder.command("expunge")
@click.option("--account", "-a", help="Account name")
@click.option("--folder", "-f", default="INBOX", help="Folder name")
@click.pass_context
def folder_expunge_cmd(ctx: click.Context, account: str | None, folder: str) -> None:
    """Expunge deleted messages in folder."""
    from .core import folder_expunge

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

        result = folder_expunge(account_name, folder)
        formatter = ctx.obj["formatter"]
        formatter.print(result)

    handle_errors(ctx, _execute)


@folder.command("purge")
@click.option("--account", "-a", help="Account name")
@click.option("--folder", "-f", default="INBOX", help="Folder name")
@click.pass_context
def folder_purge_cmd(ctx: click.Context, account: str | None, folder: str) -> None:
    """Purge all messages in folder."""
    from .core import folder_purge

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

        result = folder_purge(account_name, folder)
        formatter = ctx.obj["formatter"]
        formatter.print(result)

    handle_errors(ctx, _execute)


@envelope.command("list")
@click.option("--account", "-a", help="Account name")
@click.option("--folder", "-f", default="INBOX", help="Folder name")
@click.option("--limit", "-l", default=50, help="Limit number of envelopes")
@click.option(
    "--sort-by",
    type=click.Choice(["date", "size", "subject", "from"]),
    default="date",
    help="Sort field",
)
@click.option("--order", type=click.Choice(["asc", "desc"]), default="desc")
@click.option("--page", type=int, default=1, help="Page number (1-based)")
@click.option("--page-size", type=int, default=50, help="Page size")
@click.option("--threaded", is_flag=True, help="Group result by thread")
@click.pass_context
def envelope_list_cmd(
    ctx: click.Context,
    account: str | None,
    folder: str,
    limit: int,
    sort_by: str,
    order: str,
    page: int,
    page_size: int,
    threaded: bool,
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

        envelopes = envelope_list(
            account_name,
            folder,
            limit,
            sort_by=sort_by,
            order=order,
            page=page,
            page_size=page_size,
            threaded=threaded,
        )
        formatter = ctx.obj["formatter"]
        formatter.print(envelopes)

    handle_errors(ctx, _execute)


@envelope.command("search")
@click.option("--account", "-a", help="Account name")
@click.option("--folder", "-f", default="INBOX", help="Folder name")
@click.option(
    "--sort-by",
    type=click.Choice(["date", "size", "subject", "from"]),
    default="date",
    help="Sort field",
)
@click.option("--order", type=click.Choice(["asc", "desc"]), default="desc")
@click.option("--page", type=int, default=1, help="Page number (1-based)")
@click.option("--page-size", type=int, default=50, help="Page size")
@click.option("--threaded", is_flag=True, help="Group result by thread")
@click.argument("query")
@click.pass_context
def envelope_search_cmd(
    ctx: click.Context,
    account: str | None,
    folder: str,
    sort_by: str,
    order: str,
    page: int,
    page_size: int,
    threaded: bool,
    query: str,
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

        envelopes = envelope_search(
            account_name,
            query,
            folder,
            sort_by=sort_by,
            order=order,
            page=page,
            page_size=page_size,
            threaded=threaded,
        )
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


@message.command("write")
@click.option("--to", "-t", required=True, help="Recipient email")
@click.option("--subject", "-s", required=True, help="Subject")
@click.option("--body", "-b", required=True, help="Message body")
@click.option("--cc", help="CC recipients")
@click.option("--output", "-o", required=True, help="Output .eml path")
@click.pass_context
def message_write_cmd(
    ctx: click.Context,
    to: str,
    subject: str,
    body: str,
    cc: str | None,
    output: str,
) -> None:
    """Write local draft message."""
    from .core import message_write

    def _execute():
        result = message_write(to, subject, body, output, cc)
        formatter = ctx.obj["formatter"]
        formatter.print(result)

    handle_errors(ctx, _execute)


@message.command("export")
@click.option("--account", "-a", help="Account name")
@click.option("--folder", "-f", default="INBOX", help="Folder name")
@click.option("--output", "-o", required=True, help="Output file path")
@click.argument("msg_id")
@click.pass_context
def message_export_cmd(
    ctx: click.Context,
    account: str | None,
    folder: str,
    output: str,
    msg_id: str,
) -> None:
    """Export remote message to .eml."""
    from .core import message_export

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

        result = message_export(account_name, msg_id, output, folder)
        formatter = ctx.obj["formatter"]
        formatter.print(result)

    handle_errors(ctx, _execute)


@message.command("reply")
@click.option("--account", "-a", help="Account name")
@click.option("--folder", "-f", default="INBOX", help="Folder name")
@click.option("--body", "-b", required=True, help="Reply body")
@click.option("--reply-all", is_flag=True, help="Include original Cc")
@click.argument("msg_id")
@click.pass_context
def message_reply_cmd(
    ctx: click.Context,
    account: str | None,
    folder: str,
    body: str,
    reply_all: bool,
    msg_id: str,
) -> None:
    """Reply to a message."""
    from .core import message_reply

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

        result = message_reply(account_name, msg_id, body, folder, reply_all)
        formatter = ctx.obj["formatter"]
        formatter.print(result)

    handle_errors(ctx, _execute)


@message.command("forward")
@click.option("--account", "-a", help="Account name")
@click.option("--folder", "-f", default="INBOX", help="Folder name")
@click.option("--to", "-t", required=True, help="Forward recipient")
@click.option("--body", "-b", default="", help="Forward notes")
@click.argument("msg_id")
@click.pass_context
def message_forward_cmd(
    ctx: click.Context,
    account: str | None,
    folder: str,
    to: str,
    body: str,
    msg_id: str,
) -> None:
    """Forward a message."""
    from .core import message_forward

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

        result = message_forward(account_name, msg_id, to, body, folder)
        formatter = ctx.obj["formatter"]
        formatter.print(result)

    handle_errors(ctx, _execute)


@message.command("copy")
@click.option("--account", "-a", help="Account name")
@click.option("--from-folder", default="INBOX", help="Source folder")
@click.option("--to-folder", required=True, help="Destination folder")
@click.argument("msg_id")
@click.pass_context
def message_copy_cmd(
    ctx: click.Context,
    account: str | None,
    from_folder: str,
    to_folder: str,
    msg_id: str,
) -> None:
    """Copy a message."""
    from .core import message_copy

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

        result = message_copy(account_name, msg_id, to_folder, from_folder)
        formatter = ctx.obj["formatter"]
        formatter.print(result)

    handle_errors(ctx, _execute)


@message.command("move")
@click.option("--account", "-a", help="Account name")
@click.option("--from-folder", default="INBOX", help="Source folder")
@click.option("--to-folder", required=True, help="Destination folder")
@click.argument("msg_id")
@click.pass_context
def message_move_cmd(
    ctx: click.Context,
    account: str | None,
    from_folder: str,
    to_folder: str,
    msg_id: str,
) -> None:
    """Move a message."""
    from .core import message_move

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

        result = message_move(account_name, msg_id, to_folder, from_folder)
        formatter = ctx.obj["formatter"]
        formatter.print(result)

    handle_errors(ctx, _execute)


@message.command("delete")
@click.option("--account", "-a", help="Account name")
@click.option("--folder", "-f", default="INBOX", help="Folder name")
@click.option("--no-expunge", is_flag=True, help="Only mark deleted")
@click.argument("msg_id")
@click.pass_context
def message_delete_cmd(
    ctx: click.Context,
    account: str | None,
    folder: str,
    no_expunge: bool,
    msg_id: str,
) -> None:
    """Delete a message."""
    from .core import message_delete

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

        result = message_delete(account_name, msg_id, folder, expunge=not no_expunge)
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


@flag.command("add")
@click.option("--account", "-a", help="Account name")
@click.option("--folder", "-f", default="INBOX", help="Folder name")
@click.option(
    "--flag",
    "flag_name",
    required=True,
    type=click.Choice(["seen", "flagged"]),
    help="Flag name",
)
@click.argument("msg_id")
@click.pass_context
def flag_add_cmd(
    ctx: click.Context,
    account: str | None,
    folder: str,
    flag_name: str,
    msg_id: str,
) -> None:
    """Add a flag to message."""
    from .core import flag_add

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

        result = flag_add(account_name, msg_id, flag_name, folder)
        formatter = ctx.obj["formatter"]
        formatter.print(result)

    handle_errors(ctx, _execute)


@flag.command("remove")
@click.option("--account", "-a", help="Account name")
@click.option("--folder", "-f", default="INBOX", help="Folder name")
@click.option(
    "--flag",
    "flag_name",
    required=True,
    type=click.Choice(["seen", "flagged"]),
    help="Flag name",
)
@click.argument("msg_id")
@click.pass_context
def flag_remove_cmd(
    ctx: click.Context,
    account: str | None,
    folder: str,
    flag_name: str,
    msg_id: str,
) -> None:
    """Remove a flag from message."""
    from .core import flag_remove

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

        result = flag_remove(account_name, msg_id, flag_name, folder)
        formatter = ctx.obj["formatter"]
        formatter.print(result)

    handle_errors(ctx, _execute)


@template.command("list-providers")
@click.pass_context
def template_list_providers_cmd(ctx: click.Context) -> None:
    """List built-in account templates."""
    from .core import template_list_providers

    def _execute():
        formatter = ctx.obj["formatter"]
        formatter.print(template_list_providers())

    handle_errors(ctx, _execute)


@template.command("render")
@click.option(
    "--provider",
    required=True,
    type=click.Choice(["exmail", "gmail", "m365"]),
    help="Provider name",
)
@click.option("--account", "account_name", required=True, help="Account name")
@click.option("--email", required=True, help="Account email")
@click.pass_context
def template_render_cmd(
    ctx: click.Context,
    provider: str,
    account_name: str,
    email: str,
) -> None:
    """Render provider account TOML template."""
    from .core import template_render_account

    def _execute():
        formatter = ctx.obj["formatter"]
        formatter.print(template_render_account(provider, account_name, email))

    handle_errors(ctx, _execute)
