import sqlite3
from datetime import datetime
from uuid import UUID

from ..domain.journal import JournalEntry, PhotoBlock, TextBlock
from .database import atomic_write
from .event_repository import get_event
from .photo_repository import get_photo


def _journal_entry_from_row(
    connection: sqlite3.Connection,
    row: sqlite3.Row,
) -> JournalEntry:
    event = None
    if row["event_id"] is not None:
        event = get_event(connection, UUID(row["event_id"]))
        if event is None:
            raise ValueError("Journal entry refers to a missing event")

    block_rows = connection.execute(
        """
        SELECT kind, text, photo_id FROM journal_blocks
        WHERE entry_id = ? ORDER BY position
        """,
        (row["id"],),
    ).fetchall()
    blocks = []
    for block_row in block_rows:
        if block_row["kind"] == "text":
            blocks.append(TextBlock(block_row["text"]))
        else:
            photo = get_photo(connection, UUID(block_row["photo_id"]))
            if photo is None:
                raise ValueError("Journal block refers to a missing photo")
            blocks.append(PhotoBlock(photo))

    return JournalEntry(
        id=UUID(row["id"]),
        title=row["title"],
        created_at=datetime.fromisoformat(row["created_at"]),
        event=event,
        blocks=blocks,
    )


def _save_blocks(
    connection: sqlite3.Connection,
    entry: JournalEntry,
) -> None:
    rows = []
    for position, block in enumerate(entry.blocks):
        if isinstance(block, TextBlock):
            rows.append((str(entry.id), position, "text", block.text, None))
        elif isinstance(block, PhotoBlock):
            rows.append((str(entry.id), position, "photo", None, str(block.photo.id)))
        else:
            raise TypeError(f"Unsupported journal block: {type(block).__name__}")
    connection.executemany(
        """
        INSERT INTO journal_blocks (entry_id, position, kind, text, photo_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        rows,
    )


def save_journal_entry(
    connection: sqlite3.Connection,
    entry: JournalEntry,
) -> None:
    with atomic_write(connection):
        connection.execute(
            """
            INSERT INTO journal_entries (id, title, created_at, event_id)
            VALUES (?, ?, ?, ?)
            """,
            (
                str(entry.id), entry.title, entry.created_at.isoformat(),
                str(entry.event.id) if entry.event is not None else None,
            ),
        )
        _save_blocks(connection, entry)


def get_journal_entry(
    connection: sqlite3.Connection,
    entry_id: UUID,
) -> JournalEntry | None:
    row = connection.execute(
        "SELECT * FROM journal_entries WHERE id = ?",
        (str(entry_id),),
    ).fetchone()
    if row is None:
        return None
    return _journal_entry_from_row(connection, row)


def list_journal_entries(
    connection: sqlite3.Connection,
    event_id: UUID | None = None,
) -> list[JournalEntry]:
    if event_id is None:
        rows = connection.execute(
            "SELECT * FROM journal_entries ORDER BY created_at, id"
        ).fetchall()
    else:
        rows = connection.execute(
            """
            SELECT * FROM journal_entries
            WHERE event_id = ? ORDER BY created_at, id
            """,
            (str(event_id),),
        ).fetchall()
    return [_journal_entry_from_row(connection, row) for row in rows]


def update_journal_entry(
    connection: sqlite3.Connection,
    entry: JournalEntry,
) -> bool:
    with atomic_write(connection):
        cursor = connection.execute(
            """
            UPDATE journal_entries SET title = ?, created_at = ?, event_id = ?
            WHERE id = ?
            """,
            (
                entry.title, entry.created_at.isoformat(),
                str(entry.event.id) if entry.event is not None else None,
                str(entry.id),
            ),
        )
        if cursor.rowcount == 0:
            return False
        connection.execute(
            "DELETE FROM journal_blocks WHERE entry_id = ?",
            (str(entry.id),),
        )
        _save_blocks(connection, entry)
    return True


def delete_journal_entry(
    connection: sqlite3.Connection,
    entry_id: UUID,
) -> bool:
    with atomic_write(connection):
        cursor = connection.execute(
            "DELETE FROM journal_entries WHERE id = ?",
            (str(entry_id),),
        )
    return cursor.rowcount == 1
