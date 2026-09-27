import uuid

from datetime import datetime
from dataclasses import dataclass, field

from .person import Person


@dataclass
class Event:
    title: str
    starts_at: datetime
    ends_at: datetime | None = None
    all_day: bool = False
    participants: list[Person] = field(default_factory=list)
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __post_init__(self):
        if self.title.strip() == "":
            raise ValueError("Name cannot be empty")
        
        if self.starts_at is None:
            raise ValueError("Date cannot be empty")

        if self.ends_at is not None and self.ends_at < self.starts_at:
            raise ValueError("Event end time cannot be earlier than its start time")

        