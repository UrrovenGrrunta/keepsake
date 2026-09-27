import pytest

from keepsake.domain.person import Person
from keepsake.domain.relationship import Relationship


def test_relationship_between_different_people() -> None:
    person_a = Person("Alina")
    person_b = Person("Alisa")
    relationship = Relationship(
        person_a=person_a,
        person_b=person_b,
        )

    assert relationship.side_a_to_b is not relationship.side_b_to_a
    assert relationship.person_a is person_a
    assert relationship.person_b is person_b

def test_relationship_between_one_person() -> None:
    person_a = Person("Alisa")
    with pytest.raises(ValueError):
        relationship = Relationship(
            person_a=person_a,
            person_b=person_a,
        )