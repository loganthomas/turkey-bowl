"""
Leader board methods
"""
# Standard libraries
from pathlib import Path
from typing import Dict

# Third-party libraries
import pandas as pd


class LeaderBoard:
    def __init__(self, year: int, participant_teams: Dict[str, pd.DataFrame]) -> None:
        self.year = year
        self.participant_teams = participant_teams
        self.filter_cols = ["Position", "Player", "Team", "ACTUAL_pts", "PROJ_pts"]
        self.output_file_path = Path(
            f"archive/{self.year}/{self.year}_leader_board.xlsx"
        )

    @property
    def data(self) -> pd.DataFrame:
        leader_board_data = {}

        for participant, participant_team in self.participant_teams.items():

            # Assumes Bench player is last row (displayed but not included in sum)
            team_pts = participant_team[:-1]["ACTUAL_pts"].sum().round(3)
            leader_board_data[participant] = team_pts

        # Create a DataFrame from point_totals
        leader_board_df = pd.DataFrame.from_dict(
            leader_board_data, orient="index", columns=["PTS"]
        )

        # Sort the leader board on highest pts to lowest pts
        leader_board_df = leader_board_df.sort_values("PTS", ascending=False)

        # Create column to show how far ahead each participant is compared to next
        leader_board_df["margin"] = leader_board_df["PTS"].diff(-1)

        # Create column to show how far out of lead they are
        leader_board_df["pts_back"] = (
            leader_board_df.iloc[0, 0] - leader_board_df["PTS"].values
        )

        return leader_board_df

    def display(self) -> None:
        for participant, participant_team in self.participant_teams.items():
            print(f"\n### {participant.upper()} stats ###\n")
            print(participant_team[self.filter_cols])
            print("\n\n\n")

        print(
            f"\n{self.data.index[0]} winning with {round(self.data.iloc[0,0],2)} pts\n"
        )
        print(self.data)
        print("\n")

    def save(self) -> None:
        print(f"Saving LeaderBoard to: {self.output_file_path}...")

        with pd.ExcelWriter(self.output_file_path) as writer:

            # Center columns
            workbook = writer.book
            center = workbook.add_format()
            center.set_align("center")
            center.set_align("vcenter")

            # Leader board sheet
            self.data.to_excel(writer, sheet_name="Leader Board")
            worksheet = writer.sheets["Leader Board"]

            # Start enumerate at 1 since index written
            for i, col in enumerate(self.data, 1):
                series = self.data[col]
                max_len = max(series.astype(str).map(len).max(), len(str(series.name)))

                # Add a little extra spacing
                worksheet.set_column(i, i, max_len + 1, center)

            # Individual Players
            for participant, participant_team in self.participant_teams.items():
                participant_team[self.filter_cols].to_excel(
                    writer, sheet_name=participant, index=False
                )

                # Auto-format column lengths and center columns
                worksheet = writer.sheets[participant]

                for i, col in enumerate(participant_team):
                    series = participant_team[col]
                    max_len = max(
                        series.astype(str).map(len).max(), len(str(series.name))
                    )

                    # Add a little extra spacing
                    if col in ("Position", "Player", "Team"):
                        worksheet.set_column(i, i, max_len + 2)
                    else:
                        worksheet.set_column(i, i, max_len + 2, center)
