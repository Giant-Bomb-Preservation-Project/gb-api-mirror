from argparse import ArgumentParser
from enum import StrEnum
import json
import os

from utils import api, logger, file

# Subdir to store the images
IMAGE_DIR = "images"


class Resource(StrEnum):
    VIDEO_CATEGORIES = "video_categories"
    VIDEO_SHOWS = "video_shows"


def _download_data(resource: Resource, api_key: str, delay: int) -> list:
    """Download data for the given resource, returning the results."""
    regular_resources = [
        # resources that just use the regular offset paged API
        Resource.VIDEO_CATEGORIES,
        Resource.VIDEO_SHOWS,
    ]

    if resource in regular_resources:
        return api.get_paged_resource(resource.value, api_key, delay)
    else:
        logger.error(f"Unhandled resource: {resource}")
        return []


def _download_images(images: list[str], target_dir: str, skip_existing: bool) -> int:
    """Download a list of images to the target dir, returning how many were downloaded."""
    logger.warn("TODO")
    return 0


def _extract_images(resource: Resource, data: list) -> list[str]:
    """Extract out all the images from the given resource."""
    logger.warn("TODO")
    return []


if __name__ == "__main__":
    parser = ArgumentParser(description="Downloads data from the Giant Bomb API")
    parser.add_argument(
        "target",
        metavar="TARGET_DIR",
        type=str,
        help="directory to store the data in",
    )
    parser.add_argument(
        "-d",
        "--delay",
        type=int,
        default=18,  # 200 requests per hour
        metavar="SECONDS",
        help="time to delay between requests (default: 18)",
    )
    parser.add_argument(
        "-f",
        "--images",
        help="download images alongside metadata",
        action="store_true",
    )
    parser.add_argument(
        "-i",
        "--include",
        metavar="RESOURCES",
        help="which resources to include (defaults to all)",
    )
    parser.add_argument("-q", "--quiet", help="prevent all output", action="store_true")
    parser.add_argument(
        "-s",
        "--skip-existing",
        help="skip files that already exist",
        action="store_true",
    )
    parser.add_argument(
        "-v", "--verbose", help="show verbose output", action="store_true"
    )

    # Get API key

    if "GB_API_KEY" not in os.environ:
        logger.fatal("Missing environment variable: GB_API_KEY")
    api_key = os.environ["GB_API_KEY"]

    # Parse arguments

    args = parser.parse_args()

    resources: list[Resource] = []
    if args.include:
        for res in args.include.lower().split(","):
            if res not in Resource:
                logger.fatal(f"Unsupported resource: {res}")
            resources.append(Resource[res.upper()])
    else:
        resources = [r for r in Resource]

    if args.quiet and args.verbose:
        logger.fatal("Unable to be both quiet and verbose at the same time :(")
    if args.quiet:
        logger.log_level = logger.Level.ERROR
    if args.verbose:
        logger.log_level = logger.Level.DEBUG

    target_dir = os.path.abspath(args.target)

    # Do the thing

    if not os.path.isdir(target_dir):
        logger.debug(f"Creating directory: {target_dir}")
        os.makedirs(target_dir)

    for resource in resources:
        target_file = os.path.join(target_dir, resource.value + ".json")
        if os.path.isfile(target_file) and args.skip_existing:
            logger.info(f"Skipping existing resource: {resource}")
            continue

        logger.info(f"Downloading {resource.value}...")
        data = _download_data(resource, api_key, args.delay)
        if len(data) == 0:
            logger.warn(f"Got 0 results for: {resource.value}")
            continue

        file.save_json_file(data, target_file)

        logger.info(f"Saved {len(data)} items")

        if args.images:
            images = _extract_images(resource, data)
            if len(images) == 0:
                logger.warn(f"Got 0 images for: {resource.value}")
                continue

            logger.info(f"Downloading {len(images)} images...")
            count = _download_images(
                images, os.path.join(target_dir, IMAGE_DIR), args.skip_existing
            )
            logger.info(f"Saved {count} images ({len(images) - count} skipped)")
