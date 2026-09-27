from keepsake.domain.journal import JournalEntry
from keepsake.domain.journal import TextBlock, Photo, PhotoBlock
from pathlib import Path
from datetime import UTC


def test_journal_entries_have_different_uuids() -> None:
    new_entry_1 = JournalEntry(
        "Entry 1",
    )
    new_entry_2 = JournalEntry(
        "Entry 2",
    )
    assert new_entry_1.id != new_entry_2.id


def test_time_is_utc() -> None:
    new_entry = JournalEntry()
    assert new_entry.created_at.tzinfo is UTC


def test_blocks_are_independent() -> None:
    text_block = TextBlock("Hello, world!")
    entry_one = JournalEntry()
    entry_two = JournalEntry()
    entry_one.blocks.append(text_block)

    assert entry_one.blocks is not entry_two.blocks
    assert entry_one.blocks == [text_block]
    assert entry_two.blocks == []


def test_journal_entry_preserves_block_order() -> None:
    text_before = TextBlock("Hello, world!")
    photo = Photo(Path("img/img.jpg"))
    photo_block = PhotoBlock(photo)
    text_after = TextBlock("Goodbye cruel world. \nXOXO Azazel")
    blocks = [text_before, photo_block, text_after]
    entry = JournalEntry(
        blocks = blocks
    )


    assert entry.blocks == blocks
    assert photo_block.photo is photo
