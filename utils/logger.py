from enum import Enum
import sys

from termcolor import cprint


class Level(Enum):
    NONE = 0
    ERROR = 1
    WARNING = 2
    INFO = 3
    DEBUG = 4

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


log_level: Level = Level.INFO


def debug(message: str, end: str = "\n"):
    """Log a debug message."""
    if log_level < Level.DEBUG:
        return

    cprint(message, "dark_grey", end=end)


def error(message: str, end: str = "\n"):
    """Log an error message."""
    if log_level < Level.ERROR:
        return

    cprint(message, "red", end=end, file=sys.stderr)


def fatal(message: str, end: str = "\n"):
    """Log an error message and then exit erroneously."""
    if log_level < Level.ERROR:
        return

    cprint(message, "red", end=end, file=sys.stderr)
    exit(1)


def info(message: str, end: str = "\n"):
    """Log a regular message."""
    if log_level < Level.INFO:
        return

    print(message, end=end)


def success(message: str, end: str = "\n"):
    """Log a success message."""
    if log_level < Level.INFO:
        return

    cprint(message, "green", end=end)


def warn(message: str, end: str = "\n"):
    """Log a warning message."""
    if log_level < Level.WARNING:
        return

    cprint(message, "yellow", end=end)
