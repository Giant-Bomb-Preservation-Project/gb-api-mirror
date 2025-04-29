from enum import StrEnum

from bs4 import BeautifulSoup

from utils import api, logger


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


class Resource(StrEnum):
    """A resource that is downloadable from the GB API."""

    ACCESSORIES = "accessories"
    CHARACTERS = "characters"
    COMPANIES = "companies"
    FRANCHISES = "franchises"
    GAMES = "games"
    GAME_RATINGS = "game_ratings"
    REVIEWS = "reviews"
    USER_REVIEWS = "user_reviews"
    VIDEO_CATEGORIES = "video_categories"
    VIDEO_SHOWS = "video_shows"
    VIDEOS = "videos"

    def download_data(self, api_key: str, delay: int) -> list:
        """Download data for this resource."""
        data = []

        if self == Resource.ACCESSORIES:
            data = api.get_paged_resource(self.value, api_key, delay)
        elif self == Resource.CHARACTERS:
            data = api.get_paged_resource(self.value, api_key, delay)
        elif self == Resource.COMPANIES:
            data = api.get_paged_resource(self.value, api_key, delay)
        elif self == Resource.FRANCHISES:
            data = api.get_paged_resource(self.value, api_key, delay)
        elif self == Resource.GAMES:
            data = api.get_paged_resource(self.value, api_key, delay)
        elif self == Resource.GAME_RATINGS:
            data = api.get_paged_resource(self.value, api_key, delay)
        elif self == Resource.REVIEWS:
            data = api.get_individualized_resource("review", 1000, api_key, delay)
        elif self == Resource.USER_REVIEWS:
            data = api.get_paged_resource(self.value, api_key, delay)
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

        if self == Resource.ACCESSORIES:
            images = _extract_images_from_field(data, "image")
            images += _extract_images_from_text_field(data, "description")
        elif self == Resource.CHARACTERS:
            images = _extract_images_from_field(data, "image")
            images += _extract_images_from_text_field(data, "description")
        elif self == Resource.COMPANIES:
            images = _extract_images_from_field(data, "image")
            images += _extract_images_from_text_field(data, "description")
        elif self == Resource.FRANCHISES:
            images = _extract_images_from_field(data, "image")
            images += _extract_images_from_text_field(data, "description")
        elif self == Resource.GAMES:
            images = _extract_images_from_field(data, "image")
            images += _extract_images_from_text_field(data, "description")
        if self == Resource.GAME_RATINGS:
            pass  # no images
        elif self == Resource.REVIEWS:
            images = _extract_images_from_text_field(data, "description")
        elif self == Resource.USER_REVIEWS:
            images = _extract_images_from_text_field(data, "description")
        elif self == Resource.VIDEO_CATEGORIES:
            images = _extract_images_from_field(data, "image")
        elif self == Resource.VIDEO_SHOWS:
            images = _extract_images_from_field(data, "image")
            images += _extract_images_from_field(data, "logo")
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
