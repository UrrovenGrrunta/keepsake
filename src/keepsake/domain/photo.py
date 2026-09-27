import uuid
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class Photo:
    path: Path
    alt_text: str | None = None
    title: str | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __post_init__(self) -> None:
        if self.path is None:
            raise ValueError("File path cannot be empty")
        if self.path.is_absolute():
            raise ValueError("File path cannot be absolute")
        if self.path == Path("."):
            raise ValueError("File path MUST BE file-path")
