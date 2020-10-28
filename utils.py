"""
Utility functions
"""
# Standard libraries
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


def get_current_year() -> int:
    return datetime.now().year


def write_to_json(json_dict: Dict[str, Any], filename: Path) -> None:
    with open(filename, "w") as json_file:
        json.dump(json_dict, json_file, indent=2)


def load_from_json(filename: Path) -> Dict[str, Any]:
    with open(filename, "r") as json_file:
        json_dict = json.load(json_file)

    return json_dict
