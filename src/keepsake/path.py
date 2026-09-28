from pathlib import Path

def get_project_root() -> Path:
    path = Path(__file__).resolve().parents[2]
    return path