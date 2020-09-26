"""
Unit Tests
pytest --cov-report term-missing --cov=.
"""
# Standard libraries
import calendar
import datetime

# Third-party libraries
import numpy as np
import pytest

# Local libraries
import utils

# NFL starts week of first Monday of September on Thursday
nfl_start_dates = [
    (2010, datetime.datetime(2010, 9, 9)),
    (2011, datetime.datetime(2011, 9, 8)),
    (2012, datetime.datetime(2012, 9, 5)),  # Wednesday this year
    (2013, datetime.datetime(2013, 9, 5)),
    (2014, datetime.datetime(2014, 9, 4)),
    (2015, datetime.datetime(2015, 9, 10)),
    (2016, datetime.datetime(2016, 9, 8)),
    (2017, datetime.datetime(2017, 9, 7)),
    (2018, datetime.datetime(2018, 9, 6)),
    (2019, datetime.datetime(2019, 9, 5)),
]


@pytest.mark.parametrize("year,expected", nfl_start_dates)
def test_get_nfl_start_week(year, expected):
    # Setup
    calendar.setfirstweekday(calendar.SUNDAY)
    jan = np.array(calendar.monthcalendar(year, 1))
    jan_thursdays = jan[:, 4]
    first_thur_in_jan = [thur for thur in jan_thursdays if thur != 0][0]
    first_thur_in_jan_date = datetime.datetime(year, 1, first_thur_in_jan)

    expected = expected

    # Exercise
    nfl_start_cal_week_num = utils.get_nfl_start_week(year)
    week_delta = nfl_start_cal_week_num - 1  # 1-indexed not 0-indexed
    result = first_thur_in_jan_date + datetime.timedelta(weeks=week_delta)

    # 2012 started on a wednesday
    if year == 2012:
        result -= datetime.timedelta(days=1)

    # Verify
    assert result == expected

    # Cleanup - none necessary


thanksgiving_dates = [
    (2010, datetime.datetime(2010, 11, 25)),
    (2011, datetime.datetime(2011, 11, 24)),
    (2012, datetime.datetime(2012, 11, 22)),
    (2013, datetime.datetime(2013, 11, 28)),
    (2014, datetime.datetime(2014, 11, 27)),
    (2015, datetime.datetime(2015, 11, 26)),
    (2016, datetime.datetime(2016, 11, 24)),
    (2017, datetime.datetime(2017, 11, 23)),
    (2018, datetime.datetime(2018, 11, 22)),
    (2019, datetime.datetime(2019, 11, 28)),
]


@pytest.mark.parametrize("year,expected", thanksgiving_dates)
def test_get_thanksgiving_week(year, expected):
    # Setup
    calendar.setfirstweekday(calendar.SUNDAY)
    jan = np.array(calendar.monthcalendar(year, 1))
    jan_thursdays = jan[:, 4]
    first_thur_in_jan = [thur for thur in jan_thursdays if thur != 0][0]
    first_thur_in_jan_date = datetime.datetime(year, 1, first_thur_in_jan)

    expected = expected

    # Exercise
    thanksgiving_cal_week_num = utils.get_thanksgiving_week(year)
    week_delta = thanksgiving_cal_week_num - 1  # 1-indexed not 0-indexed
    result = first_thur_in_jan_date + datetime.timedelta(weeks=week_delta)

    # Verify
    assert result == expected

    # Cleanup - none necessary
