import pytest

from keepsake.domain.event import Event
from keepsake.domain.person import Person

from datetime import datetime as dt #// Not osu! reference 


def test_event_with_default_values() -> None:
    start = dt(2006, 12, 23)

    new_event = Event(
        title="Test 1",
        starts_at=start
    )

    assert new_event.title == "Test 1"
    assert new_event.starts_at == start
    assert new_event.ends_at is None
    assert new_event.all_day is False
    assert new_event.participants == []
    assert new_event.id is not None


def test_event_rejects_blank_title() -> None:
    with pytest.raises(ValueError, match="Name cannot be empty"):
        Event(
            title="     ",
            starts_at=dt(2026, 2, 7)
        )


def test_event_rejects_end_before_start() -> None:
    with pytest.raises(
        ValueError,
        match="Event end time cannot be earlier than its start time",
    ):
        Event(
            title="Test 2",
            starts_at=dt(2026, 12, 20),
            ends_at=dt(2020, 12, 25)
        )


def test_events_have_independent_participant_lists() -> None:
    person = Person("Tim")

    event_one = Event(
        title="Test 3",
        starts_at=dt(2026, 12, 23),
    )
    event_two = Event(
        title="Test 4",
        starts_at=dt(2000, 11, 11),
    )

    event_one.participants.append(person)

    assert event_one.participants is not event_two.participants
    assert event_one.participants == [person]
    assert event_two.participants == []
