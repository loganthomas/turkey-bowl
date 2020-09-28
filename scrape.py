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
from pathlib import Path
from typing import Any, Dict
from urllib.parse import urlencode

# Third-party libraries
import numpy as np
import pandas as pd
import requests
from tqdm import tqdm

# Local libraries
import utils


class Scraper:
    def __init__(self, year: int) -> None:
        self.year = year
        self.player_ids_json_path = Path("./player_ids.json")
        self.stat_ids_json_path = Path("./stat_ids.json")

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
        Url for web scrapping (or API calling) PRJECTED fantasy points.

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
                print(f"Successful API response obtained for: {query_url}")
            else:
                print(f"WARNING: API response unsuccessful for: {query_url}")

        return response.json()

    def get_projected_player_pts(self) -> Dict[str, Any]:
        """
        Collect players and their corresponding PROJECTED points.

        A GET request is sent to the  projected_pts_url. The returned
        json is parsed to only get relevant player points.
        """
        # This is a unique identifier NOT truly a GAME identifier
        print("\nCollecting projected player points...")
        response_json = self.scrape_url(self.projected_pts_url)
        system_config = response_json.get("systemConfig").get("currentGameId")  # type: ignore[union-attr]
        projected_player_pts = response_json.get("games").get(system_config).get("players")  # type: ignore[union-attr]

        return projected_player_pts

    def get_actual_player_pts(self) -> Dict[str, Any]:
        """
        Collect players and their corresponding PROJECTED points.

        A GET request is sent to the  projected_pts_url. The returned
        json is parsed to only get relevant player points.
        """
        # This is a unique identifier NOT truly a GAME identifier
        print("\nCollecting actual player points...")
        response_json = self.scrape_url(self.actual_pts_url)
        system_config = response_json.get("systemConfig").get("currentGameId")  # type: ignore[union-attr]
        actual_player_pts = response_json.get("games").get(system_config).get("players")  # type: ignore[union-attr]

        return actual_player_pts

    def _check_player_ids_need_update(self) -> bool:
        """
        Helper function to check if player ids exist.
        If it does, player ids need to be updated only if ``year`` does
        not match THIS year.
        """
        if self.player_ids_json_path.exists():
            player_ids_loaded = utils.load_from_json(self.player_ids_json_path)

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
        game_id = list(response_json.get("games").keys())[0]  # type: ignore[union-attr]
        metadata = response_json.get("games").get(game_id).get("players")[player_id]  # type: ignore[union-attr]

        return metadata

    def update_player_ids(self, projected_player_pts: Dict[str, Any]) -> None:
        """
        Updates player ids (name, pos, team) and saves to json file.
        """
        if self._check_player_ids_need_update():
            pulled_player_ids = list(projected_player_pts.keys())

            # Sort by numerical string value
            pulled_player_ids.sort(key=int)

            # Add a year reference (for checking)
            pulled_player_ids.insert(0, "year")
            pulled_player_data = {pid: {} for pid in pulled_player_ids}  # type: ignore[var-annotated]

            for pid in tqdm(pulled_player_ids, desc="Updating player ids", ncols=75):
                if pid == "year":
                    pulled_player_data[pid] = self.year  # type: ignore[assignment]

                else:
                    player_metadata = self._get_player_metadata(pid)

                    pulled_player_data[pid]["name"] = player_metadata.get("name")
                    pulled_player_data[pid]["position"] = player_metadata.get(
                        "position"
                    )
                    pulled_player_data[pid]["team"] = player_metadata.get("nflTeamAbbr")
                    pulled_player_data[pid]["injury"] = player_metadata.get(
                        "injuryGameStatus"
                    )

            utils.write_to_json(
                json_dict=pulled_player_data, filename=self.player_ids_json_path
            )

        else:
            print(f"\nPlayer ids are up to date at: {self.player_ids_json_path}")

    @staticmethod
    def _get_player_pnts_stat_type(player_pts: Dict[str, Any]) -> str:
        """
        Helper function to get the stat type within the pulled player
        points. Will be either 'projectedStats' or 'stats'.
        """
        unique_type = set([list(v.keys())[0] for v in player_pts.values()])

        if len(unique_type) > 1:
            raise ValueError(f"More than one unique stats type detected: {unique_type}")

        stats_type = list(unique_type)[0]

        if stats_type not in ("projectedStats", "stats"):
            raise ValueError(
                f"Unrecognized stats type: '{stats_type}'. Expected either 'projectedStats' or 'stats'."
            )

        return stats_type

    def _unpack_player_pnts(self, player_pts_dict: Dict[str, Any]) -> Dict[str, str]:
        """
        Helper function to unpack player points nested dictionaries.
        """
        year = self.year
        week = self.nfl_thanksgiving_calendar_week

        ((_, points_dict),) = player_pts_dict.items()
        points_dict = points_dict.get("week").get(str(year)).get(str(week))

        return points_dict

    def create_player_pts_df(self, player_pts: Dict[str, Any]) -> pd.DataFrame:
        """
        Create a DataFrame to house all player projected and actual points.
        The ``player_pts`` argument can be ``projected_player_pts`` or
        ``actual_player_pts``.
        """
        # Determine whether provided projected ('projectedStats') or
        # actual player points ('stats'). Actual points will need to
        # be pulled multiple times throughout as more games are
        # played/completed. Projected points should be pulled once and
        # only once.
        stats_type = self._get_player_pnts_stat_type(player_pts)

        proj_filename = Path(f"archive/{self.year}").joinpath(
            f"{self.year}_{self.nfl_thanksgiving_calendar_week}_projected_player_pts.csv"
        )

        if (stats_type == "projectedStats") & (proj_filename.exists()):
            print(f"Projected player data already exists at: {proj_filename}")
            player_pts_df = pd.read_csv(proj_filename, index_col=0)

        else:

            index = []
            points = []

            for pid, player_pnts_dict in player_pts.items():
                points_dict = self._unpack_player_pnts(player_pnts_dict)
                index.append(pid)
                points.append(points_dict)

            player_pts_df = pd.DataFrame(points, index=index)

            # Get definition of each point attribute
            stat_ids_dict = utils.load_from_json(self.stat_ids_json_path)
            stat_defns = {
                k: v["name"].replace(" ", "_") for k, v in stat_ids_dict.items()
            }
            player_pts_df = player_pts_df.rename(columns=stat_defns)

            if stats_type == "projectedStats":
                prefix = "PROJ_"

            if stats_type == "stats":
                prefix = "ACTUAL_"

            player_pts_df = player_pts_df.add_prefix(prefix)
            player_pts_df = player_pts_df.reset_index().rename(
                columns={"index": "Name"}
            )

            # Get definition of each player team and name based on player id
            player_ids = utils.load_from_json(self.player_ids_json_path)
            team = player_pts_df["Name"].apply(lambda x: player_ids[x]["team"])
            player_pts_df.insert(1, "Team", team)

            player_defns = {k: v["name"] for k, v in player_ids.items() if k != "year"}
            name = player_pts_df["Name"].apply(lambda x: player_defns[x])
            player_pts_df["Name"] = name

            # Make pts col the third column for easy access
            pts_col = player_pts_df.filter(regex="pts")
            pts_col_name = f"{prefix}pts"
            player_pts_df = player_pts_df.drop(pts_col_name, axis=1)
            player_pts_df.insert(2, pts_col_name, pts_col)

            # Write projected players to csv so only done once
            if stats_type == "projectedStats":

                player_pts_df.to_csv(proj_filename)

        return player_pts_df
