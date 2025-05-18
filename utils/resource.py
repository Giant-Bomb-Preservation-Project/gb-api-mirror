from enum import StrEnum
import math
import re
import os
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from utils import api, file, logger


# Which image size to download
IMAGE_SIZE = "original_url"

# The URL that is at the start of all images
IMAGE_URL_PREFIX = "https://www.giantbomb.com/a/uploads/"

# Attributes in the <img> tags that contain the source images
IMAGE_SOURCE_ATTRIBUTES = [
    "srcset",
    "data-srcset",
    "data-full-srcset",
]

SRCSET_WIDTH_RE = r"\s+\d+w$"


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
                images += str(figure.get("data-img-src")).split(",")

            tags = soup.select("img")
            for tag in tags:
                srcset = ""
                for attr in IMAGE_SOURCE_ATTRIBUTES:
                    if attr in tag.attrs:
                        srcset = tag.attrs[attr]
                        break

                if srcset == "":
                    if tag.src:  # fall back to the image source
                        images.append(str(tag.src))
                    continue

                srcs = [
                    re.sub(SRCSET_WIDTH_RE, "", src)
                    for src in srcset.split(", ")
                    if src.startswith(f"{IMAGE_URL_PREFIX}original/")
                ]

                if len(srcs) == 0:
                    if tag.src:  # fall back to the image source
                        images.append(str(tag.src))
                    continue

                images += srcs

    return images


def _fill_image_object(image_url: str) -> dict:
    """Take a single image URL and create a full image object."""
    if not image_url.startswith(IMAGE_URL_PREFIX):
        return {
            "icon_url": image_url,
            "medium_url": image_url,
            "screen_url": image_url,
            "screen_large_url": image_url,
            "small_url": image_url,
            "super_url": image_url,
            "thumb_url": image_url,
            "tiny_url": image_url,
            "original_url": image_url,
            "image_tags": None,
        }

    image_uri = "/" + "/".join(image_url.replace(IMAGE_URL_PREFIX, "").split("/")[1:])

    return {
        "icon_url": IMAGE_URL_PREFIX + "square_avatar" + image_uri,
        "medium_url": IMAGE_URL_PREFIX + "scale_medium" + image_uri,
        "screen_url": IMAGE_URL_PREFIX + "screen_medium" + image_uri,
        "screen_large_url": IMAGE_URL_PREFIX + "screen_kubrick" + image_uri,
        "small_url": IMAGE_URL_PREFIX + "scale_small" + image_uri,
        "super_url": IMAGE_URL_PREFIX + "scale_large" + image_uri,
        "thumb_url": IMAGE_URL_PREFIX + "scale_avatar" + image_uri,
        "tiny_url": IMAGE_URL_PREFIX + "square_mini" + image_uri,
        "original_url": IMAGE_URL_PREFIX + "original" + image_uri,
        "image_tags": None,
    }


def _extract_articles_from_page(page: str) -> list:
    """Extract a list of articles from a page."""
    articles = []
    soup = BeautifulSoup(page, "html.parser")
    cards = soup.select(".site-container .content-item--card-item a")
    for card in cards:
        guid = str(card["href"]).rsplit("/")[-2]
        [image, meta] = card.find_all("div")
        meta_elements = meta.find_all("p")
        articles.append(
            {
                "site_detail_url": f"https://www.giantbomb.com{card['href']}",
                "deck": meta_elements[1].text,
                "guid": guid,
                "id": int(guid.split("-")[1]),
                "title": meta_elements[0].text,
                "image": _fill_image_object(image.img["src"]),
            }
        )

    return articles


def _extract_article_contents_from_page(page: str) -> dict:
    soup = BeautifulSoup(page, "html.parser").select("article.news-article")[0]
    header = soup.select(".news-hdr")[0]
    content = soup.select(".article-body .content-entity-body")[0]
    related = [
        {
            "site_detail_url": "https://www.giantbomb.com" + str(item["href"]),
            "name": item.text,
        }
        for item in soup.select(".news-related dd a")
    ]

    user = None
    if header.h3 and header.h3.a:
        user = str(header.h3.a["href"]).rsplit("/")[-2]

    return {
        "title": header.h1.text if header.h1 else None,
        "deck": header.p.text if header.p else None,
        "user": user,
        "content": str(content),
        "related": related,
        "date": header.time["datetime"] if header.time else None,
    }


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
    ARTICLES = "articles"
    CHARACTERS = "characters"
    CHATS = "chats"
    COMPANIES = "companies"
    CONCEPTS = "concepts"
    DLCS = "dlcs"
    FRANCHISES = "franchises"
    GAMES = "games"
    GAME_RATINGS = "game_ratings"
    GENRES = "genres"
    IMAGE_DATA = "image_data"
    IMAGES = "images"
    LOCATIONS = "locations"
    OBJECTS = "objects"
    PEOPLE = "people"
    PLATFORMS = "platforms"
    PROMOS = "promos"
    RATING_BOARDS = "rating_boards"
    REGIONS = "regions"
    RELEASES = "releases"
    REVIEWS = "reviews"
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

        if self == Resource.ARTICLES:
            resource_file = os.path.join(target_dir, f"{self.value}.json")
            if os.path.isfile(resource_file) and skip_existing:
                logger.info(f"Skipping existing resource: {self.value}")
                return

            logger.info(f"Downloading {self.value}...")
            data = []
            page = 1
            params = {
                "type": "articles",
            }
            while True:
                params["page"] = str(page)
                response = api.get_page("https://www.giantbomb.com/words/", params)
                articles = _extract_articles_from_page(response)

                if len(articles) == 0:
                    break

                for article in articles:
                    try:
                        response = api.get_page(article["site_detail_url"])
                        content = _extract_article_contents_from_page(response)
                        data.append(article | content)
                    except api.ApiError as error:
                        logger.error(
                            f"Unable to extract article content from {article['site_detail_url']}: {error}"
                        )
                        data.append(article)

                page += 1

            _save_data(data, resource_file)

            return

        if self == Resource.IMAGE_DATA:
            # Split resources into files, organised into folder by thousands
            resource_dir = os.path.join(target_dir, self.value)
            for gallery_id in range(1, 1000000):
                gallery_dir = os.path.join(
                    resource_dir, str(math.floor(gallery_id / 1000))
                )
                resource_file = os.path.join(gallery_dir, f"{gallery_id}.json")
                if os.path.isfile(resource_file) and skip_existing:
                    logger.info(
                        f"Skipping existing resource: {self.value}/{gallery_id}"
                    )
                    continue

                if not os.path.isdir(gallery_dir):
                    logger.debug(f"Creating directory: {gallery_dir}")
                    os.makedirs(gallery_dir)

                logger.info(f"Downloading {self.value}/{gallery_id}...")
                data = api.get_image_data(f"1310-{gallery_id}")
                _save_data(data, resource_file)

            return

        if self == Resource.IMAGES:
            logger.info(f"Extracting image resources from: {target_dir}")
            image_resources = set()
            filenames = next(os.walk(target_dir), (None, None, []))[2]
            for filename in filenames:
                source_file = os.path.join(target_dir, filename)
                _, ext = os.path.splitext(source_file)
                if ext != ".json":
                    continue

                data = file.load_json_file(source_file)
                if isinstance(data, list):
                    for item in data:
                        if "image_tags" in item:
                            for tag in item["image_tags"]:
                                url = urlparse(tag["api_detail_url"])
                                image_resources.add(url.path.rsplit("/")[-2])

            resource_dir = os.path.join(target_dir, self.value)
            if not os.path.isdir(resource_dir):
                logger.debug(f"Creating directory: {resource_dir}")
                os.makedirs(resource_dir)

            for resource_id in image_resources:
                resource_file = os.path.join(resource_dir, f"{resource_id}.json")
                resource_uri = f"images/{resource_id}"

                if os.path.isfile(resource_file) and skip_existing:
                    logger.info(f"Skipping existing resource: {resource_uri}")
                    continue

                logger.info(f"Downloading {resource_uri}...")
                data = api.get_paged_resource(resource_uri, api_key)
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
        images = []

        # Special resource handling

        if self == Resource.IMAGES:
            resource_dir = os.path.join(target_dir, self.value)
            logger.debug(f"Getting images from directory: {resource_dir}")
            files = file.list_files(resource_dir, "json")
            for file_path in files:
                for item in file.load_json_file(file_path):
                    images.append(item[IMAGE_SIZE])

            return list(set(images))

        if self == Resource.IMAGE_DATA:
            resource_dir = os.path.join(target_dir, self.value)
            logger.debug(f"Getting images from directory: {resource_dir}")
            files = file.list_files(resource_dir, "json")
            for file_path in files:
                for item in file.load_json_file(file_path):
                    images.append(item["original"])

            return list(set(images))

        # Regular resource handling

        resource_file = os.path.join(target_dir, f"{self.value}.json")
        data = file.load_json_file(resource_file)

        if self == Resource.ACCESSORIES:
            images = _extract_images_from_field(data, "image")
            images += _extract_images_from_text_field(data, "description")
        elif self == Resource.ARTICLES:
            images = _extract_images_from_field(data, "image")
            images += _extract_images_from_text_field(data, "content")
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
