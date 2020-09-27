# Standard libraries
import calendar
from datetime import datetime

# Third-party libraries
import numpy as np


class Scraper:
    def __init__(self, year: int) -> None:
        self.year = year

    def __repr__(self):
        return f"Scraper({self.year})"

    def __str__(self):
        return f"Turkey Bowl Scraper (Year: {self.year} NFL Week: {self.nfl_thanksgiving_calendar_week})"

    @property
    def nfl_calendar_week_start(self) -> int:
        """
        Get the calendar week in which the NFL season starts.

        The NFL season starts the first week of September, typically on
        a Thursday (not including pre-season games).

        The API requires that scores be pulled by WEEK (hence the reason
        for creating a function to return the NFL start WEEK).

        This is 1-indexed not 0-indexed. Thus, Week 1 is the true start
        of the NFL season.
        """
        # Set Sunday as first day of the week
        calendar.setfirstweekday(calendar.SUNDAY)

        # Gather September days
        sept = np.array(calendar.monthcalendar(self.year, 9))

        # Get all September Mondays
        sept_mondays = sept[:, 1]

        # Find first Monday's date
        sept_first_monday = min([mon for mon in sept_mondays if mon != 0])

        # Convert first Monday in September to datetime object
        sept_first_monday_date = datetime(self.year, 9, sept_first_monday)

        # Find calendar week for start of NFL season
        nfl_calendar_week_start = sept_first_monday_date.isocalendar()[1]

        return nfl_calendar_week_start

    @property
    def thanksgiving_calendar_week_start(self) -> int:
        """
        Get the calendar week in which Thanksgiving starts.

        The API requires that scores be pulled by WEEK. The
        ``nfl_calendar_week_start`` property function is
        created to return the NFL start WEEK. This function returns the
        Thanksgiving start WEEK.

        The correct week to pull from the API is based on subtracting
        the NFL start week from the Thanksgiving week.

        For example, if the NFL starts on week 35 and Thanksgiving is
        week 47, the week to pull via the API is week 12 (47 - 35 = 12).
        """
        # Set Sunday as first day of week
        calendar.setfirstweekday(calendar.SUNDAY)

        # Gather November days
        nov = np.array(calendar.monthcalendar(self.year, 11))

        # Find 4th Thursday in November
        nov_thursdays = nov[:, 4]
        thanksgiving_day = [thur for thur in nov_thursdays if thur != 0][3]

        # Convert Thanksgiving day to datetime object
        thanksgiving_day_date = datetime(self.year, 11, thanksgiving_day)

        # Find calendar week for Thanksgiving day
        thanksgiving_calendar_week_start = thanksgiving_day_date.isocalendar()[1]

        return thanksgiving_calendar_week_start

    @property
    def nfl_thanksgiving_calendar_week(self) -> int:
        """
        Calculate the NFL week that corresponds to Thanksgiving.

        This finds the delta between NFL Week 1 and Thanksgiving week.

        For example, if the NFL Week 1 is calendar week 35 and
        Thanksgiving is during calendar week 47, the week to pull (i.e.
        the NFL Thanksgiving calendar week) is week 12 (47 - 35 = 12).
        """
        # Find delta between NFL week 1 and Thanksgiving Week
        delta = self.thanksgiving_calendar_week_start - self.nfl_calendar_week_start

        # Add one since indexed at 1
        # (first week is considered Week 1 not Week 0)
        nfl_thanksgiving_calendar_week = delta + 1

        return nfl_thanksgiving_calendar_week
