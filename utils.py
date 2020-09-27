"""
Utility functions
"""
# Standard libraries
from datetime import datetime
from typing import Dict

# Third-party libraries
import pandas as pd


def get_current_year() -> int:
    return datetime.now().year


def merge_points(
    participant_teams: Dict[str, pd.DataFrame], players_df: pd.DataFrame
) -> Dict[str, pd.DataFrame]:
    """
    Notes:
        Although the 'Bench (RB/WR)' player is reported in the
        player_stats DF, it is not used to calculate the total points for a
        given participant. It is assumed that the 'Bench (RB/WR)' player
        is listed last in the excel spreadsheet.
    """
    for participant, participant_team in participant_teams.items():
        merged = pd.merge(
            participant_team,
            players_df,
            left_on=["Player", "Team"],
            right_on=["name", "team"],
            how="left",
        )

        merged = merged.drop(
            [
                "name",
                "team",
            ],
            axis=1,
        )
        participant_teams[participant] = merged

        # Defensive programming (ignore bench player in case written in as NONE in .xlsx)
        if sum(pd.isna(merged[:-1]["id"])) > 0:
            print(f"WARNING!! {participant}'s merge has missing player ids")

    return participant_teams


def create_leader_board(year, output_dir, participant_teams):
    """
    Notes: Bench player assumed last row in excel sheet.
    Left out of calculation but still shown.
    """
    # Instantiate writer to save leader board and data
    writer = pd.ExcelWriter(
        output_dir.joinpath(f"{year}_leader_board.xlsx"), engine="xlsxwriter"
    )

    # Instantiate leader board data
    leader_board_data = {}

    for participant, participant_team in participant_teams.items():
        print(f"\n### {participant.upper()} stats ###\n")
        print(participant_team)
        print("\n\n\n")

        # Assumes bench is last row (shown but not included in sum)
        team_pts = participant_team[:-1]["act_pts"].sum()

        leader_board_data[participant] = team_pts

        # Save to sheet in excel
        participant_team.to_excel(writer, sheet_name=participant)

    # Create a DataFrame from point_totals
    leader_board = pd.DataFrame.from_dict(
        leader_board_data, orient="index", columns=["PTS"]
    )

    # Sort the leader board on highest pts to lowest pts
    leader_board = leader_board.sort_values("PTS", ascending=False)

    # Create column to show how far ahead each participant is compared to next
    leader_board["margin"] = leader_board["PTS"].diff(-1)

    # Create column to show how far out of lead they are
    leader_board["pts_back"] = leader_board.iloc[0, 0] - leader_board["PTS"].values

    # Print details on points
    print(
        f"\n{leader_board.index[0]} winning with {round(leader_board.iloc[0,0],2)} pts\n"
    )
    print(leader_board)
    print("\n")

    # Save leader board as sheet in excel
    leader_board.to_excel(writer, sheet_name="leader_board")
    writer.save()
