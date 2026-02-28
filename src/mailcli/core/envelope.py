"""Envelope business logic."""

from __future__ import annotations

from email.utils import parsedate_to_datetime
from typing import Any

from ..infra import get_config
from ..infra.connections import IMAPAdapter


def envelope_list(
    account_name: str,
    folder: str = "INBOX",
    limit: int = 50,
    sort_by: str = "date",
    order: str = "desc",
    page: int = 1,
    page_size: int | None = None,
    threaded: bool = False,
) -> list[dict[str, Any]]:
    """List envelopes from a folder."""
    config = get_config()
    account = config.get_account(account_name)

    effective_page_size = page_size or limit
    fetch_limit = max(limit, page * effective_page_size)

    adapter = IMAPAdapter(account)
    adapter.connect()
    try:
        envelopes = adapter.list_envelopes(folder, fetch_limit)
    finally:
        adapter.disconnect()

    return _shape_envelopes(
        envelopes,
        sort_by=sort_by,
        order=order,
        page=page,
        page_size=effective_page_size,
        threaded=threaded,
    )


def envelope_search(
    account_name: str,
    query: str,
    folder: str = "INBOX",
    sort_by: str = "date",
    order: str = "desc",
    page: int = 1,
    page_size: int = 50,
    threaded: bool = False,
) -> list[dict[str, Any]]:
    """Search envelopes by query."""
    config = get_config()
    account = config.get_account(account_name)

    adapter = IMAPAdapter(account)
    adapter.connect()
    try:
        envelopes = adapter.search_envelopes(query, folder)
    finally:
        adapter.disconnect()

    return _shape_envelopes(
        envelopes,
        sort_by=sort_by,
        order=order,
        page=page,
        page_size=page_size,
        threaded=threaded,
    )


def _shape_envelopes(
    envelopes: list[dict[str, Any]],
    sort_by: str,
    order: str,
    page: int,
    page_size: int,
    threaded: bool,
) -> list[dict[str, Any]]:
    """Sort, paginate, and optionally group envelopes by thread."""
    page = max(1, page)
    page_size = max(1, page_size)

    sorted_envelopes = sorted(
        envelopes,
        key=lambda item: _sort_value(item, sort_by),
        reverse=order == "desc",
    )

    start = (page - 1) * page_size
    end = start + page_size
    paged = sorted_envelopes[start:end]

    if not threaded:
        return paged

    threads: dict[str, list[dict[str, Any]]] = {}
    for envelope in paged:
        key = _thread_key(envelope.get("subject", ""))
        threads.setdefault(key, []).append(envelope)

    return [
        {
            "thread_key": key,
            "count": len(items),
            "messages": items,
        }
        for key, items in threads.items()
    ]


def _thread_key(subject: str) -> str:
    """Build a coarse thread key from subject."""
    cleaned = subject.strip()
    while True:
        lowered = cleaned.lower()
        if lowered.startswith("re:"):
            cleaned = cleaned[3:].strip()
            continue
        if lowered.startswith("fw:"):
            cleaned = cleaned[3:].strip()
            continue
        if lowered.startswith("fwd:"):
            cleaned = cleaned[4:].strip()
            continue
        break
    return cleaned.lower()


def _sort_value(envelope: dict[str, Any], sort_by: str) -> Any:
    """Get sortable value from envelope."""
    lowered = sort_by.lower()
    if lowered == "size":
        return int(envelope.get("size", 0) or 0)
    if lowered == "subject":
        return str(envelope.get("subject", "")).lower()
    if lowered == "from":
        return str(envelope.get("from", "")).lower()
    if lowered == "date":
        date_str = str(envelope.get("date", ""))
        try:
            return parsedate_to_datetime(date_str)
        except (TypeError, ValueError):
            return parsedate_to_datetime("Thu, 01 Jan 1970 00:00:00 +0000")
    return str(envelope.get(lowered, "")).lower()
