import json
import os

from utils import logger


def list_files(source_dir: str, extension: str) -> list[str]:
    """Get a list of files in the directory that are of the given extension."""
    found = []
    for dirpath, dirnames, filenames in os.walk(source_dir):
        for file in filenames:
            _, ext = os.path.splitext(file)
            if ext == f".{extension}":
                found.append(os.path.join(dirpath, file))

    return found


def load_json_file(path: str):
    with open(path, "r", encoding="utf-8") as f:
        logger.debug(f"Loading data from: {path}")
        return json.load(f)


def save_json_file(data: dict | list, path: str):
    """Save data to a JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        logger.debug(f"Writing data to: {path}")
        json.dump(data, f, ensure_ascii=False, indent=4)
