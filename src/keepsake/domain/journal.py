from dataclasses import dataclass, field
from datetime import datetime, UTC
import uuid

@dataclass
class TextBlock:
    text: str

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("Text block cannot be empty.")


@dataclass
class JournalEntry:
    title: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    blocks: list[TextBlock] = field(default_factory=list)
    id: uuid.UUID = field(default_factory=uuid.uuid4)
