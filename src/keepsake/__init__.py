from pathlib import Path
from keepsake.storage.database import connect_database, initialize_database
from keepsake.path import get_project_root


def main() -> None:
    print(get_project_root())

