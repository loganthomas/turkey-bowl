"""
Utility functions
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


def get_current_year() -> int:
    return datetime.now().year


def load_from_json(filename: Path) -> Dict[str, Any]:
    with open(filename, "r") as json_file:
        json_dict = json.load(json_file)

    return json_dict


def setup_logger(level=logging.INFO):
    """Set up logger with standard formatting and handlers."""

    PREFIX = "%(asctime)s %(levelname).4s %(name)s - "
    DATE_FMT = "%Y-%m-%d %H:%M:%S"

    # Get root logger
    logger = logging.getLogger()

    logger.setLevel(level)
    console = logging.StreamHandler()
    console.setLevel(level)
    if level == logging.DEBUG:
        formatter = logging.Formatter(
            fmt=PREFIX + "%(funcName)s() [%(lineno)d] - %(message)s",
            datefmt=DATE_FMT,
        )
    else:
        formatter = logging.Formatter(
            fmt=PREFIX + "%(message)s",
            datefmt=DATE_FMT,
        )
    console.setFormatter(formatter)
    logger.addHandler(console)


def write_to_json(json_dict: Dict[str, Any], filename: Path) -> None:
    with open(filename, "w") as json_file:
        json.dump(json_dict, json_file, indent=2)
