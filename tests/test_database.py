import sqlite3

from pathlib import Path
from keepsake.storage.database import connect_database, initialize_database


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