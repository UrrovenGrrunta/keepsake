import pytest
from keepsake.domain.journal import TextBlock


def test_textblock_with_valid_data() -> None:
    block = TextBlock("Hello world!")
    assert block.text == "Hello world!"


def test_text_block_rejects_whitespace()-> None:
    with pytest.raises(
        ValueError,
        match="Text block cannot be empty."
    ):
        TextBlock("     \n   \t")