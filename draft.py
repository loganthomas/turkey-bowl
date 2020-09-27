"""
Draft functions
"""
# Standard libraries
import json
import random
from pathlib import Path

# Third-party libraries
import pandas as pd


class Draft:
    def __init__(self, year: int) -> None:
        self.year = year
        self.output_dir = Path(f"archive/{self.year}")

    def setup(self) -> None:
        """ Instantiate draft with needed files and directories. """
        self.draft_order_path = self.output_dir.joinpath(
            f"{self.year}_draft_order.json"
        )

        self.draft_sheet_path = self.output_dir.joinpath(
            f"{self.year}_draft_sheet.xlsx"
        )

        if not self.output_dir.exists():
            self.output_dir.mkdir()

        if not self.draft_order_path.exists():
            participant_list = input(
                "\nPlease enter the participants separated by a comma: "
            ).split(",")

            self.participant_list = [*map(str.strip, participant_list)]

            self.draft_order = random.sample(
                self.participant_list, len(self.participant_list)
            )

            draft_order_dict = {p: i for i, p in enumerate(self.draft_order, 1)}

            print(f"\n\tDraft Order: {self.draft_order}")

            with open(self.draft_order_path, "w") as draft_order_file:
                json.dump(draft_order_dict, draft_order_file)

            print(f"\tSaved draft order to {self.draft_order_path}")

        else:
            print(f"\nDraft order already exists at {self.draft_order_path}")
            with open(self.draft_order_path, "r") as draft_order_file:
                draft_order_dict = json.load(draft_order_file)

            self.participant_list = list(draft_order_dict.keys())
            self.draft_order = list(draft_order_dict.keys())

            print(f"\n\tDraft Order: {self.draft_order}")

        if not self.draft_sheet_path.exists():
            draft_info = {
                "Position": [
                    "QB",
                    "RB_1",
                    "RB_2",
                    "WR_1",
                    "WR_2",
                    "TE",
                    "Flex (RB/WR/TE)",
                    "K",
                    "Defense (Team Name)",
                    "Bench (RB/WR/TE)",
                ],
                "Player": [""] * 10,
                "Team": [""] * 10,
            }
            draft_df = pd.DataFrame(draft_info)

            with pd.ExcelWriter(self.draft_sheet_path) as writer:
                for participant in self.draft_order:
                    draft_df.to_excel(
                        writer, sheet_name=participant.title(), index=False
                    )


def get_draft_data(draft_file_path):
    """
    Parses an excel spreadsheet into participant teams.

    The drafted teams should be collected within one excel spreadsheet
    in which each participant is a separate sheet. The sheet names
    correspond to the names of the participants and each sheet should have
    a 'Position' column, a 'Player', and a 'Team' column. For the time being,
    the draft-able positions are as follows:
        'QB', 'RB_1', 'RB_2', 'WR_1', 'WR_2', 'TE',
        'Flex (RB/WR)', 'K', 'Defense (Team Name)', 'Bench (RB/WR)'.

    Args:
        draft_file_path (pathlib.Path): Path to excel spreadsheet. Ideally, each year will
            have its own directory and the excel spreadsheet would be named
            'draft_sheet_{year}.xlsx'. For example, in the year 2018,
            xlsx_path = '2018/draft_sheet_2018.xlsx'.

    Returns:
        participant_teams (dict): A dictionary of participant (str),
        team (pandas DataFrame) key, value pairs.
        (i.e., each participants drafted team as a DF housed in a dict).
    """
    # Load excel sheet
    xlsx = pd.ExcelFile(draft_file_path)

    # Get each participant's drafted players
    participant_teams = {p: xlsx.parse(p) for p in xlsx.sheet_names}

    return participant_teams
