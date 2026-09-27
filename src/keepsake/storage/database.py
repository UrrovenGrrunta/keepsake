import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


@contextmanager
def atomic_write(connection: sqlite3.Connection) -> Iterator[None]:
    """Keep a repository write atomic without committing the caller's transaction."""
    connection.execute("SAVEPOINT repository_write")
    try:
        yield
    except BaseException:
        connection.execute("ROLLBACK TO SAVEPOINT repository_write")
        connection.execute("RELEASE SAVEPOINT repository_write")
        raise
    else:
        connection.execute("RELEASE SAVEPOINT repository_write")


def connect_database(database_path: Path) -> sqlite3.Connection:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(
    connection: sqlite3.Connection,
) -> None:
    with atomic_write(connection):
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS photos (
                id TEXT PRIMARY KEY,
                path TEXT NOT NULL,
                alt_text TEXT,
                title TEXT
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS people (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                bio TEXT,
                profile_photo_id TEXT,
                FOREIGN KEY (profile_photo_id)
                    REFERENCES photos (id)
                    ON DELETE SET NULL
            )
            """
        )

        columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(people)")
        }
        if "profile_photo_id" not in columns:
            connection.execute(
                """
                ALTER TABLE people
                ADD COLUMN profile_photo_id TEXT
                    REFERENCES photos (id)
                    ON DELETE SET NULL
                """
            )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS relationships (
                id TEXT PRIMARY KEY,
                person_a_id TEXT NOT NULL REFERENCES people (id)
                    ON DELETE CASCADE,
                person_b_id TEXT NOT NULL REFERENCES people (id)
                    ON DELETE CASCADE,
                a_to_b_role TEXT NOT NULL,
                a_to_b_sentiment TEXT NOT NULL,
                b_to_a_role TEXT NOT NULL,
                b_to_a_sentiment TEXT NOT NULL,
                CHECK (person_a_id <> person_b_id)
            )
            """
        )
        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS relationships_unordered_pair
            ON relationships (
                min(person_a_id, person_b_id),
                max(person_a_id, person_b_id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                starts_at TEXT NOT NULL,
                ends_at TEXT,
                all_day INTEGER NOT NULL CHECK (all_day IN (0, 1))
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS event_participants (
                event_id TEXT NOT NULL REFERENCES events (id)
                    ON DELETE CASCADE,
                position INTEGER NOT NULL,
                person_id TEXT NOT NULL REFERENCES people (id)
                    ON DELETE CASCADE,
                PRIMARY KEY (event_id, position)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS journal_entries (
                id TEXT PRIMARY KEY,
                title TEXT,
                created_at TEXT NOT NULL,
                event_id TEXT REFERENCES events (id)
                    ON DELETE SET NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS journal_blocks (
                entry_id TEXT NOT NULL REFERENCES journal_entries (id)
                    ON DELETE CASCADE,
                position INTEGER NOT NULL,
                kind TEXT NOT NULL CHECK (kind IN ('text', 'photo')),
                text TEXT,
                photo_id TEXT REFERENCES photos (id)
                    ON DELETE RESTRICT,
                PRIMARY KEY (entry_id, position),
                CHECK (
                    (kind = 'text' AND text IS NOT NULL AND photo_id IS NULL)
                    OR
                    (kind = 'photo' AND text IS NULL AND photo_id IS NOT NULL)
                )
            )
            """
        )
        # Existing databases may still have the old CASCADE foreign key.
        connection.execute(
            """
            CREATE TRIGGER IF NOT EXISTS prevent_used_photo_deletion
            BEFORE DELETE ON photos
            WHEN EXISTS (
                SELECT 1 FROM journal_blocks WHERE photo_id = OLD.id
            )
            BEGIN
                SELECT RAISE(ABORT, 'photo is used by a journal block');
            END
            """
        )
