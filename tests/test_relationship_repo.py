import sqlite3
from pathlib import Path
from uuid import uuid4

import pytest

from keepsake.domain.person import Person
from keepsake.domain.relationship import (
    Relationship,
    RelationshipRole,
    RelationshipSentiment,
    RelationshipSide,
)
from keepsake.storage.database import connect_database, initialize_database
from keepsake.storage.person_repository import delete_person, save_person
from keepsake.storage.relationship_repository import (
    delete_relationship,
    get_relationship,
    list_relationships,
    save_relationship,
    update_relationship,
)


def test_relationship_round_trip_update_list_and_delete(tmp_path: Path) -> None:
    connection = connect_database(tmp_path / "keepsake.db")
    initialize_database(connection)
    alice = Person(name="Alice")
    bob = Person(name="Bob")
    charlie = Person(name="Charlie")
    relationship = Relationship(
        person_a=alice,
        person_b=bob,
        side_a_to_b=RelationshipSide(
            RelationshipRole.FRIEND, RelationshipSentiment.POSITIVE
        ),
        side_b_to_a=RelationshipSide(
            RelationshipRole.ACQUAINTANCE, RelationshipSentiment.NEUTRAL
        ),
    )
    try:
        for person in (alice, bob, charlie):
            save_person(connection, person)
        save_relationship(connection, relationship)
        assert get_relationship(connection, relationship.id) == relationship
        assert list_relationships(connection) == [relationship]
        assert list_relationships(connection, bob.id) == [relationship]
        assert list_relationships(connection, charlie.id) == []

        relationship.person_b = charlie
        relationship.side_b_to_a.role = RelationshipRole.COLLEAGUE
        assert update_relationship(connection, relationship)
        assert get_relationship(connection, relationship.id) == relationship
        assert list_relationships(connection, bob.id) == []
        assert list_relationships(connection, charlie.id) == [relationship]

        assert delete_relationship(connection, relationship.id)
        assert get_relationship(connection, relationship.id) is None
        assert not delete_relationship(connection, relationship.id)
        assert not update_relationship(connection, relationship)
        assert get_relationship(connection, uuid4()) is None
    finally:
        connection.close()


def test_relationship_rejects_missing_people_and_cascades(tmp_path: Path) -> None:
    connection = connect_database(tmp_path / "keepsake.db")
    initialize_database(connection)
    alice = Person(name="Alice")
    bob = Person(name="Bob")
    relationship = Relationship(alice, bob)
    try:
        save_person(connection, alice)
        with pytest.raises(sqlite3.IntegrityError):
            save_relationship(connection, relationship)
        save_person(connection, bob)
        save_relationship(connection, relationship)
        delete_person(connection, alice.id)
        assert get_relationship(connection, relationship.id) is None
    finally:
        connection.close()


def test_relationship_failed_update_keeps_existing_links(tmp_path: Path) -> None:
    connection = connect_database(tmp_path / "keepsake.db")
    initialize_database(connection)
    alice = Person(name="Alice")
    bob = Person(name="Bob")
    relationship = Relationship(alice, bob)
    try:
        save_person(connection, alice)
        save_person(connection, bob)
        save_relationship(connection, relationship)

        relationship.person_b = Person(name="Missing")
        with pytest.raises(sqlite3.IntegrityError):
            update_relationship(connection, relationship)

        loaded = get_relationship(connection, relationship.id)
        assert loaded is not None
        assert loaded.person_a == alice
        assert loaded.person_b == bob
    finally:
        connection.close()
