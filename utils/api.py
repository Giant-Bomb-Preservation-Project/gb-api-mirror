import os
import re
from time import sleep

import requests

from utils import logger


# Base URL for the API
BASE_URL = "https://www.giantbomb.com/api"

# Headers sent with each request
HEADERS = {
    "User-Agent": "gb-api-mirror",
    "Accept": "application/json",
}

# Delay between fetching images (to avoid overloading the API)
IMAGE_DELAY = 0.5

# Mapping from one URL to another (where there is an error)
IMAGE_URL_MAPPING = {
    "https://static.giantbomb.com/": "https://www.giantbomb.com/a/",
    "https://giantbomb1.cbsistatic.com/": "https://www.giantbomb.com/a/",
    "https://www.giantbomb.com/a/uploads/scale_super/": "https://www.giantbomb.com/a/uploads/original/",
    "https://giantbomb.com/a/uploads/scale_super/": "https://www.giantbomb.com/a/uploads/original/",
}

# Valid prefixes for downloading images (any others will be skipped)
IMAGE_URL_PREFIXES = [
    "https://www.giantbomb.com/a/uploads/original/",
    "https://giantbomb.com/a/uploads/original/",
]

# How many times to retry a failed GET request
MAX_RETRIES = 10

# How long (in seconds) to wait between retrying requests
RETRY_DELAY = 30

# How long (in seconds) to wait between retrying requests if we got a rate limit error
RETRY_DELAY_RATE_LIMIT = 600

# How many items to request per page (max 100)
PAGE_REQUEST_LIMIT = 100


def _format_dict(data: dict | None, connect: str, join: str) -> str:
    """Format a dict for output."""
    if data is None:
        return ""

    return join.join([f"{k}{connect}{v}" for k, v in data.items()])


def _get(url: str, params: dict | None = None, headers: dict | None = None) -> dict:
    """Make a GET request, returning the response parsed as JSON."""
    tries = 0
    while tries < MAX_RETRIES:
        tries += 1
        logger.debug(
            f"GET {url} "
            + _format_dict(params, "=", "&")
            + " ("
            + _format_dict(headers, ":", " ")
            + ")"
        )

        if headers is None:
            headers = {}
        headers["Accept"] = "application/json"

        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return response.json()  # yay!

        if response.status_code == 420:
            logger.warn("We've gone over the limit! Waiting 10 minutes to try again...")
            sleep(RETRY_DELAY_RATE_LIMIT)
        else:
            logger.error(
                f"Unexpected response ({response.status_code}): {response.text}"
            )
            sleep(RETRY_DELAY)

    logger.fatal(f"Unable to fetch resource after {MAX_RETRIES} retries")
    return {}


def download_images(
    images: list[str], target_dir: str, overwrite_existing: bool
) -> tuple[int, int, int]:
    """Download a list of images to the target dir, returning how many were downloaded, skipped, and errored."""
    downloaded = 0
    skipped = 0
    errors = 0
    for url in images:
        for find, replace in IMAGE_URL_MAPPING.items():
            url = url.replace(find, replace)

        image_url_prefix = None
        for prefix in IMAGE_URL_PREFIXES:
            if url.startswith(prefix):
                image_url_prefix = prefix
                break

        if not image_url_prefix:
            logger.warn(f"Unhandled image URL: {url}")
            continue

        target_file = os.path.join(target_dir, url.replace(image_url_prefix, ""))

        # Remove any junk after the file extension
        _, ext = os.path.splitext(target_file)
        clean_ext = re.sub(r"^(\.[\w]+)(.*?)$", r"\1", ext)
        target_file = target_file.replace(ext, clean_ext)

        file_dir = os.path.dirname(target_file)
        if not os.path.isdir(file_dir):
            os.makedirs(file_dir, exist_ok=True)

        if not overwrite_existing and os.path.isfile(target_file):
            logger.debug(f"Skipping existing image: {target_file}")
            skipped += 1
            continue

        logger.debug(f"Downloading: {url}")
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(target_file, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            downloaded += 1
            sleep(IMAGE_DELAY)
        except Exception as err:
            logger.error(f"Error when downloading file: {str(err)}")
            errors += 1

    return downloaded, skipped, errors


def get_individualized_resource(
    resource: str, max_count: int, api_key: str, delay: int
) -> list:
    """Get a resource that needs to be fetched one entry at a time."""
    base_url = f"{BASE_URL}/{resource}"
    params = {
        "api_key": api_key,
        "format": "json",
    }

    results = []
    num = 1
    while True:
        url = f"{base_url}/{num}/"
        data = _get(url, params=params, headers=HEADERS)

        if "error" in data and data["error"] != "OK":
            logger.error(f"Received error for /{resource}/{num}: {data["error"]}")

        if "results" in data and data["results"]:
            results.append(data["results"])

        num += 1
        if num > max_count:
            break

        sleep(delay)

    return results


def get_paged_resource(resource: str, api_key: str, delay: int) -> list:
    """Get a resource that's paged with limit/offset parameters."""
    resources = []
    offset = 0
    while True:
        results = get_resource(resource, api_key, offset)
        if len(results) == 0:
            break

        resources += results
        offset += PAGE_REQUEST_LIMIT

        sleep(delay)

    return resources


def get_resource(resource: str, api_key: str, offset: int = 0) -> list:
    """Get a resource from a given offset."""
    url = f"{BASE_URL}/{resource}/"
    params = {
        "api_key": api_key,
        "format": "json",
        "limit": PAGE_REQUEST_LIMIT,
        "offset": offset,
    }

    data = _get(url, params=params, headers=HEADERS)
    if not data["results"] or len(data["results"]) == 0:
        return []

    return data["results"]
