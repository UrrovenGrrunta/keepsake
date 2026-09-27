import sqlite3
from uuid import UUID

from ..domain.relationship import (
    Relationship,
    RelationshipRole,
    RelationshipSentiment,
    RelationshipSide,
)
from .person_repository import get_person


def _relationship_from_row(
    connection: sqlite3.Connection,
    row: sqlite3.Row,
) -> Relationship:
    person_a = get_person(connection, UUID(row["person_a_id"]))
    person_b = get_person(connection, UUID(row["person_b_id"]))
    if person_a is None or person_b is None:
        raise ValueError("Relationship refers to a missing person")

    return Relationship(
        id=UUID(row["id"]),
        person_a=person_a,
        person_b=person_b,
        side_a_to_b=RelationshipSide(
            role=RelationshipRole(row["a_to_b_role"]),
            sentiment=RelationshipSentiment(row["a_to_b_sentiment"]),
        ),
        side_b_to_a=RelationshipSide(
            role=RelationshipRole(row["b_to_a_role"]),
            sentiment=RelationshipSentiment(row["b_to_a_sentiment"]),
        ),
    )


def save_relationship(
    connection: sqlite3.Connection,
    relationship: Relationship,
) -> None:
    with connection:
        connection.execute(
            """
            INSERT INTO relationships (
                id, person_a_id, person_b_id,
                a_to_b_role, a_to_b_sentiment,
                b_to_a_role, b_to_a_sentiment
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(relationship.id),
                str(relationship.person_a.id),
                str(relationship.person_b.id),
                relationship.side_a_to_b.role.value,
                relationship.side_a_to_b.sentiment.value,
                relationship.side_b_to_a.role.value,
                relationship.side_b_to_a.sentiment.value,
            ),
        )


def get_relationship(
    connection: sqlite3.Connection,
    relationship_id: UUID,
) -> Relationship | None:
    row = connection.execute(
        "SELECT * FROM relationships WHERE id = ?",
        (str(relationship_id),),
    ).fetchone()
    if row is None:
        return None
    return _relationship_from_row(connection, row)


def list_relationships(
    connection: sqlite3.Connection,
    person_id: UUID | None = None,
) -> list[Relationship]:
    if person_id is None:
        rows = connection.execute(
            "SELECT * FROM relationships ORDER BY id"
        ).fetchall()
    else:
        rows = connection.execute(
            """
            SELECT * FROM relationships
            WHERE person_a_id = ? OR person_b_id = ?
            ORDER BY id
            """,
            (str(person_id), str(person_id)),
        ).fetchall()
    return [_relationship_from_row(connection, row) for row in rows]


def update_relationship(
    connection: sqlite3.Connection,
    relationship: Relationship,
) -> bool:
    with connection:
        cursor = connection.execute(
            """
            UPDATE relationships SET
                person_a_id = ?, person_b_id = ?,
                a_to_b_role = ?, a_to_b_sentiment = ?,
                b_to_a_role = ?, b_to_a_sentiment = ?
            WHERE id = ?
            """,
            (
                str(relationship.person_a.id),
                str(relationship.person_b.id),
                relationship.side_a_to_b.role.value,
                relationship.side_a_to_b.sentiment.value,
                relationship.side_b_to_a.role.value,
                relationship.side_b_to_a.sentiment.value,
                str(relationship.id),
            ),
        )
    return cursor.rowcount == 1


def delete_relationship(
    connection: sqlite3.Connection,
    relationship_id: UUID,
) -> bool:
    with connection:
        cursor = connection.execute(
            "DELETE FROM relationships WHERE id = ?",
            (str(relationship_id),),
        )
    return cursor.rowcount == 1
