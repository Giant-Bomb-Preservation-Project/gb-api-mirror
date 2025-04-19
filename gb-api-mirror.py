from argparse import ArgumentParser
from enum import StrEnum

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

    # Validate arguments
    args = parser.parse_args()
    resources: list[Resource] = []
    if args.include:
        for res in args.include.lower().split(","):
            if res not in Resource:
                logger.fatal(f"Unsupported resource: {res}")
            resources.append(Resource[res.upper()])
    else:
        resources = [r for r in Resource]

    logger.info(f"TODO: download to {args.target}")
    logger.info(f"include={resources}")
