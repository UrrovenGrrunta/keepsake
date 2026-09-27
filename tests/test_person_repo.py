from pathlib import Path
from uuid import uuid4

from keepsake.domain.person import Person
from keepsake.storage.database import (
    connect_database,
    initialize_database,
)
from keepsake.storage.person_repository import (
    delete_person,
    get_person,
    list_people,
    save_person,
    update_person,
)


def create_test_database(
    tmp_path: Path,
):
    connection = connect_database(
        tmp_path / "keepsake.db"
    )
    initialize_database(connection)

    return connection


def test_person_can_be_saved_and_loaded(
    tmp_path: Path,
) -> None:
    connection = create_test_database(tmp_path)
    person = Person(
        name="Tim",
        bio="Guitar enjoyer",
    )

    try:
        save_person(connection, person)
        loaded_person = get_person(connection, person.id)

        assert loaded_person == person
    finally:
        connection.close()


def test_people_can_be_listed(
    tmp_path: Path,
) -> None:
    connection = create_test_database(tmp_path)
    person_b = Person(name="Bob")
    person_a = Person(name="Alice")

    try:
        save_person(connection, person_b)
        save_person(connection, person_a)

        people = list_people(connection)

        assert people == [person_a, person_b]
    finally:
        connection.close()


def test_person_can_be_updated_and_deleted(
    tmp_path: Path,
) -> None:
    connection = create_test_database(tmp_path)
    person = Person(name="Old name")

    try:
        save_person(connection, person)

        person.name = "New name"
        person.bio = "New bio"

        assert update_person(connection, person) is True
        assert get_person(connection, person.id) == person

        assert delete_person(connection, person.id) is True
        assert get_person(connection, person.id) is None

        assert delete_person(connection, person.id) is False
    finally:
        connection.close()


def test_get_person_returns_none_for_unknown_id(
    tmp_path: Path,
) -> None:
    connection = create_test_database(tmp_path)

    try:
        assert get_person(connection, uuid4()) is None
    finally:
        connection.close()