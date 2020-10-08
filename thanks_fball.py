"""
Thanksgiving Football module
"""
# Standard libraries
from pathlib import Path

# Third-party libraries
import pandas as pd

# Local libraries
import aggregate
import utils
from draft import Draft
from leader_board import LeaderBoard
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

    # May need a check function here to ensure draft is complete
    # Load drafted teams
    participant_teams = draft.load()

    # Instantiate Scraper
    scraper = Scraper(year)

    # TODO: projected points only need to be pulled once...
    # check if df exists (these won't change)
    projected_player_pts = scraper.get_projected_player_pts()
    actual_player_pts = scraper.get_actual_player_pts()

    # # Update player ids (needs to be done once)
    scraper.update_player_ids(projected_player_pts)

    # # Create a DataFrame of PROJECTED player pts
    # #   Create/Save if it doesn't already exist
    # #   Load if it already exists
    week = scraper.nfl_thanksgiving_calendar_week
    projected_player_pts_df = aggregate.create_player_pts_df(
        year=year,
        week=week,
        player_pts=projected_player_pts,
        savepath=Path(f"archive/{year}/{year}_{week}_projected_player_pts.csv"),
    )

    # Create a DataFrame of ACTUAL player pts
    # This will be created as multiple points in time.
    # Note: ``actual_player_pts`` will be none until games start
    if actual_player_pts:
        actual_player_pts_df = aggregate.create_player_pts_df(
            year=year, week=week, player_pts=actual_player_pts, savepath=None
        )
    else:
        actual_player_pts_df = projected_player_pts_df[["Player", "Team"]].copy()
        actual_player_pts_df["ACTUAL_pts"] = 0.0

    # Merge points to teams
    participant_teams = aggregate.merge_points(
        participant_teams, projected_player_pts_df
    )
    participant_teams = aggregate.merge_points(participant_teams, actual_player_pts_df)

    # Sort robust columns so actual is next to projected
    participant_teams = aggregate.sort_robust_cols(participant_teams)

    # Write robust scores to excel for reviewing if desired
    aggregate.write_robust_participant_team_scores(
        year=year,
        week=week,
        participant_teams=participant_teams,
        savepath=Path(
            f"archive/{year}/{year}_{week}_robust_participant_player_pts.xlsx"
        ),
    )

    board = LeaderBoard(year, participant_teams)
    board.display()
    board.save()


if __name__ == "__main__":
    main()
