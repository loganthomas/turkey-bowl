"""
Unit Tests
pytest --cov-report term-missing --cov=.
"""
# Standard libraries
import calendar
from datetime import datetime, timedelta

# Third-party libraries
import numpy as np
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


def _get_date_of_first_thur_in_year(year: int) -> datetime:
    """ Helper function for finding the first Thursday in the year."""
    calendar.setfirstweekday(calendar.SUNDAY)
    jan = np.array(calendar.monthcalendar(year, 1))
    jan_thursdays = jan[:, 4]
    first_thur_in_jan = [thur for thur in jan_thursdays if thur != 0][0]
    first_thur_in_jan_date = datetime(year, 1, first_thur_in_jan)

    return first_thur_in_jan_date


@pytest.mark.parametrize(
    "year, expected_nfl_start_DATE",
    [
        (2010, datetime(2010, 9, 9)),
        (2011, datetime(2011, 9, 8)),
        (2012, datetime(2012, 9, 5)),  # Wednesday this year
        (2013, datetime(2013, 9, 5)),
        (2014, datetime(2014, 9, 4)),
        (2015, datetime(2015, 9, 10)),
        (2016, datetime(2016, 9, 8)),
        (2017, datetime(2017, 9, 7)),
        (2018, datetime(2018, 9, 6)),
        (2019, datetime(2019, 9, 5)),
        (2020, datetime(2020, 9, 10)),
    ],
)
def test_get_nfl_start_week(year, expected_nfl_start_DATE):
    """
    Test that correct NFL start DATE is returned.

    The NFL starts the first week of September, typically on a Thursday
    (not including pre-season games).

    The API requires that scores be pulled by WEEK (hence the reason for
    creating a function to return the NFL start WEEK).

    This test function converts the week returned to the actual start
    NFL start DATE. Thus, the provided expected values are NFL start
    dates (not weeks).

    It's easier to look up the NFL start date than to convert the date
    to the week of the year.
    """
    # Setup
    first_thur_in_year = _get_date_of_first_thur_in_year(year)

    # Exercise
    nfl_start_cal_week_num = utils.get_nfl_start_week(year)
    week_delta = nfl_start_cal_week_num - 1  # 1-indexed not 0-indexed
    result_nfl_start_date = first_thur_in_year + timedelta(weeks=week_delta)

    # 2012 started on a Wednesday
    if year == 2012:
        result_nfl_start_date -= timedelta(days=1)

    # Verify
    assert result_nfl_start_date == expected_nfl_start_DATE

    # Cleanup - none necessary


@pytest.mark.parametrize(
    "year, expected_thanksgiving_day_DATE",
    [
        (2010, datetime(2010, 11, 25)),
        (2011, datetime(2011, 11, 24)),
        (2012, datetime(2012, 11, 22)),
        (2013, datetime(2013, 11, 28)),
        (2014, datetime(2014, 11, 27)),
        (2015, datetime(2015, 11, 26)),
        (2016, datetime(2016, 11, 24)),
        (2017, datetime(2017, 11, 23)),
        (2018, datetime(2018, 11, 22)),
        (2019, datetime(2019, 11, 28)),
        (2020, datetime(2020, 11, 26)),
    ],
)
def test_get_thanksgiving_week(year, expected_thanksgiving_day_DATE):
    """
    Test that correct Thanksgiving day DATE is returned.

    The API requires that scores be pulled by WEEK. A function is
    created to return the NFL start WEEK and the Thanksgiving WEEK.
    The correct week to pull is based on subtracting the NFL start week
    from the Thanksgiving week. For example, if the NFL starts on week
    35 and Thanksgiving is week 47, the week to pull via the API is week
    12 (47 - 35 = 12).

    This test function converts the week returned to the actual
    Thanksgiving day DATE. Thus, the provided expected values are
    dates for Thanksgiving day (not weeks).

    It's easier to look up Thanksgiving day dates than to convert the
    date to the week of the year.
    """
    # Setup
    first_thur_in_year = _get_date_of_first_thur_in_year(year)

    # Exercise
    thanksgiving_cal_week_num = utils.get_thanksgiving_week(year)
    week_delta = thanksgiving_cal_week_num - 1  # 1-indexed not 0-indexed
    result = first_thur_in_year + timedelta(weeks=week_delta)

    # Verify
    assert result == expected_thanksgiving_day_DATE

    # Cleanup - none necessary


@pytest.mark.parametrize(
    "nfl_start_cal_week_num, thanksgiving_cal_week_num, expected_pull_week",
    [
        (38, 38, 1),  # zero-index test return week 1 for 0
        (38, 39, 2),  # zero-index test return week 2 for 1
        (36, 47, 12),  # 2018
        (36, 48, 13),  # 2019
        (37, 48, 12),  # 2020
    ],
    ids=[
        "zero-index-test-week1",
        "zero-index-test-week2",
        "2018-week",
        "2019-week",
        "2020-week",
    ],
)
def test_calculate_nfl_thanksgiving_week(
    nfl_start_cal_week_num, thanksgiving_cal_week_num, expected_pull_week
):
    """
    Test that the NFL week of Thanksgiving is returned.
    This will be the pull week to use within the API.
    Note that weeks are 1-indexed (NFL Week 0 doesn't exist).
    """
    # Setup - none necessary

    # Exercise
    result = utils.calculate_nfl_thanksgiving_week(
        nfl_start_cal_week_num, thanksgiving_cal_week_num
    )

    # Verify
    assert result == expected_pull_week

    # Cleanup - none necessary


def test_create_output_dir_path_exists(tmp_path):
    # Setup
    root_tmp_dir = tmp_path.joinpath("archive")
    root_tmp_dir.mkdir()
    tmp_2020 = root_tmp_dir.joinpath("2020")
    tmp_2020.mkdir()

    # ensure path to year 2020 already exists
    assert list(root_tmp_dir.iterdir())[0].name == "2020"

    # Exercise
    result = utils.create_output_dir(path=f"{str(root_tmp_dir)}/2020")

    # Verify
    assert str(result) == str(tmp_2020)

    # Cleanup - none necessary


def test_create_output_dir_path_doesnt_exist(tmp_path):
    # Setup
    root_tmp_dir = tmp_path.joinpath("archive")
    root_tmp_dir.mkdir()

    # ensure path already exists
    assert list(tmp_path.iterdir())[0].name == "archive"
    assert root_tmp_dir.joinpath("2020").exists() is False

    # Exercise
    result = utils.create_output_dir(path=f"{str(root_tmp_dir)}/2020")

    # Verify
    assert str(result) == str(root_tmp_dir.joinpath("2020"))
    assert root_tmp_dir.joinpath("2020").exists() is True

    # Cleanup - none necessary
