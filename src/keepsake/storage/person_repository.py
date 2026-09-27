import sqlite3

from uuid import UUID

from ..domain.person import Person


def save_person(
    connection: sqlite3.Connection,
    person: Person,
) -> None:
    with connection:
        connection.execute(
            """
            INSERT INTO people (id, name, bio)
            VALUES (?, ?, ?)
            """,
            (
                str(person.id),
                person.name,
                person.bio,
            ),
        )


def get_person(
    connection: sqlite3.Connection,
    person_id: UUID,
) -> Person | None:
    row = connection.execute(
        """
        SELECT id, name, bio
        FROM people
        WHERE id = ?
        """,
        (str(person_id),),
    ).fetchone()

    if row is None:
        return None

    return Person(
        id=UUID(row["id"]),
        name=row["name"],
        bio=row["bio"],
    )


def list_people(
    connection: sqlite3.Connection,
) -> list[Person]:
    rows = connection.execute(
        """
        SELECT id, name, bio
        FROM people
        ORDER BY name COLLATE NOCASE, id
        """
    ).fetchall()

    return [
        Person(
            id=UUID(row["id"]),
            name=row["name"],
            bio=row["bio"],
        )
        for row in rows
    ]


def update_person(
    connection: sqlite3.Connection,
    person: Person,
) -> bool:
    with connection:
        cursor = connection.execute(
            """
            UPDATE people
            SET name = ?, bio = ?
            WHERE id = ?
            """,
            (
                person.name,
                person.bio,
                str(person.id),
            ),
        )

    return cursor.rowcount == 1


def delete_person(
    connection: sqlite3.Connection,
    person_id: UUID,
) -> bool:
    with connection:
        cursor = connection.execute(
            """
            DELETE FROM people
            WHERE id = ?
            """,
            (str(person_id),),
        )

    return cursor.rowcount == 1