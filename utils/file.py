import json

from utils import logger


def load_json_file(path: str):
    with open(path, "r", encoding="utf-8") as f:
        logger.debug(f"Loading data from: {path}")
        return json.load(f)


def save_json_file(data: dict | list, path: str):
    """Save data to a JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        logger.debug(f"Writing data to: {path}")
        json.dump(data, f, ensure_ascii=False, indent=4)
