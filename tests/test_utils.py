"""
Unit tests for utils.py
"""
# Standard libraries
from datetime import datetime

# Third-party libraries
import pytest

# Local libraries
import utils


@pytest.fixture
def current_date():
    return datetime.today()


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
def test_get_current_year(current_date, freezer, frozen_date, expected):
    """ Use pytest-freezegun to freeze dates and check year."""
    # Setup
    freezer.move_to(frozen_date)

    # Exercise
    result = utils.get_current_year()

    # Verify
    assert result == expected

    # Cleanup - none necessary
