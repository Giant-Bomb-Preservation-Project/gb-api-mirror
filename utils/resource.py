from enum import StrEnum
import math
import os

from bs4 import BeautifulSoup

from utils import api, file, logger


# Which image size to download
IMAGE_SIZE = "original_url"


def _extract_images_from_field(items: list[dict], field: str) -> list[str]:
    """Extract out the image field from a list of items."""
    return [item[field][IMAGE_SIZE] for item in items if field in item and item[field]]


def _extract_images_from_text_field(items: list[dict], field: str) -> list[str]:
    """Extract images from a text field from a list of items."""
    images = []
    for item in items:
        if field in item and item[field]:
            soup = BeautifulSoup(item[field], "html.parser")
            figures = soup.select("figure[data-img-src]")

            for figure in figures:
                images.append(str(figure.get("data-img-src")))

    return images


def _save_data(data: list, target_file: str):
    """Save the data to a given file, logging how much."""
    file.save_json_file(data, target_file)
    if len(data) == 0:
        logger.warn(" -> saved 0 items")
    else:
        logger.success(f" -> saved {len(data)} items")


class Resource(StrEnum):
    """A resource that is downloadable from the GB API."""

    ACCESSORIES = "accessories"
    CHARACTERS = "characters"
    CHATS = "chats"
    COMPANIES = "companies"
    CONCEPTS = "concepts"
    DLCS = "dlcs"
    FRANCHISES = "franchises"
    GAMES = "games"
    GAME_RATINGS = "game_ratings"
    GENRES = "genres"
    LOCATIONS = "locations"
    OBJECTS = "objects"
    PEOPLE = "people"
    PLATFORMS = "platforms"
    PROMOS = "promos"
    RATING_BOARDS = "rating_boards"
    REGIONS = "regions"
    RELEASES = "releases"
    REVIEWS = "reviews"
    PROFILE_IMAGES = "profile_images"
    THEMES = "themes"
    TYPES = "types"
    USER_REVIEWS = "user_reviews"
    VIDEO_CATEGORIES = "video_categories"
    VIDEO_SHOWS = "video_shows"
    VIDEO_TYPES = "video_types"
    VIDEOS = "videos"

    def download_data(self, target_dir: str, api_key: str, skip_existing: bool):
        """Download data for this resource, saving it in the given directory."""
        if not os.path.isdir(target_dir):
            logger.debug(f"Creating directory: {target_dir}")
            os.makedirs(target_dir)

        # Special resource handling

        if self == Resource.PROFILE_IMAGES:
            # Split resources into files, organised into folder by thousands
            resource_dir = os.path.join(target_dir, self.value)
            for profile_id in range(1, 1000000):
                profile_dir = os.path.join(
                    resource_dir, str(math.floor(profile_id / 1000))
                )
                resource_file = os.path.join(profile_dir, f"{profile_id}.json")
                if os.path.isfile(resource_file) and skip_existing:
                    logger.info(
                        f"Skipping existing resource: {self.value}/{profile_id}"
                    )
                    continue

                if not os.path.isdir(profile_dir):
                    logger.debug(f"Creating directory: {profile_dir}")
                    os.makedirs(profile_dir)

                logger.info(f"Downloading {self.value}/{profile_id}...")
                data = api.get_image_data(f"1310-{profile_id}")
                _save_data(data, resource_file)

            return

        # Regular resource handling

        resource_file = os.path.join(target_dir, f"{self.value}.json")
        data = []

        if os.path.isfile(resource_file) and skip_existing:
            logger.info(f"Skipping existing resource: {self.value}")
            return

        logger.info(f"Downloading {self.value}...")
        if self in [
            Resource.ACCESSORIES,
            Resource.CHARACTERS,
            Resource.CHATS,
            Resource.COMPANIES,
            Resource.CONCEPTS,
            Resource.DLCS,
            Resource.FRANCHISES,
            Resource.GAMES,
            Resource.GAME_RATINGS,
            Resource.GENRES,
            Resource.LOCATIONS,
            Resource.OBJECTS,
            Resource.PEOPLE,
            Resource.PLATFORMS,
            Resource.PROMOS,
            Resource.RATING_BOARDS,
            Resource.REGIONS,
            Resource.RELEASES,
            Resource.USER_REVIEWS,
            Resource.THEMES,
            Resource.VIDEO_CATEGORIES,
            Resource.VIDEO_SHOWS,
            Resource.VIDEO_TYPES,
            Resource.VIDEOS,
        ]:
            data = api.get_paged_resource(self.value, api_key)
        elif self == Resource.REVIEWS:
            data = api.get_individualized_resource("review", 1000, api_key)
        elif self == Resource.TYPES:
            data = api.get_resource(self.value, api_key)
        else:
            logger.error(f"Unable to download data from resource: {self}")

        _save_data(data, resource_file)

    def extract_images(self, target_dir: str) -> list[str]:
        """Extract out all the images from the given resource by loading its file."""
        resource_file = os.path.join(target_dir, f"{self.value}.json")
        images = []

        data = file.load_json_file(resource_file)

        if self == Resource.PROFILE_IMAGES:
            logger.fatal("TODO")

        if self == Resource.ACCESSORIES:
            images = _extract_images_from_field(data, "image")
            images += _extract_images_from_text_field(data, "description")
        elif self == Resource.CHARACTERS:
            images = _extract_images_from_field(data, "image")
            images += _extract_images_from_text_field(data, "description")
        elif self == Resource.COMPANIES:
            images = _extract_images_from_field(data, "image")
            images += _extract_images_from_text_field(data, "description")
        elif self == Resource.CONCEPTS:
            images = _extract_images_from_field(data, "image")
            images += _extract_images_from_text_field(data, "description")
        elif self == Resource.DLCS:
            images = _extract_images_from_field(data, "image")
        elif self == Resource.FRANCHISES:
            images = _extract_images_from_field(data, "image")
            images += _extract_images_from_text_field(data, "description")
        elif self == Resource.GAMES:
            images = _extract_images_from_field(data, "image")
            images += _extract_images_from_text_field(data, "description")
        elif self == Resource.GAME_RATINGS:
            pass  # no images
        elif self == Resource.GENRES:
            images = _extract_images_from_field(data, "image")
        elif self == Resource.LOCATIONS:
            images = _extract_images_from_field(data, "image")
            images += _extract_images_from_text_field(data, "description")
        elif self == Resource.OBJECTS:
            images = _extract_images_from_field(data, "image")
            images += _extract_images_from_text_field(data, "description")
        elif self == Resource.PEOPLE:
            images = _extract_images_from_field(data, "image")
            images += _extract_images_from_text_field(data, "description")
        elif self == Resource.PLATFORMS:
            images = _extract_images_from_field(data, "image")
            images += _extract_images_from_text_field(data, "description")
        elif self == Resource.RATING_BOARDS:
            images = _extract_images_from_field(data, "image")
        elif self == Resource.REGIONS:
            images = _extract_images_from_field(data, "image")
        elif self == Resource.RELEASES:
            images = _extract_images_from_field(data, "image")
        elif self == Resource.REVIEWS:
            images = _extract_images_from_text_field(data, "description")
        elif self == Resource.THEMES:
            pass  # no images
        elif self == Resource.TYPES:
            pass  # no images
        elif self == Resource.USER_REVIEWS:
            images = _extract_images_from_text_field(data, "description")
        elif self == Resource.VIDEO_CATEGORIES:
            images = _extract_images_from_field(data, "image")
        elif self == Resource.VIDEO_SHOWS:
            images = _extract_images_from_field(data, "image")
            images += _extract_images_from_field(data, "logo")
        elif self == Resource.VIDEO_TYPES:
            pass  # no images
        elif self == Resource.VIDEOS:
            images = _extract_images_from_field(data, "image")
            # extract the images from the video shows as well if they didn't come through the API
            video_shows = [
                video["video_show"]
                for video in data
                if "video_show" in video and video["video_show"]
            ]
            images += _extract_images_from_field(video_shows, "logo")
            images += _extract_images_from_field(video_shows, "image")
        else:
            logger.error(f"Unable to extract images for resource: {self}")

        return list(set(images))  # remove duplicates
