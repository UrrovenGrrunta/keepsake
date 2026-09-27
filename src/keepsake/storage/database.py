import sqlite3
from pathlib import Path


def connect_database(database_path: Path) -> sqlite3.Connection:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute(
        "PRAGMA foreign_keys = ON"
        )
    return connection

def initialize_database(connection: sqlite3.Connection) -> None:
    with connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS people (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                bio TEXT
            )
            """
        )