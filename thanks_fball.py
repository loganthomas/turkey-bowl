"""
Thanksgiving Football module
"""
# Third-party libraries
import pandas as pd

# Local libraries
import aggregate
import api
import utils
from draft import Draft
from scrape import Scraper


def main():
    """
    TODO:
        - Consider making a leader board class with an updated method?
    """
    # Set option for nice DataFrame display
    pd.options.display.width = None

    # Establish current year
    year = utils.get_current_year()
    print(f"\n{'-'*5} {year} Turkey Bowl {'-'*5}")

    # Instantiate Draft
    draft = Draft(year)
    draft.setup()

    # Load drafted teams
    participant_teams = draft.load()

    # Instantiate Scraper
    scraper = Scraper(year)

    # TODO: projected points only need to be pulled once...
    # check if df exists (these won't change)
    projected_player_pts = scraper.get_projected_player_pts()
    actual_player_pts = scraper.get_actual_player_pts()

    # Update player ids (needs to be done once)
    scraper.update_player_ids(projected_player_pts)

    # Create a DataFrame of PROJECTED player pts
    #   Create/Save if it doesn't already exist
    #   Load if it already exists
    week = scraper.nfl_thanksgiving_calendar_week
    projected_player_pts_df = aggregate.create_player_pts_df(
        year=year, week=week, player_pts=projected_player_pts
    )

    # Create a DataFrame of ACTUAL player pts
    # This will be created as multiple points in time.
    # Note: ``actual_player_pts`` will be none until games start
    if actual_player_pts is not None:
        actual_player_pts_df = aggregate.create_player_pts_df(actual_player_pts)

    # Determine week to pull for stats
    nfl_start_cal_week_num = utils.get_nfl_start_week(year)
    thanksgiving_cal_week_num = utils.get_thanksgiving_week(year)

    week = utils.calculate_nfl_thanksgiving_week(
        nfl_start_cal_week_num,
        thanksgiving_cal_week_num,
    )

    # Collect prior weeks player data (notice week - 1)
    prior_players_df_path = api.create_prior_players_file_path(
        year, week - 1, output_dir
    )

    # Check if prior week players data exists, if not create it (notice week - 1)
    prior_players_df = api.check_prior_players_file_exists(
        year, week - 1, prior_players_df_path
    )

    # Merge prior week players data to drafted teams (this will be prior weeks data)
    participant_teams = utils.merge_points(participant_teams, prior_players_df)

    # Update projected points to current week (currently week prior projections)
    participant_teams = api.update_pts(
        year=year,
        week=week,
        participant_teams=participant_teams,
        stats_type="projected",
    )

    # Update actual points to current week (currently week prior actuals)
    # Can call both below multiple times when launched from IPython console
    participant_teams = api.update_pts(
        year=year, week=week, participant_teams=participant_teams, stats_type="actual"
    )

    utils.create_leader_board(year, output_dir, participant_teams)


if __name__ == "__main__":
    main()
