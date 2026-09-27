import sqlite3

from uuid import UUID
from pathlib import Path

from ..domain.photo import Photo
from .database import atomic_write


def save_photo(
    connection: sqlite3.Connection,
    photo: Photo,
) -> None:
    with atomic_write(connection):
        connection.execute(
            """
            INSERT INTO photos (id, path, alt_text, title)
            VALUES (?, ?, ?, ?)
            """,
            (
                str(photo.id),
                photo.path.as_posix(),
                photo.alt_text,
                photo.title,
            ),
        )


def get_photo(
    connection: sqlite3.Connection,
    photo_id: UUID,
) -> Photo | None:
    row = connection.execute(
        """
        SELECT id, path, alt_text, title
        FROM photos
        WHERE id = ?
        """,
        (str(photo_id),),
    ).fetchone()

    if row is None:
        return None

    return Photo(
        id=UUID(row["id"]),
        path=Path(row["path"]),
        alt_text=row["alt_text"],
        title=row["title"],
    )


def list_photos(
    connection: sqlite3.Connection,
) -> list[Photo]:
    rows = connection.execute(
        """
        SELECT id, path, alt_text, title
        FROM photos
        ORDER BY path COLLATE NOCASE, id
        """
    ).fetchall()

    return [
        Photo(
            id=UUID(row["id"]),
            path=Path(row["path"]),
            alt_text=row["alt_text"],
            title=row["title"],
        )
        for row in rows
    ]


def update_photo(
    connection: sqlite3.Connection,
    photo: Photo,
) -> bool:
    with atomic_write(connection):
        cursor = connection.execute(
            """
            UPDATE photos
            SET path = ?, alt_text = ?, title = ?
            WHERE id = ?
            """,
            (
                photo.path.as_posix(),
                photo.alt_text,
                photo.title,
                str(photo.id),
            ),
        )

    return cursor.rowcount == 1


def delete_photo(
    connection: sqlite3.Connection,
    photo_id: UUID,
) -> bool:
    with atomic_write(connection):
        cursor = connection.execute(
            """
            DELETE FROM photos
            WHERE id = ?
            """,
            (str(photo_id),),
        )

    return cursor.rowcount == 1
