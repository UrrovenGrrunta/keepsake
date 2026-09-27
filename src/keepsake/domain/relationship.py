import uuid

from enum import Enum
from .person import Person
from dataclasses import dataclass, field


class RelationshipRole(Enum):
    UNKNOWN = "unknown"
    NONE = "none"
    ACQUAINTANCE = "acquaintance"
    FRIEND = "friend"
    CLOSE_FRIEND = "close_friend"
    ROMANTIC_INTEREST = "romantic_interest"
    FAMILY = "family"
    PARTNER = "partner"
    FORMER_PARTNER = "former_partner"
    CLASSMATE = "classmate"
    COLLEAGUE = "colleague"


class RelationshipSentiment(Enum):
    UNKNOWN = "unknown"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    MIXED = "mixed"


@dataclass
class RelationshipSide:
    role: RelationshipRole = RelationshipRole.UNKNOWN
    sentiment: RelationshipSentiment = RelationshipSentiment.UNKNOWN


@dataclass
class Relationship:
    person_a: Person
    person_b: Person
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    side_a_to_b: RelationshipSide = field(default_factory=RelationshipSide)
    side_b_to_a: RelationshipSide = field(default_factory=RelationshipSide)

    def __post_init__(self):
        if self.person_a.id == self.person_b.id:
            raise ValueError("A relationship requires two different people")