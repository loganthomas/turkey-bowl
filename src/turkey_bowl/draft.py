"""
Draft functions
"""
import itertools
import json
import logging
import random
import time
from pathlib import Path
from typing import Dict, Optional

import click_spinner
import pandas as pd

from turkey_bowl import utils

logger = logging.getLogger(__name__)


class Draft:
    def __init__(self, year: int, root: Optional[str] = None) -> None:
        self.dir_config = utils.load_dir_config(year, root)
        self.year = year

    def __repr__(self):
        return f"Draft({self.year})"

    def __str__(self):
        return f"Turkey Bowl Draft: {self.year}"

    def setup(self) -> None:
        """Instantiate draft with attributes, files, and directories."""
        if not self.dir_config.output_dir.exists():
            self.dir_config.output_dir.mkdir()

        if not self.dir_config.draft_order_path.exists():
            participant_list = input(
                "\nPlease enter the participants separated by a comma: "
            ).split(",")

            self.participant_list = [*map(str.strip, participant_list)]

            self.draft_order = random.sample(
                self.participant_list, len(self.participant_list)
            )

            for i, participant in enumerate(self.draft_order, 1):
                logger.info(f"Drafting in slot {i}...")
                with click_spinner.spinner():
                    time.sleep(3)
                logger.info(f"{participant}\n")

            logger.info(f"\n\tDraft Order: {self.draft_order}")

            draft_order_dict = {p: i for i, p in enumerate(self.draft_order, 1)}

            with open(self.dir_config.draft_order_path, "w") as draft_order_file:
                json.dump(draft_order_dict, draft_order_file)

            logger.info(f"\tSaved draft order to {self.dir_config.draft_order_path}")

        else:
            logger.info(
                f"\nDraft order already exists at {self.dir_config.draft_order_path}"
            )
            with open(self.dir_config.draft_order_path, "r") as draft_order_file:
                draft_order_dict = json.load(draft_order_file)

            self.participant_list = list(draft_order_dict.keys())
            self.draft_order = list(draft_order_dict.keys())

            logger.info(f"\n\tDraft Order: {self.draft_order}")

        if not self.dir_config.draft_sheet_path.exists():
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
                "Player": [" "] * 10,  # intentional space so strip works in load
                "Team": [" "] * 10,  # intentional space so strip works in load
            }
            draft_df = pd.DataFrame(draft_info)

            with pd.ExcelWriter(self.dir_config.draft_sheet_path) as writer:
                for participant in self.draft_order:
                    draft_df.to_excel(
                        writer, sheet_name=participant.title(), index=False
                    )

                    # Ensure Position text is correct spacing length
                    worksheet = writer.sheets[participant.title()]
                    max_len = max(map(len, draft_info["Position"]))
                    worksheet.set_column(0, 0, max_len)

    def load(self) -> Dict[str, pd.DataFrame]:
        """
        Loads draft data by parsing excel spreadsheet.

        The drafted teams should be collected within one excel
        spreadsheet in which each participant is a separate sheet.

        The sheet names correspond to the names of the participants and
        each sheet should have a 'Position' column, a 'Player', and a
        'Team' column.

        For the time being, the draft-able positions are as follows:
            'QB', 'RB_1', 'RB_2', 'WR_1', 'WR_2', 'TE',
            'Flex (RB/WR/TE)', 'K', 'Defense (Team Name)',
            'Bench (RB/WR/TE)'.
        """
        participant_teams = pd.read_excel(
            self.dir_config.draft_sheet_path, sheet_name=None, engine="openpyxl"
        )

        # Strip all whitespace
        # All columns are string values so can be apply across DataFrame
        for participant, participant_team in participant_teams.items():
            participant_teams[participant] = participant_team.apply(
                lambda x: x.str.strip()
            )

        return participant_teams

    @staticmethod
    def check_players_have_been_drafted(
        participant_teams: Dict[str, pd.DataFrame]
    ) -> bool:
        """
        Helper function to determine if early stopping should occur.
        If all players are equal to "" within the participant teams,
        then no players have been drafted and the process should end.
        """
        drafted_players = [
            participant_team["Player"].tolist()
            for participant_team in participant_teams.values()
        ]

        drafted_players = [
            player for player in itertools.chain.from_iterable(drafted_players)
        ]

        players_have_been_drafted = all(player != "" for player in drafted_players)

        return players_have_been_drafted
