from datetime import UTC, datetime
from pathlib import Path

from keepsake.domain.event import Event
from keepsake.domain.journal import JournalEntry, PhotoBlock, TextBlock
from keepsake.domain.person import Person
from keepsake.domain.photo import Photo
from keepsake.domain.relationship import (
    Relationship,
    RelationshipRole,
    RelationshipSentiment,
    RelationshipSide,
)
from keepsake.storage.database import connect_database, initialize_database
from keepsake.storage.event_repository import get_event, save_event
from keepsake.storage.journal_repository import get_journal_entry, save_journal_entry
from keepsake.storage.person_repository import get_person, save_person
from keepsake.storage.photo_repository import get_photo, save_photo
from keepsake.storage.relationship_repository import get_relationship, save_relationship


def test_all_entities_survive_reopening_database(tmp_path: Path) -> None:
    database_path = tmp_path / "keepsake.db"
    photo = Photo(path=Path("photos/profile.png"), alt_text="Alice")
    alice = Person(name="Alice", profile_photo=photo, bio=None)
    bob = Person(name="Bob")
    relationship = Relationship(
        person_a=alice,
        person_b=bob,
        side_a_to_b=RelationshipSide(
            RelationshipRole.FRIEND, RelationshipSentiment.POSITIVE
        ),
        side_b_to_a=RelationshipSide(
            RelationshipRole.COLLEAGUE, RelationshipSentiment.NEUTRAL
        ),
    )
    event = Event(
        title="Meeting", starts_at=datetime(2025, 4, 1, 10, tzinfo=UTC),
        participants=[bob, alice],
    )
    entry = JournalEntry(
        created_at=datetime(2025, 4, 1, 12, tzinfo=UTC),
        event=event,
        blocks=[TextBlock("Before"), PhotoBlock(photo), TextBlock("After")],
    )

    connection = connect_database(database_path)
    try:
        initialize_database(connection)
        save_photo(connection, photo)
        save_person(connection, alice)
        save_person(connection, bob)
        save_relationship(connection, relationship)
        save_event(connection, event)
        save_journal_entry(connection, entry)
    finally:
        connection.close()

    connection = connect_database(database_path)
    try:
        initialize_database(connection)
        assert get_photo(connection, photo.id) == photo
        assert get_person(connection, alice.id) == alice
        assert get_relationship(connection, relationship.id) == relationship
        assert get_event(connection, event.id) == event
        assert get_journal_entry(connection, entry.id) == entry
    finally:
        connection.close()
