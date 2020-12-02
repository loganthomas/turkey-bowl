"""
Thanksgiving Football module
"""
# Standard libraries
import sys
from pathlib import Path

# Third-party libraries
import pandas as pd

# Local libraries
from turkey_bowl import aggregate, utils
from turkey_bowl.draft import Draft
from turkey_bowl.leader_board import LeaderBoard
from turkey_bowl.scrape import Scraper


def main():

    # Set option for nice DataFrame display
    pd.options.display.width = None

    year = utils.get_current_year()
    print(f"\n{'-'*5} {year} Turkey Bowl {'-'*5}")

    draft = Draft(year)
    draft.setup()

    participant_teams = draft.load()

    scraper = Scraper(year)
    week = scraper.nfl_thanksgiving_calendar_week

    projected_player_pts_path = Path(
        f"{draft.output_dir}/{year}_{week}_projected_player_pts.csv"
    )
    if aggregate.check_projected_player_pts_pulled(
        year, week, savepath=projected_player_pts_path
    ):
        projected_player_pts_df = pd.read_csv(projected_player_pts_path, index_col=0)

    else:
        projected_player_pts = scraper.get_projected_player_pts()
        scraper.update_player_ids(projected_player_pts)
        projected_player_pts_df = aggregate.create_player_pts_df(
            year=year,
            week=week,
            player_pts=projected_player_pts,
            savepath=projected_player_pts_path,
        )

    # If all teams are blank, exit
    # Check done after projected_player_pts so that projected points
    #   are pulled during draft.
    if not draft.check_players_have_been_drafted(participant_teams):
        print(
            f"\nNot all players have been drafted yet! Please complete the draft for {year}."
        )
        sys.exit()

    actual_player_pts = scraper.get_actual_player_pts()

    # To get to run for COVID
    del actual_player_pts["2560762"]
    del actual_player_pts["2550834"]
    del actual_player_pts["2563734"]
    del actual_player_pts["2559141"]
    del actual_player_pts["2564412"]
    del actual_player_pts["2562799"]
    del actual_player_pts["2543650"]
    del actual_player_pts["2561103"]
    del actual_player_pts["2560884"]
    del actual_player_pts["2562591"]
    del actual_player_pts["2532986"]
    del actual_player_pts["2562776"]
    del actual_player_pts["2558191"]
    del actual_player_pts["2561585"]
    del actual_player_pts["2557033"]
    del actual_player_pts["2562957"]

    if actual_player_pts:
        actual_player_pts_df = aggregate.create_player_pts_df(
            year=year, week=week, player_pts=actual_player_pts, savepath=None
        )
    else:
        actual_player_pts_df = projected_player_pts_df[["Player", "Team"]].copy()
        actual_player_pts_df["ACTUAL_pts"] = 0.0

    # Merge points to teams
    participant_teams = aggregate.merge_points(
        participant_teams, projected_player_pts_df, verbose=False
    )

    participant_teams = aggregate.merge_points(
        participant_teams, actual_player_pts_df, verbose=True
    )

    # Sort robust columns so actual is next to projected
    participant_teams = aggregate.sort_robust_cols(participant_teams)

    # Write robust scores to excel for reviewing if desired
    aggregate.write_robust_participant_team_scores(
        participant_teams=participant_teams,
        savepath=Path(
            f"{draft.output_dir}/{year}_{week}_robust_participant_player_pts.xlsx"
        ),
    )

    board = LeaderBoard(year, participant_teams)
    board.display()
    board.save(f"{draft.output_dir}/{year}_leader_board.xlsx")


if __name__ == "__main__":
    main()
