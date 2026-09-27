import uuid
from dataclasses import dataclass, field
from keepsake.domain.photo import Photo

@dataclass
class Person:
    name: str
    profile_photo: Photo | None = None
    bio: str | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
