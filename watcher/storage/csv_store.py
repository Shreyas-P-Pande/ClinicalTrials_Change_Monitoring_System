import os
import csv
from typing import Iterable, Dict

from watcher.storage.schemas import STUDIES_COLUMNS

DATA_DIR = os.path.join(os.getcwd(), "data")


def append_studies(file_name: str, records: Iterable[Dict]):
    os.makedirs(DATA_DIR, exist_ok=True)
    file_path = os.path.join(DATA_DIR, file_name)

    file_exists = os.path.exists(file_path)

    with open(file_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=STUDIES_COLUMNS)

        if not file_exists:
            writer.writeheader()

        written = 0
        for record in records:
            writer.writerow(record)
            written += 1

    return written