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

import calendar
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import numpy as np
import requests
from tqdm import tqdm

from turkey_bowl import utils

logger = logging.getLogger(__name__)


class Scraper:
    def __init__(self, year: int, root: Optional[str] = None) -> None:
        self.dir_config = utils.load_dir_config(year, root)
        self.year = year
        self.week_delta = self.thanksgiving_calendar_week_start - self.nfl_calendar_week_start

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

        Add one since indexed at 1 (first week is considered Week 1 not Week 0)
        """
        return self.week_delta + 1

    @nfl_thanksgiving_calendar_week.setter
    def nfl_thanksgiving_calendar_week(self, week) -> None:
        """
        Sets the "pull" week for scraping NFL scores.
        Original Thanksgiving calendar week and NFL calendar week
        are preserved.

        By having a setter, a user can change this week to a
        different week for testing purposes (like the week prior
        to Thanksgiving to ensure everything is working correctly).
        """
        logger.info(
            f"Updating NFL Thanksgiving Calendar week from {self.nfl_thanksgiving_calendar_week} to {week}..."
        )
        self.week_delta = week - 1

    def _encode_url_params(self, url: str) -> str:
        """
        Helper function to encode year (season) and week as url params.
        """
        params = {"season": self.year, "week": self.nfl_thanksgiving_calendar_week}
        params_encoded = urlencode(params)

        url_encoded = f"{url}{params_encoded}"

        return url_encoded

    @property
    def projected_pts_url(self) -> str:
        """
        Url for web scrapping (or API calling) PROJECTED fantasy points.

        The base url will always remain the same. However, this method
        will create a query url for the desired year, week, and
        stats type (projected) in order to scrape the correct player
        fantasy points.
        """
        url = "https://api.fantasy.nfl.com/v2/players/weekprojectedstats?"
        projected_pts_url = self._encode_url_params(url)
        return projected_pts_url

    @property
    def actual_pts_url(self) -> str:
        """
        Create a url for web scrapping (or API calling) fantasy points.

        The base url will always remain the same. However, this method
        will create a query url for the desired year, week, and
        stats type in order to scrape the correct player fantasy points.
        """
        url = "https://api.fantasy.nfl.com/v2/players/weekstats?"
        actual_pts_url = self._encode_url_params(url)
        return actual_pts_url

    @staticmethod
    def scrape_url(query_url: str, verbose: bool = True) -> Dict[str, Any]:
        """
        Send a GET request for the query url provided.
        Return the json dictionary received from the request.
        """
        response = requests.get(query_url)

        if verbose:
            if response.status_code == requests.codes.ok:
                logger.info(f"\tSuccessful API response obtained for: {query_url}")
            else:
                logger.info(f"\tWARNING: API response unsuccessful for: {query_url}")

        return response.json()

    def get_projected_player_pts(self) -> Dict[str, Any]:
        """
        Collect players and their corresponding PROJECTED points.

        A GET request is sent to the  projected_pts_url. The returned
        json is parsed to only get relevant player points.
        """
        # This is a unique identifier NOT truly a GAME identifier
        logger.info("\nCollecting projected player points...")
        response_json = self.scrape_url(self.projected_pts_url)
        system_config = response_json["systemConfig"].get("currentGameId")
        projected_player_pts = response_json["games"][system_config].get("players")

        return projected_player_pts

    def get_actual_player_pts(self) -> Dict[str, Any]:
        """
        Collect players and their corresponding ACTUAL points.

        A GET request is sent to the  actual_pts_url. The returned
        json is parsed to only get relevant player points.
        """
        # This is a unique identifier NOT truly a GAME identifier
        logger.info("\nCollecting actual player points...")
        response_json = self.scrape_url(self.actual_pts_url)
        system_config = response_json["systemConfig"].get("currentGameId")
        actual_player_pts = response_json["games"][system_config].get("players")

        return actual_player_pts

    def _player_ids_need_update(self) -> bool:
        """
        Helper function to check if player ids exist.
        If it does, player ids need to be updated only if ``year`` does
        not match THIS year.
        """
        if self.dir_config.player_ids_json_path.exists():
            player_ids_loaded = utils.load_from_json(self.dir_config.player_ids_json_path)

            if player_ids_loaded.get("year") == self.year:
                return False
        return True

    def _get_player_metadata(self, player_id: str) -> Dict[str, str]:
        """
        Helper function to scrape NFL.com for individual player data.
        """
        url = f"https://api.fantasy.nfl.com/v2/player/ngs-content?playerId={player_id}"
        response_json = self.scrape_url(url, verbose=False)

        # This is a unique identifier not truly a GAME identifier
        game_id = list(response_json["games"].keys())[0]
        metadata = response_json["games"][game_id]["players"].get(player_id)

        return metadata

    def _update_single_player_id(
        self, pid: str, pulled_player_id_data: Dict[str, Dict[str, Optional[str]]]
    ) -> None:
        player_metadata = self._get_player_metadata(pid)
        pulled_player_id_data[pid] = {}
        pulled_player_id_data[pid]["name"] = player_metadata.get("name")
        pulled_player_id_data[pid]["position"] = player_metadata.get("position")
        pulled_player_id_data[pid]["team"] = player_metadata.get("nflTeamAbbr")
        pulled_player_id_data[pid]["injury"] = player_metadata.get("injuryGameStatus")

    def update_player_ids(self, projected_player_pts: Dict[str, Any]) -> None:
        """
        Updates player ids (name, pos, team) and saves to json file.
        """
        if self._player_ids_need_update():
            pulled_player_ids = list(projected_player_pts.keys())

            # Sort by numerical string value
            pulled_player_ids.sort(key=int)

            # Add a year reference (for checking)
            pulled_player_ids.insert(0, "year")
            pulled_player_id_data = {pid: {} for pid in pulled_player_ids}  # type: ignore[var-annotated]

            for pid in tqdm(pulled_player_ids, desc="\tUpdating player ids", ncols=75):
                if pid == "year":
                    pulled_player_id_data[pid] = self.year  # type: ignore[assignment]

                else:
                    self._update_single_player_id(pid, pulled_player_id_data)

            utils.write_to_json(
                json_dict=pulled_player_id_data,
                filename=self.dir_config.player_ids_json_path,
            )

        else:
            logger.info(f"\tPlayer ids are up to date at {self.dir_config.player_ids_json_path}")
