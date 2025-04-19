import requests
from time import sleep

from utils import logger


BASE_URL = "https://www.giantbomb.com/api"

HEADERS = {
    "user-agent": "gb-api-mirror",
}

GET_RETRIES = 10
RETRY_DELAY = 30
PAGE_REQUEST_LIMIT = 100  # max 100


def _format_dict(data: dict | None, connect: str, join: str) -> str:
    """Format a dict for output."""
    if data is None:
        return ""

    return join.join([f"{k}{connect}{v}" for k, v in data.items()])


def _get(url: str, params: dict | None = None, headers: dict | None = None) -> dict:
    """Make a GET request, returning the response parsed as JSON."""
    tries = 0
    while tries < GET_RETRIES:
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

        logger.error(f"Unexpected response ({response.status_code}): {response.text}")
        sleep(RETRY_DELAY)

    logger.fatal(f"Unable to fetch resource after {GET_RETRIES} retries")
    return {}


def get_paged_resource(resource: str, api_key: str, delay: int) -> list:
    """Get a resource that's paged with limit/offset parameters."""
    url = f"{BASE_URL}/{resource}/"
    params = {
        "api_key": api_key,
        "format": "json",
        "limit": PAGE_REQUEST_LIMIT,
        "offset": 0,
    }

    results = []
    offset = 0
    while True:
        params["offset"] = offset
        data = _get(url, params=params, headers=HEADERS)

        if not data["results"] or len(data["results"]) == 0:
            break  # we're done here

        results += data["results"]
        offset += PAGE_REQUEST_LIMIT

        sleep(delay)

    return results
