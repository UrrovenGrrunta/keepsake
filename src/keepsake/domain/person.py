import uuid
from dataclasses import dataclass, field


@dataclass
class Person:
    name: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
