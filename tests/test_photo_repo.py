from pathlib import Path

from keepsake.domain.photo import Photo
from keepsake.storage.database import (
    connect_database,
    initialize_database,
)
from keepsake.storage.photo_repository import (
    delete_photo,
    get_photo,
    list_photos,
    save_photo,
    update_photo,
)


def create_test_database(
    tmp_path: Path,
):
    connection = connect_database(
        tmp_path / "keepsake.db"
    )
    initialize_database(connection)

    return connection


def test_photo_can_be_saved_and_loaded(
    tmp_path: Path,
) -> None:
    connection = create_test_database(tmp_path)
    photo = Photo(
        path=Path("photos/image.jpg"),
        alt_text="Test image",
        title="Test photo",
    )

    try:
        save_photo(connection, photo)

        assert get_photo(connection, photo.id) == photo
    finally:
        connection.close()


def test_photos_can_be_listed(
    tmp_path: Path,
) -> None:
    connection = create_test_database(tmp_path)
    photo_b = Photo(path=Path("photos/b.jpg"))
    photo_a = Photo(path=Path("photos/a.jpg"))

    try:
        save_photo(connection, photo_b)
        save_photo(connection, photo_a)

        assert list_photos(connection) == [
            photo_a,
            photo_b,
        ]
    finally:
        connection.close()


def test_photo_can_be_updated_and_deleted(
    tmp_path: Path,
) -> None:
    connection = create_test_database(tmp_path)
    photo = Photo(path=Path("photos/old.jpg"))

    try:
        save_photo(connection, photo)

        photo.path = Path("photos/new.jpg")
        photo.alt_text = "New alt text"
        photo.title = "New title"

        assert update_photo(connection, photo) is True
        assert get_photo(connection, photo.id) == photo

        assert delete_photo(connection, photo.id) is True
        assert get_photo(connection, photo.id) is None
        assert delete_photo(connection, photo.id) is False
    finally:
        connection.close()