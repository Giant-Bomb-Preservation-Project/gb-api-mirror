from argparse import ArgumentParser
import math
import os

from utils import api, logger, file
from utils.resource import Resource

# Subdir to store the images
IMAGE_DIR = "uploads"


def _download_resource(
    resource: Resource,
    target_file: str,
    skip_existing: bool,
    api_key: str,
    param: str | None = None,
) -> list:
    """Helper function for downloading a resource to a given file, returning the downloaded data."""
    resource_name = resource.value
    if param:
        resource_name += f"/{param}"

    if os.path.isfile(target_file) and skip_existing:
        logger.info(f"Skipping existing resource: {resource_name}")
        return

    logger.info(f"Downloading {resource_name}...")
    data = resource.download_data(api_key, param)

    file.save_json_file(data, target_file)
    if len(data) == 0:
        logger.warn("Saved 0 item")
    else:
        logger.success(f"Saved {len(data)} items")

    return data


if __name__ == "__main__":
    parser = ArgumentParser(description="Downloads data from the Giant Bomb API")
    parser.add_argument(
        "target",
        metavar="TARGET_DIR",
        type=str,
        help="directory to store the data in",
    )
    parser.add_argument(
        "-f",
        "--download-images",
        help="download image files alongside metadata",
        action="store_true",
    )
    parser.add_argument(
        "-i",
        "--include",
        metavar="RESOURCES",
        help="which resources to include (defaults to all)",
    )
    parser.add_argument(
        "-o",
        "--overwrite-images",
        help="overwrite existing images",
        action="store_true",
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
        data = []

        if resource == Resource.PROFILE_IMAGES:
            resource_dir = os.path.join(target_dir, resource.value)

            # Download one per profile ID
            for profile_id in range(1, 999999):
                profile_dir = os.path.join(
                    resource_dir, str(math.floor(profile_id / 1000))
                )
                if not os.path.isdir(profile_dir):
                    logger.debug(f"Creating directory: {profile_dir}")
                    os.makedirs(profile_dir)
                target_file = os.path.join(profile_dir, f"{profile_id}.json")
                _download_resource(
                    resource,
                    target_file=target_file,
                    skip_existing=args.skip_existing,
                    api_key=api_key,
                    param=str(profile_id),
                )

            if args.download_images:
                logger.fatal("Downloading profile images currently not supported")
        else:
            target_file = os.path.join(target_dir, f"{resource.value}.json")
            data = _download_resource(
                resource,
                target_file=target_file,
                skip_existing=args.skip_existing,
                api_key=api_key,
                param=None,
            )

            if args.download_images:
                images = resource.extract_images(data)
                if len(images) == 0:
                    logger.warn(f"Got 0 images for {resource}")
                    continue

                logger.info(f"Downloading {len(images)} images...")
                downloaded, skipped, errors = api.download_images(
                    images, os.path.join(target_dir, IMAGE_DIR), args.overwrite_images
                )
                logger.success(
                    f"Saved {downloaded} images ({skipped} skipped, {errors} errors)"
                )
