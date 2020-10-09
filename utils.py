"""
Utility functions
"""
# Standard libraries
import itertools
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Third-party libraries
import pandas as pd


def get_current_year() -> int:
    return datetime.now().year


def collect_drafted_players(participant_teams: Dict[str, pd.DataFrame]) -> List[str]:
    drafted_players = [
        participant_team["Player"].tolist()
        for participant_team in participant_teams.values()
    ]
    drafted_players = [
        player for player in itertools.chain.from_iterable(drafted_players)
    ]

    return drafted_players


def check_players_have_been_drafted(drafted_players: List[str]) -> bool:
    return all(player != "" for player in drafted_players)


def write_to_json(json_dict: Dict[str, Any], filename: Path) -> None:
    with open(filename, "w") as json_file:
        json.dump(json_dict, json_file, indent=2)


def load_from_json(filename: Path) -> Dict[str, Any]:
    with open(filename, "r") as json_file:
        json_dict = json.load(json_file)

    return json_dict
