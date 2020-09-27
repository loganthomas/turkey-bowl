"""
Scraping utilities

Notes:
    2018 used ESPN web scraping.
    ESPN changed the API in 2019 and broke everything.
    http://fantasy.espn.com/apis/v3/games/ffl/seasons/2019/segments/0/leagues/1241838?
        view=mDraftDetail&view=mLiveScoring&view=mMatchupScore&scoringPeriodId=11
    http://fantasy.espn.com/apis/v3/games/ffl/seasons/2019/segments/0/leagues/1241838?
        view=mLiveScoring&view=mMatchupScore&scoringPeriodId=11

    2019 uses NFL.com instead of ESPN. API docs found below:
    https://api.fantasy.nfl.com/v2/docs/service?serviceName=playersWeekStats
    https://api.fantasy.nfl.com/v2/docs/service?serviceName=playersWeekProjectedStats
    https://api.fantasy.nfl.com/v2/docs/service?serviceName=playerNgsContent
    https://api.fantasy.nfl.com/v2/docs/service?serviceName=gameStats
"""

# Standard libraries
import calendar
from datetime import datetime
from typing import Any, Dict
from urllib.parse import urlencode

# Third-party libraries
import numpy as np
import requests


class Scraper:
    def __init__(self, year: int) -> None:
        self.year = year
        self.base_url = "https://api.fantasy.nfl.com/v2/players"

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
        for creating a method to return the NFL start WEEK).

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
        ``nfl_calendar_week_start`` property method is
        created to return the NFL start WEEK. This method returns the
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

    def create_query_url(self, stats_type: str) -> str:
        """
        Create a url for web scrapping (or API calling) fantasy points.

        The base url will always remain the same. However, this method
        will create a query url for the desired year, week, and
        stats type in order to scrape the correct player fantasy points.
        """
        if stats_type not in ("actual", "projected"):
            raise ValueError(
                f"Invalid `stats_type`: '{stats_type}'. Must be 'actual' or 'projected'."
            )

        if stats_type == "projected":
            url = f"{self.base_url}/weekprojectedstats?"
        else:
            url = f"{self.base_url}/weekstats?"

        # Encode year and week parameters
        params = {"season": self.year, "week": self.nfl_thanksgiving_calendar_week}
        params_encoded = urlencode(params)

        query_url = f"{url}{params_encoded}"

        return query_url

    @staticmethod
    def scrape_url(query_url: str) -> Dict[str, Any]:
        """
        Send a GET request for the query url provided.
        Return the json dictionary received from the request.
        """
        response = requests.get(query_url)

        if response.status_code == requests.codes.ok:
            print(f"Successful API response obtained for: {query_url}")
        else:
            print(f"WARNING: API response unsuccessful for: {query_url}")

        return response.json()

    @staticmethod
    def collect_player_ids_pts(
        player_pts_response_json: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Collect only the players and their corresponding points for a
        provided GET request (sub-select from the json returned from
        the json dictionary returned from the request).

        Note: this assumes that ``player_pts_reponse_json`` is a result
        of sending a GET request for a the fantasy points (not for the
        player metadata).
        """
        # This is a unique identifier NOT truly a GAME identifier
        system_config = player_pts_response_json.get("systemConfig").get("currentGameId")  # type: ignore[union-attr]
        player_ids_pts = player_pts_response_json.get("games").get(system_config).get("players")  # type: ignore[union-attr]

        return player_ids_pts
