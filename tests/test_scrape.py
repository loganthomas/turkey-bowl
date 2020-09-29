"""
Unit tests for scrape.py
"""

# Standard libraries
import calendar
from datetime import datetime, timedelta

# Third-party libraries
import numpy as np
import pytest
import responses

# Local libraries
from scrape import Scraper


def test_Scraper_instantiation():
    # Setup - none necessary

    # Exercise
    scraper = Scraper(2020)

    # Verify
    assert scraper.year == 2020
    assert scraper.player_ids_json_path.as_posix() == "player_ids.json"

    assert scraper.__repr__() == "Scraper(2020)"
    assert scraper.__str__() == "Turkey Bowl Scraper (Year: 2020 NFL Week: 12)"

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
def test_Scraper_nfl_calendar_week_start(year, expected_nfl_start_DATE):
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
    scraper = Scraper(year)

    # Account for 1-indexed not 0-indexed
    week_delta = scraper.nfl_calendar_week_start - 1
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
def test_Scraper_thanksgiving_calendar_week_start(year, expected_thanksgiving_day_DATE):
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
    scraper = Scraper(year)

    # Account for 1-indexed not 0-indexed
    week_delta = scraper.thanksgiving_calendar_week_start - 1
    result = first_thur_in_year + timedelta(weeks=week_delta)

    # Verify
    assert result == expected_thanksgiving_day_DATE

    # Cleanup - none necessary


@pytest.mark.parametrize(
    "year, expected_nfl_thanksgiving_calendar_WEEK",
    [
        (2015, 12),
        (2016, 12),
        (2017, 12),
        (2018, 12),
        (2019, 13),
        (2020, 12),
    ],
)
def test_Scraper_nfl_thanksgiving_calendar_week(
    year, expected_nfl_thanksgiving_calendar_WEEK
):
    """
    Test that the NFL week of Thanksgiving is returned.
    This will be the pull week to use within the API.
    Note that weeks are 1-indexed (NFL Week 0 doesn't exist).
    """
    # Setup - none necessary

    # Exercise
    scraper = Scraper(year)

    # Verify
    assert (
        scraper.nfl_thanksgiving_calendar_week
        == expected_nfl_thanksgiving_calendar_WEEK
    )

    # Cleanup - none necessary


@pytest.mark.parametrize(
    "year, week",
    [
        (2015, 12),
        (2016, 12),
        (2017, 12),
        (2018, 12),
        (2019, 13),
        (2020, 12),
    ],
)
def test_Scraper_encode_url_params(year, week):
    # Setup
    url = "https://test.com/v2/players/test?"
    expected = f"https://test.com/v2/players/test?season={year}&week={week}"

    # Exercise
    scraper = Scraper(year)
    result = scraper._encode_url_params(url)

    # Verify
    assert result == expected

    # Cleanup - none necessary


@pytest.mark.parametrize(
    "year, week",
    [
        (2015, 12),
        (2016, 12),
        (2017, 12),
        (2018, 12),
        (2019, 13),
        (2020, 12),
    ],
)
def test_Scraper_projected_pts_url(year, week):
    # Setup
    expected = f"https://api.fantasy.nfl.com/v2/players/weekprojectedstats?season={year}&week={week}"

    # Exercise
    scraper = Scraper(year)

    # Verify
    assert scraper.projected_pts_url == expected

    # Cleanup - none necessary


@pytest.mark.parametrize(
    "year, week",
    [
        (2015, 12),
        (2016, 12),
        (2017, 12),
        (2018, 12),
        (2019, 13),
        (2020, 12),
    ],
)
def test_Scraper_actual_pts_url(year, week):
    # Setup
    expected = (
        f"https://api.fantasy.nfl.com/v2/players/weekstats?season={year}&week={week}"
    )

    # Exercise
    scraper = Scraper(year)

    # Verify
    assert scraper.actual_pts_url == expected

    # Cleanup - none necessary


@responses.activate
def test_Scraper_scrape_url_bad_status_code(capsys):
    # Setup
    url = "https://test.com"
    expected_json = {
        "errors": [
            {
                "id": "leaguePlayer",
                "message": "PLAYER_INVALID",
                "messageStringId": "PLAYER_INVALID",
            }
        ]
    }
    responses.add(method=responses.GET, url=url, json=expected_json, status=400)

    # Exercise
    scraper = Scraper(2020)
    result = scraper.scrape_url(url)
    captured = capsys.readouterr()

    # Verify
    assert result == expected_json
    assert captured.out == "WARNING: API response unsuccessful for: https://test.com\n"

    # Cleanup - none necessary


@responses.activate
def test_Scraper_scrape_url_good_status_code(capsys):
    # Setup
    url = "https://test.com"
    expected_json = {"data": "good"}
    responses.add(method=responses.GET, url=url, json=expected_json, status=200)

    # Exercise
    scraper = Scraper(2020)
    result = scraper.scrape_url(url)
    captured = capsys.readouterr()

    # Verify
    assert result == expected_json
    assert captured.out == "Successful API response obtained for: https://test.com\n"

    # Cleanup - none necessary
