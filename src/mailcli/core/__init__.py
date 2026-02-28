"""Core business logic."""

from .account import account_list, account_set_default, diagnose_account
from .attachment import attachment_download, attachment_list
from .envelope import envelope_list, envelope_search
from .flag import flag_add, flag_remove
from .folder import (
    folder_create,
    folder_delete,
    folder_expunge,
    folder_list,
    folder_purge,
)
from .message import (
    message_copy,
    message_delete,
    message_export,
    message_forward,
    message_move,
    message_read,
    message_reply,
    message_send,
    message_write,
)
from .template import template_list_providers, template_render_account

__all__ = [
    "account_list",
    "account_set_default",
    "diagnose_account",
    "envelope_list",
    "envelope_search",
    "folder_list",
    "folder_create",
    "folder_delete",
    "folder_expunge",
    "folder_purge",
    "message_read",
    "message_send",
    "message_write",
    "message_export",
    "message_reply",
    "message_forward",
    "message_copy",
    "message_move",
    "message_delete",
    "flag_add",
    "flag_remove",
    "attachment_list",
    "attachment_download",
    "template_list_providers",
    "template_render_account",
]
