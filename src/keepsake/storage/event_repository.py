import sqlite3
from datetime import datetime
from uuid import UUID

from ..domain.event import Event
from .person_repository import get_person


def _event_from_row(
    connection: sqlite3.Connection,
    row: sqlite3.Row,
) -> Event:
    participant_rows = connection.execute(
        """
        SELECT person_id FROM event_participants
        WHERE event_id = ? ORDER BY position
        """,
        (row["id"],),
    ).fetchall()
    participants = []
    for participant_row in participant_rows:
        person = get_person(connection, UUID(participant_row["person_id"]))
        if person is None:
            raise ValueError("Event refers to a missing person")
        participants.append(person)

    return Event(
        id=UUID(row["id"]),
        title=row["title"],
        starts_at=datetime.fromisoformat(row["starts_at"]),
        ends_at=(
            datetime.fromisoformat(row["ends_at"])
            if row["ends_at"] is not None else None
        ),
        all_day=bool(row["all_day"]),
        participants=participants,
    )


def _save_participants(
    connection: sqlite3.Connection,
    event: Event,
) -> None:
    connection.executemany(
        """
        INSERT INTO event_participants (event_id, position, person_id)
        VALUES (?, ?, ?)
        """,
        (
            (str(event.id), position, str(person.id))
            for position, person in enumerate(event.participants)
        ),
    )


def save_event(
    connection: sqlite3.Connection,
    event: Event,
) -> None:
    with connection:
        connection.execute(
            """
            INSERT INTO events (id, title, starts_at, ends_at, all_day)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                str(event.id), event.title, event.starts_at.isoformat(),
                event.ends_at.isoformat() if event.ends_at is not None else None,
                int(event.all_day),
            ),
        )
        _save_participants(connection, event)


def get_event(
    connection: sqlite3.Connection,
    event_id: UUID,
) -> Event | None:
    row = connection.execute(
        "SELECT * FROM events WHERE id = ?",
        (str(event_id),),
    ).fetchone()
    if row is None:
        return None
    return _event_from_row(connection, row)


def list_events(
    connection: sqlite3.Connection,
    person_id: UUID | None = None,
) -> list[Event]:
    if person_id is None:
        rows = connection.execute(
            "SELECT * FROM events ORDER BY starts_at, id"
        ).fetchall()
    else:
        rows = connection.execute(
            """
            SELECT events.* FROM events
            WHERE EXISTS (
                SELECT 1 FROM event_participants
                WHERE event_id = events.id AND person_id = ?
            )
            ORDER BY starts_at, id
            """,
            (str(person_id),),
        ).fetchall()
    return [_event_from_row(connection, row) for row in rows]


def update_event(
    connection: sqlite3.Connection,
    event: Event,
) -> bool:
    with connection:
        cursor = connection.execute(
            """
            UPDATE events SET title = ?, starts_at = ?, ends_at = ?, all_day = ?
            WHERE id = ?
            """,
            (
                event.title, event.starts_at.isoformat(),
                event.ends_at.isoformat() if event.ends_at is not None else None,
                int(event.all_day), str(event.id),
            ),
        )
        if cursor.rowcount == 0:
            return False
        connection.execute(
            "DELETE FROM event_participants WHERE event_id = ?",
            (str(event.id),),
        )
        _save_participants(connection, event)
    return True


def delete_event(
    connection: sqlite3.Connection,
    event_id: UUID,
) -> bool:
    with connection:
        cursor = connection.execute(
            "DELETE FROM events WHERE id = ?",
            (str(event_id),),
        )
    return cursor.rowcount == 1
