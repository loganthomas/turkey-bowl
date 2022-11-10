"""
Leader board methods
"""
import logging
from pathlib import Path
from typing import Dict

import pandas as pd

logger = logging.getLogger(__name__)


class LeaderBoard:
    def __init__(self, year: int, participant_teams: Dict[str, pd.DataFrame]) -> None:
        self.year = year
        self.participant_teams = participant_teams
        self.filter_cols = ["Position", "Player", "Team", "ACTUAL_pts", "PROJ_pts"]

    def __repr__(self):
        return f"LeaderBoard({self.year}, participant_teams={{}})"

    def __str__(self):
        return f"Turkey Bowl Leader Board: {self.year}"

    @property
    def data(self) -> pd.DataFrame:
        leader_board_data = {}

        for participant, participant_team in self.participant_teams.items():

            # Assumes Bench player is last row (displayed but not included in sum)
            team_pts = participant_team[:-1]["ACTUAL_pts"].sum().round(3)
            leader_board_data[participant] = team_pts

        # Create a DataFrame from point_totals
        leader_board_df = pd.DataFrame.from_dict(leader_board_data, orient="index", columns=["PTS"])

        # Sort the leader board on highest pts to lowest pts
        leader_board_df = leader_board_df.sort_values("PTS", ascending=False)

        # Create column to show how far ahead each participant is compared to next
        leader_board_df["margin"] = leader_board_df["PTS"].diff(-1)

        # Create column to show how far out of lead they are
        leader_board_df["pts_back"] = leader_board_df.iloc[0, 0] - leader_board_df["PTS"].values

        return leader_board_df

    def display(self) -> None:
        for participant, participant_team in self.participant_teams.items():
            logger.info(
                f"\n\n### {participant.upper()} stats ###\n{participant_team[self.filter_cols]}\n"
            )

        logger.info(
            f"{self.data.index[0]} winning with {round(self.data.iloc[0,0],2)} pts\n{self.data}\n"
        )

    def save(self, savepath: Path) -> None:
        logger.info(f"Saving LeaderBoard to {savepath}...")

        with pd.ExcelWriter(savepath) as writer:

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
                    max_len = max(series.astype(str).map(len).max(), len(str(series.name)))

                    # Add a little extra spacing
                    if col in ("Position", "Player", "Team"):
                        worksheet.set_column(i, i, max_len + 2)
                    else:
                        worksheet.set_column(i, i, max_len + 2, center)
