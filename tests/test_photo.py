import pytest

from pathlib import Path
from keepsake.domain.photo import Photo


def test_photo_with_relative_path() -> None:
    path = Path("photos/test.jpg")

    photo = Photo(path=path)

    assert photo.path == path
    assert photo.alt_text is None
    assert photo.title is None
    assert photo.id is not None


def test_photo_rejects_empty_path() -> None:
    with pytest.raises(
        ValueError,
        match="File path MUST BE file-path",
    ):
        Photo(path=Path(""))


def test_photo_rejects_absolute_path() -> None:
    absolute_path = Path.cwd() / "test.jpg"

    with pytest.raises(
        ValueError,
        match="File path cannot be absolute",
    ):
        Photo(path=absolute_path)