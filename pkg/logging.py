# logging_config.py

from loguru import logger
import sys

TIME_FORMAT = "%I:%M%p"

# Define custom levels with colors
logger.level("DBG", no=10, color="<yellow>")
logger.level("INF", no=20, color="<green>")
logger.level("WRN", no=30, color="<red>")
logger.level("ERR", no=40, color="<bold red>")
logger.level("FTL", no=50, color="<bold magenta>")

# Fix: Use valid tag pairs and avoid raw ANSI in format string
LOG_FORMAT = (
    "<green>{time:" + TIME_FORMAT + "}</green> | "
    "<level>{level: <3}</level> <light-black>> </light-black>"
    "<cyan>{module}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> "
    "<light-black>> </light-black><level>{message}</level>"
)

# Remove default handlers
logger.remove()

# Add our custom handler
logger.add(
    sys.stderr,
    format=LOG_FORMAT,
    level="DBG",
    colorize=True,
    backtrace=True,
    diagnose=True,
)

Logger = logger
