"""
Draft functions
"""
# Standard libraries
import json
import random
import shutil
from pathlib import Path

# Third-party libraries
import pandas as pd


class Draft:
    def __init__(self, year: int) -> None:
        self.year = year

    def setup(self) -> None:
        """ Instantiate draft with needed files and directories. """
        self.output_dir = Path(f"archive/{self.year}")
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
                "Please enter the participants separated by a comma: "
            ).split(",")
            self.participant_list = [*map(str.strip, participant_list)]

            self.draft_order = random.sample(
                self.participant_list, len(self.participant_list)
            )
            draft_order_dict = {p: i for i, p in enumerate(self.draft_order, 1)}

            with open(self.draft_order_path, "w") as draft_order_file:
                json.dump(draft_order_dict, draft_order_file)
        else:
            with open(self.draft_order_path, "r") as draft_order_file:
                draft_order_dict = json.load(draft_order_file)

            self.participant_list = list(draft_order_dict.keys())
            self.draft_order = list(draft_order_dict.keys())

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

        print(f"\n{'-'*5} {self.year} Turkey Bowl {'-'*5}")
        print(f"\n\tDraft Order: {self.draft_order}")


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


def make_draft_order(year, output_dir, participant_teams):
    """
    Creates a random draft order by shuffling participants.

    Given a dictionary of participants and their corresponding teams,
    this function returns a list of randomly shuffled participants
    that can be used for a random draft order.

    Args:
        participant_teams (dict): A dictionary of participant (str),
            team (pandas DataFrame) key, value pairs.

    Returns:
        draft_order (list of str): A random draft order of participants.
    """
    draft_order_path = output_dir.joinpath(f"{year}_draft_order.csv")

    if draft_order_path.is_file():
        print(f"\nDraft order already exists at {draft_order_path}")
        print(f"\nLoading pre-existing draft order...")

        draft_df = pd.read_csv(draft_order_path)
        draft_order = draft_df["Participant"].tolist()

        print("\nDraft Oder:\n")
        print(f"\t{draft_order}\n")

    else:
        # Gather list of participants
        draft_order = list(participant_teams.keys())

        # Create random list of participants
        random.shuffle(draft_order)

        # Convert to dataframe and save
        draft_df = pd.DataFrame([(p, i) for i, p in enumerate(draft_order, 1)])
        draft_df.columns = ["Participant", "Slot"]

        draft_df.to_csv(draft_order_path, index=False)
        print("\nDraft Oder:\n")
        print(f"\t{draft_order}\n")
        print(f"\tSaved draft order to {draft_order_path}")

    return draft_order_path, draft_order
