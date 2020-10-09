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

    # Set option for nice DataFrame display
    pd.options.display.width = None

    year = utils.get_current_year()
    print(f"\n{'-'*5} {year} Turkey Bowl {'-'*5}")

    draft = Draft(year)
    draft.setup()

    participant_teams = draft.load()

    # Do we actually need the drafted players?
    # I'd like to see all the projected points and all the player ids since
    # the player ids show injury. If we want to draft one player but he is injured
    # it's easy to see who to swap for if we store all the data.
    # Similarly, it would be nice to save all the projected points for future referees...
    # I think the check_players_have_been_drafted should include what this below
    # function does...
    # Also... this should probably be a draft method... not utils
    drafted_players = utils.collect_drafted_players(participant_teams)

    # If all teams are blank, exit
    if not utils.check_players_have_been_drafted(drafted_players):
        print(
            f"\nNo players have been drafted yet! Please complete the draft for {year}."
        )
        exit()

    scraper = Scraper(year)

    # Pull ALL player projected points (takes ~ 5 minutes)
    # Used to associate player id with player name of drafted players.
    # Useful for determining which players are eligible for draft.
    # (see injury status in player_ids.json)
    # This will be done once and only once.
    projected_player_pts = scraper.get_projected_player_pts()
    scraper.update_player_ids(projected_player_pts)

    # Update needed here....
    # Check if projected_player_pts.csv exists...
    # If not, pull get_projected_players_pts, update_player_ids, create
    # If exists, load projected_player_pts...

    # This is fast... and merge is fast as well, so no need to limit here...
    actual_player_pts = scraper.get_actual_player_pts()

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
