import sqlite3
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest

from keepsake.domain.event import Event
from keepsake.domain.journal import JournalEntry, PhotoBlock, TextBlock
from keepsake.domain.person import Person
from keepsake.domain.photo import Photo
from keepsake.storage.database import connect_database, initialize_database
from keepsake.storage.event_repository import delete_event, save_event
from keepsake.storage.journal_repository import (
    delete_journal_entry,
    get_journal_entry,
    list_journal_entries,
    save_journal_entry,
    update_journal_entry,
)
from keepsake.storage.person_repository import save_person
from keepsake.storage.photo_repository import delete_photo, save_photo


def test_journal_round_trip_update_list_and_delete(tmp_path: Path) -> None:
    connection = connect_database(tmp_path / "keepsake.db")
    initialize_database(connection)
    person = Person(name="Alice")
    photo = Photo(path=Path("photos/trip.jpg"), title="Trip")
    event = Event(
        title="Trip",
        starts_at=datetime(2025, 5, 2, 9, 30, tzinfo=timezone(timedelta(hours=2))),
        participants=[person],
    )
    entry = JournalEntry(
        title=None,
        created_at=datetime(2025, 5, 3, 12, 1, 2, 123456, UTC),
        event=event,
        blocks=[TextBlock("Before"), PhotoBlock(photo), TextBlock("After")],
    )
    try:
        save_person(connection, person)
        save_photo(connection, photo)
        save_event(connection, event)
        save_journal_entry(connection, entry)

        assert get_journal_entry(connection, entry.id) == entry
        assert list_journal_entries(connection) == [entry]
        assert list_journal_entries(connection, event.id) == [entry]
        assert list_journal_entries(connection, uuid4()) == []

        entry.title = "Updated"
        entry.created_at += timedelta(days=1)
        entry.event = None
        entry.blocks = [TextBlock("After"), PhotoBlock(photo), TextBlock("Before")]
        assert update_journal_entry(connection, entry)
        assert get_journal_entry(connection, entry.id) == entry
        assert list_journal_entries(connection, event.id) == []
        assert not update_journal_entry(connection, JournalEntry(id=uuid4()))

        assert delete_journal_entry(connection, entry.id)
        assert get_journal_entry(connection, entry.id) is None
        assert not delete_journal_entry(connection, entry.id)
    finally:
        connection.close()


def test_journal_links_and_failed_writes(tmp_path: Path) -> None:
    connection = connect_database(tmp_path / "keepsake.db")
    initialize_database(connection)
    photo = Photo(path=Path("photos/one.jpg"))
    event = Event(title="Trip", starts_at=datetime.now(UTC))
    entry = JournalEntry(event=event, blocks=[TextBlock("Start"), PhotoBlock(photo)])
    try:
        save_photo(connection, photo)
        save_event(connection, event)
        save_journal_entry(connection, entry)

        entry.title = "This must roll back"
        entry.blocks = [PhotoBlock(Photo(path=Path("photos/missing.jpg")))]
        with pytest.raises(sqlite3.IntegrityError):
            update_journal_entry(connection, entry)
        loaded = get_journal_entry(connection, entry.id)
        assert loaded is not None
        assert loaded.title is None
        assert loaded.blocks == [TextBlock("Start"), PhotoBlock(photo)]

        unsaved = JournalEntry(blocks=[PhotoBlock(Photo(path=Path("missing.jpg")))])
        with pytest.raises(sqlite3.IntegrityError):
            save_journal_entry(connection, unsaved)
        assert get_journal_entry(connection, unsaved.id) is None

        delete_event(connection, event.id)
        loaded = get_journal_entry(connection, entry.id)
        assert loaded is not None
        assert loaded.event is None

        delete_photo(connection, photo.id)
        loaded = get_journal_entry(connection, entry.id)
        assert loaded is not None
        assert loaded.blocks == [TextBlock("Start")]
    finally:
        connection.close()
