"""
Unit tests for utils.py
"""
import json
from pathlib import Path

import pytest

from turkey_bowl import utils


@pytest.mark.freeze_time
@pytest.mark.parametrize(
    "frozen_date, expected",
    [
        ("2010-09-09", 2010),
        ("2011-09-08", 2011),
        ("2012-09-05", 2012),
        ("2018-09-06", 2018),
        ("2019-09-05", 2019),
    ],
)
def test_get_current_year(freezer, frozen_date, expected):
    """Use pytest-freezegun to freeze dates and check year."""
    # Setup
    freezer.move_to(frozen_date)

    # Exercise
    result = utils.get_current_year()

    # Verify
    assert result == expected

    # Cleanup - none necessary


def test_write_to_json(tmp_path):
    # Setup
    tmp_file_path = tmp_path.joinpath("test.json")
    json_data = {"test": "test", "test2": "test2"}

    # Exercise
    assert tmp_file_path.exists() is False  # non-existent prior to write
    utils.write_to_json(json_data, tmp_file_path)

    # Verify
    assert tmp_file_path.exists() is True
    with open(tmp_file_path, "r") as written_file:
        result = json.load(written_file)

    assert result == json_data

    # Cleanup - none necessary


def test_load_from_json(tmp_path):
    # Setup
    tmp_file_path = tmp_path.joinpath("test.json")
    json_data = {"test": "test", "test2": "test2"}

    with open(tmp_file_path, "w") as written_file:
        json.dump(json_data, written_file)

    # Exercise
    assert tmp_file_path.exists() is True  # existent prior to load
    result = utils.load_from_json(tmp_file_path)

    # Verify
    assert result == json_data

    # Cleanup - none necessary


def test_write_to_and_load_from(tmp_path):
    # Setup
    tmp_file_path = tmp_path.joinpath("test.json")
    json_data = {"test": "test", "test2": "test2"}

    # Exercise
    assert tmp_file_path.exists() is False  # non-existent prior to write
    utils.write_to_json(json_data, tmp_file_path)
    result = utils.load_from_json(tmp_file_path)

    # Verify
    assert tmp_file_path.exists() is True
    assert result == json_data

    # Cleanup - none necessary


def test_load_stat_ids():
    # Setup
    file_loc = Path(__file__)
    stat_ids_json_path = file_loc.parent.parent.joinpath("assets/stat_ids.json")

    # Exercise
    result = utils.load_from_json(stat_ids_json_path)

    # Verify
    assert len(result) == 91

    for k, v in result.items():
        assert int(k) == v["id"]
        assert list(v.keys()) == ["id", "abbr", "name", "shortName"]

    # Cleanup - none necessary


def test_load_player_ids():
    # Setup
    file_loc = Path(__file__)
    stat_ids_json_path = file_loc.parent.parent.joinpath("assets/player_ids.json")

    # Exercise
    result = utils.load_from_json(stat_ids_json_path)

    # Verify
    assert "year" in result
    for k, v in result.items():
        if k == "year":
            assert isinstance(v, int)
        else:
            assert list(v.keys()) == ["name", "position", "team", "injury"]

    # Cleanup - none necessary
