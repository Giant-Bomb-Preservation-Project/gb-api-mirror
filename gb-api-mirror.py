from argparse import ArgumentParser
from enum import StrEnum
import os

from utils import logger


class Resource(StrEnum):
    VIDEO_SHOWS = "video_shows"


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
        "--images",
        help="download images alongside metadata",
        action="store_true",
    )
    parser.add_argument(
        "-i",
        "--include",
        help="which resources to include",
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

        print(target_file)
