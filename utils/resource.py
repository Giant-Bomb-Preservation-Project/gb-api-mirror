from enum import StrEnum

from utils import api, logger


# Which image size to download
IMAGE_SIZE = "original_url"


def _extract_image_field(items: list, field: str) -> list[str]:
    """Extract out the image field from a list of items."""
    return [item[field][IMAGE_SIZE] for item in items if field in item and item[field]]


class Resource(StrEnum):
    """A resource that is downloadable from the GB API."""

    VIDEO_CATEGORIES = "video_categories"
    VIDEO_SHOWS = "video_shows"
    VIDEOS = "videos"

    def download_data(self, api_key: str, delay: int) -> list:
        """Download data for this resource."""
        if self == Resource.VIDEO_CATEGORIES:
            return api.get_paged_resource(self.value, api_key, delay)
        elif self == Resource.VIDEO_SHOWS:
            return api.get_paged_resource(self.value, api_key, delay)
        elif self == Resource.VIDEOS:
            return api.get_paged_resource(self.value, api_key, delay)
        else:
            logger.error(f"Unable to download data from resource: {self}")
            return []

    def extract_images(self, data: list) -> list[str]:
        """Extract out all the images from the given resource."""
        images = []

        if self == Resource.VIDEO_CATEGORIES:
            images += _extract_image_field(data, "image")
        elif self == Resource.VIDEO_SHOWS:
            images += _extract_image_field(data, "image")
            images += _extract_image_field(data, "logo")
        elif self == Resource.VIDEOS:
            images += _extract_image_field(data, "image")
            # extract the images from the video shows as well in case they didn't come through the API
            video_shows = [
                video["video_show"]
                for video in data
                if "video_show" in video and video["video_show"]
            ]
            images += _extract_image_field(video_shows, "logo")
            images += _extract_image_field(video_shows, "image")
        else:
            logger.error(f"Unable to extract images for resource: {self}")

        return list(set(images))  # remove duplicates
