import csv
import os
from typing import Optional

DATA_DIR = os.path.join(os.getcwd(), "data")
STATE_FILE = "pipeline_state.csv"


def _state_file_path() -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, STATE_FILE)


def load_last_known_update_date() -> Optional[str]:
    """
    Load last_known_update_date from pipeline_state.csv
    """
    path = _state_file_path()

    if not os.path.exists(path):
        return None

    with open(path, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("key") == "last_known_update_date":
                return row.get("value")

    return None


def save_last_known_update_date(value: str) -> None:
    """
    Persist last_known_update_date to pipeline_state.csv
    """
    path = _state_file_path()

    with open(path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["key", "value"])
        writer.writeheader()
        writer.writerow(
            {
                "key": "last_known_update_date",
                "value": value,
            }
        )