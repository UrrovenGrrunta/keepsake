import sqlite3

from uuid import UUID
from pathlib import Path

from ..domain.photo import Photo
from ..domain.person import Person
from .database import atomic_write


def person_from_row(row: sqlite3.Row) -> Person:
    profile_photo = None

    if row["photo_id"] is not None:
        profile_photo = Photo(
            id=UUID(row["photo_id"]),
            path=Path(row["photo_path"]),
            alt_text=row["photo_alt_text"],
            title=row["photo_title"],
        )

    return Person(
        id=UUID(row["person_id"]),
        name=row["person_name"],
        bio=row["person_bio"],
        profile_photo=profile_photo,
    )


def save_person(
    connection: sqlite3.Connection,
    person: Person,
) -> None:
    profile_photo_id = None

    if person.profile_photo is not None:
        profile_photo_id = str(person.profile_photo.id)

    with atomic_write(connection):
        connection.execute(
            """
            INSERT INTO people (
                id,
                name,
                bio,
                profile_photo_id
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                str(person.id),
                person.name,
                person.bio,
                profile_photo_id,
            ),
        )


def get_person(
    connection: sqlite3.Connection,
    person_id: UUID,
) -> Person | None:
    row = connection.execute(
        """
        SELECT
            people.id AS person_id,
            people.name AS person_name,
            people.bio AS person_bio,
            photos.id AS photo_id,
            photos.path AS photo_path,
            photos.alt_text AS photo_alt_text,
            photos.title AS photo_title
        FROM people
        LEFT JOIN photos
            ON people.profile_photo_id = photos.id
        WHERE people.id = ?
        """,
        (str(person_id),),
    ).fetchone()

    if row is None:
        return None

    return person_from_row(row)


def list_people(
    connection: sqlite3.Connection,
) -> list[Person]:
    rows = connection.execute(
        """
        SELECT
            people.id AS person_id,
            people.name AS person_name,
            people.bio AS person_bio,
            photos.id AS photo_id,
            photos.path AS photo_path,
            photos.alt_text AS photo_alt_text,
            photos.title AS photo_title
        FROM people
        LEFT JOIN photos
            ON people.profile_photo_id = photos.id
        ORDER BY people.name COLLATE NOCASE, people.id
        """
    ).fetchall()

    return [
        person_from_row(row)
        for row in rows
    ]


def update_person(
    connection: sqlite3.Connection,
    person: Person,
) -> bool:
    profile_photo_id = None

    if person.profile_photo is not None:
        profile_photo_id = str(person.profile_photo.id)

    with atomic_write(connection):
        cursor = connection.execute(
            """
            UPDATE people
            SET
                name = ?,
                bio = ?,
                profile_photo_id = ?
            WHERE id = ?
            """,
            (
                person.name,
                person.bio,
                profile_photo_id,
                str(person.id),
            ),
        )

    return cursor.rowcount == 1


def delete_person(
    connection: sqlite3.Connection,
    person_id: UUID,
) -> bool:
    with atomic_write(connection):
        cursor = connection.execute(
            """
            DELETE FROM people
            WHERE id = ?
            """,
            (str(person_id),),
        )

    return cursor.rowcount == 1
