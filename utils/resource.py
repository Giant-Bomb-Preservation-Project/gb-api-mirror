from enum import StrEnum
import re

from utils import api, logger


# Which image size to download
IMAGE_SIZE = "original_url"

# Regex for finding the image source attribute
IMAGE_SOURCE_RE = r"data-img-src=\"(.*?)\""


def _extract_images_from_field(items: list, field: str) -> list[str]:
    """Extract out the image field from a list of items."""
    return [item[field][IMAGE_SIZE] for item in items if field in item and item[field]]


def _extract_images_from_text_field(items: list, field: str) -> list[str]:
    """Extract images from a text field from a list of items."""
    images = []
    for item in items:
        if field in item and item[field]:
            images += re.findall(IMAGE_SOURCE_RE, item[field])

    return images


class Resource(StrEnum):
    """A resource that is downloadable from the GB API."""

    REVIEWS = "reviews"
    VIDEO_CATEGORIES = "video_categories"
    VIDEO_SHOWS = "video_shows"
    VIDEOS = "videos"

    def download_data(self, api_key: str, delay: int) -> list:
        """Download data for this resource."""
        data = []

        if self == Resource.REVIEWS:
            data = api.get_individualized_resource("review", 1000, api_key, delay)
        elif self == Resource.VIDEO_CATEGORIES:
            data = api.get_paged_resource(self.value, api_key, delay)
        elif self == Resource.VIDEO_SHOWS:
            data = api.get_paged_resource(self.value, api_key, delay)
        elif self == Resource.VIDEOS:
            data = api.get_paged_resource(self.value, api_key, delay)
        else:
            logger.error(f"Unable to download data from resource: {self}")

        return data

    def extract_images(self, data: list) -> list[str]:
        """Extract out all the images from the given resource."""
        images = []

        if self == Resource.REVIEWS:
            images = _extract_images_from_text_field(data, "description")
        elif self == Resource.VIDEO_CATEGORIES:
            images = _extract_images_from_field(data, "image")
        elif self == Resource.VIDEO_SHOWS:
            images = _extract_images_from_field(data, "image")
            images += _extract_images_from_field(data, "logo")
        elif self == Resource.VIDEOS:
            images = _extract_images_from_field(data, "image")
            # extract the images from the video shows as well in case they didn't come through the API
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
