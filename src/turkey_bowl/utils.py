"""
Utility functions
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def get_current_year() -> int:
    return datetime.now().year


def load_dir_config(year: int, root: Optional[str] = None) -> SimpleNamespace:
    # 3 levels up (zero indexed)
    root = Path(__file__).parents[2] if root is None else Path(root)

    output_dir = root.joinpath(f"archive/{year}")
    draft_order_path = output_dir.joinpath(f"{year}_draft_order.json")
    draft_sheet_path = output_dir.joinpath(f"{year}_draft_sheet.xlsx")
    player_ids_json_path = root.joinpath("assets/player_ids.json")

    dir_config = SimpleNamespace(
        output_dir=output_dir.resolve(),
        draft_order_path=draft_order_path.resolve(),
        draft_sheet_path=draft_sheet_path.resolve(),
        player_ids_json_path=player_ids_json_path.resolve(),
    )

    return dir_config


def load_from_json(filename: Path) -> Dict[str, Any]:
    with open(filename, "r") as json_file:
        json_dict = json.load(json_file)

    return json_dict


def setup_logger(level: int = logging.INFO, root: Optional[str] = None) -> None:
    """Set up logger with standard formatting and handlers."""

    PREFIX = "%(asctime)s %(levelname).4s %(name)s - "
    DATE_FMT = "%Y-%m-%d %H:%M:%S"
    root = Path(__file__).parents[2] if root is None else Path(root)

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

    # Initialize the log file in the current year archive directory
    # TODO: better file/archive management instead of root here
    dir_config = load_dir_config(year=get_current_year(), root=root)
    log_filepath = dir_config.output_dir.joinpath("turkey-bowl.log")
    if not log_filepath.exists():
        if not log_filepath.parent.exists():
            log_filepath.parent.mkdir()
        open(log_filepath, mode="a").close()

    # default mode='a' but can use mode='w' to write instead of append
    log_file = logging.FileHandler(log_filepath)
    log_file.setLevel(level)
    log_file.setFormatter(formatter)
    logger.addHandler(log_file)


def write_to_json(json_dict: Dict[str, Any], filename: Path) -> None:
    with open(filename, "w") as json_file:
        json.dump(json_dict, json_file, indent=2)
        json_file.write("\n")  # ensure new line is written at end of file
