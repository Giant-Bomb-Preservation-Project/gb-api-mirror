from enum import Enum
import sys


# Copied from https://github.com/termcolor/termcolor
COLORS: dict[str, int] = {
    "black": 30,
    "grey": 30,
    "red": 31,
    "green": 32,
    "yellow": 33,
    "blue": 34,
    "magenta": 35,
    "cyan": 36,
    "light_grey": 37,
    "dark_grey": 90,
    "light_red": 91,
    "light_green": 92,
    "light_yellow": 93,
    "light_blue": 94,
    "light_magenta": 95,
    "light_cyan": 96,
    "white": 97,
}


class Level(Enum):
    """Level of the logger."""
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


def _colorize(message: object, color: str) -> str:
    """Add color to a message."""
    if color not in COLORS:
        return str(message)

    return "\033[{}m{}\033[0m".format(COLORS[color], str(message))


def debug(message: object):
    """Log a debug message."""
    if log_level < Level.DEBUG:
        return

    print(_colorize(message, "dark_grey"))


def error(message: object):
    """Log an error message."""
    if log_level < Level.ERROR:
        return

    print(_colorize(message, "red"), file=sys.stderr)


def fatal(message: object):
    """Log an error message and then exit erroneously."""
    if log_level < Level.ERROR:
        return

    print(_colorize(message, "red"), file=sys.stderr)
    sys.exit(1)


def info(message: object):
    """Log a regular message."""
    if log_level < Level.INFO:
        return

    print(message)


def success(message: object):
    """Log a success message."""
    if log_level < Level.INFO:
        return

    print(_colorize(message, "green"))


def warn(message: object):
    """Log a warning message."""
    if log_level < Level.WARNING:
        return

    print(_colorize(message, "yellow"))
