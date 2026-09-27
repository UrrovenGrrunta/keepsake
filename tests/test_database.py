import sqlite3
from pathlib import Path
from uuid import uuid4

from keepsake.storage.database import connect_database, initialize_database
from keepsake.storage.person_repository import get_person


def test_connect_database_configures_connection(tmp_path: Path) -> None:
    database_path = tmp_path / "data" / "keepsake.db"
    connection = connect_database(database_path)

    try:
        assert database_path.is_file()
        assert connection.row_factory is sqlite3.Row

        foreign_keys = connection.execute(
            "PRAGMA foreign_keys"
        ).fetchone()[0]

        assert foreign_keys == 1
    finally:
        connection.close()


def test_initialize_database_upgrades_existing_people_table(
    tmp_path: Path,
) -> None:
    connection = connect_database(tmp_path / "keepsake.db")
    person_id = uuid4()

    try:
        with connection:
            connection.execute(
                """
                CREATE TABLE people (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    bio TEXT
                )
                """
            )
            connection.execute(
                "INSERT INTO people (id, name, bio) VALUES (?, ?, ?)",
                (str(person_id), "Tim", "Existing person"),
            )

        initialize_database(connection)
        initialize_database(connection)

        person = get_person(connection, person_id)
        assert person is not None
        assert person.name == "Tim"
        assert person.bio == "Existing person"
        assert person.profile_photo is None

        columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(people)")
        }
        assert "profile_photo_id" in columns
    finally:
        connection.close()


def test_initialize_database_creates_people_table(
    tmp_path: Path
) -> None:
    database_path = tmp_path / "keepsake.db"
    connection = connect_database(database_path)

    try:
        initialize_database(connection)

        table = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table' AND name = 'people'
            """
        ).fetchone()

        assert table is not None
        assert table["name"] == "people"
    finally:
        connection.close()
