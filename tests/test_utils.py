"""
Unit tests for utils.py
"""
# Standard libraries
from pathlib import Path

# Third-party libraries
import pytest

# Local libraries
import utils


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
    """ Use pytest-freezegun to freeze dates and check year."""
    # Setup
    freezer.move_to(frozen_date)

    # Exercise
    result = utils.get_current_year()

    # Verify
    assert result == expected

    # Cleanup - none necessary


def test_write_to_json():
    pytest.xfail()


def test_load_from_json():
    pytest.xfail()


# def test_load_stat_ids():
#     # Setup
#     file_loc = Path(__file__)
#     stat_ids_json_path = file_loc.parent.parent.joinpath("stat_ids.json")

#     # Exercise
#     result = utils.load_from_json(stat_ids_json_path)

#     # Verify
#     assert len(result) == 91

#     for k, v in result.items():
#         assert int(k) == v["id"]

#     # Cleanup - none necessary
