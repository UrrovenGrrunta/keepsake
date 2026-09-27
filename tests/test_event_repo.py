import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pytest

from keepsake.domain.event import Event
from keepsake.domain.person import Person
from keepsake.storage.database import connect_database, initialize_database
from keepsake.storage.event_repository import (
    delete_event,
    get_event,
    list_events,
    save_event,
    update_event,
)
from keepsake.storage.person_repository import delete_person, save_person


def test_event_round_trip_update_list_and_delete(tmp_path: Path) -> None:
    connection = connect_database(tmp_path / "keepsake.db")
    initialize_database(connection)
    alice = Person(name="Alice")
    bob = Person(name="Bob")
    start = datetime(2025, 2, 3, 10, 30, 1, 123456, UTC)
    event = Event(
        title="Concert", starts_at=start,
        ends_at=start + timedelta(hours=2),
        all_day=False, participants=[bob, alice, bob],
    )
    try:
        save_person(connection, alice)
        save_person(connection, bob)
        save_event(connection, event)
        assert get_event(connection, event.id) == event
        assert list_events(connection) == [event]
        assert list_events(connection, alice.id) == [event]
        assert list_events(connection, uuid4()) == []

        event.title = "Updated concert"
        event.ends_at = None
        event.all_day = True
        event.participants = [alice]
        assert update_event(connection, event)
        assert get_event(connection, event.id) == event
        assert list_events(connection, bob.id) == []
        assert not update_event(connection, Event(id=uuid4(), title="Unknown", starts_at=start))

        assert delete_event(connection, event.id)
        assert get_event(connection, event.id) is None
        assert not delete_event(connection, event.id)
    finally:
        connection.close()


def test_event_links_cascade_and_failed_update_rolls_back(tmp_path: Path) -> None:
    connection = connect_database(tmp_path / "keepsake.db")
    initialize_database(connection)
    alice = Person(name="Alice")
    missing = Person(name="Missing")
    event = Event(title="Trip", starts_at=datetime.now(UTC), participants=[alice])
    try:
        save_person(connection, alice)
        save_event(connection, event)
        event.title = "Broken update"
        event.participants = [missing]
        with pytest.raises(sqlite3.IntegrityError):
            update_event(connection, event)
        loaded = get_event(connection, event.id)
        assert loaded is not None
        assert loaded.title == "Trip"
        assert loaded.participants == [alice]

        delete_person(connection, alice.id)
        loaded = get_event(connection, event.id)
        assert loaded is not None
        assert loaded.participants == []
    finally:
        connection.close()


def test_event_save_with_missing_participant_rolls_back(tmp_path: Path) -> None:
    connection = connect_database(tmp_path / "keepsake.db")
    initialize_database(connection)
    event = Event(
        title="Unstored participant",
        starts_at=datetime.now(UTC),
        participants=[Person(name="Missing")],
    )
    try:
        with pytest.raises(sqlite3.IntegrityError):
            save_event(connection, event)
        assert get_event(connection, event.id) is None
    finally:
        connection.close()
