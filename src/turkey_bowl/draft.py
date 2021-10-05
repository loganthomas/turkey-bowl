"""
Draft functions
"""
# Standard libraries
import itertools
import json
import random
import time
from pathlib import Path
from typing import Dict

# Third-party libraries
import click_spinner
import pandas as pd
from traits.api import Bool, Button, HasTraits, Int, List, Property, Str
from traitsui.api import Group, HGroup, Item, ListStrEditor, UItem, VGroup, View


class Draft:
    def __init__(self, year: int) -> None:
        self.year = year
        self.output_dir = Path(f"archive/{self.year}")
        self.draft_order_path = self.output_dir.joinpath(
            f"{self.year}_draft_order.json"
        )
        self.draft_sheet_path = self.output_dir.joinpath(
            f"{self.year}_draft_sheet.xlsx"
        )

    def __repr__(self):
        return f"Draft({self.year})"

    def __str__(self):
        return f"Turkey Bowl Draft: {self.year}"

    def setup(self) -> None:
        """ Instantiate draft with attributes, files, and directories. """
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

            print()
            for i, participant in enumerate(self.draft_order, 1):
                print(f"Drafting in slot {i}...")
                with click_spinner.spinner():
                    time.sleep(3)
                print(f"{participant}\n")

            print(f"\n\tDraft Order: {self.draft_order}")

            draft_order_dict = {p: i for i, p in enumerate(self.draft_order, 1)}

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
                "Player": [" "] * 10,  # intentional space so strip works in load
                "Team": [" "] * 10,  # intentional space so strip works in load
            }
            draft_df = pd.DataFrame(draft_info)

            with pd.ExcelWriter(self.draft_sheet_path) as writer:
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
            self.draft_sheet_path, sheet_name=None, engine="openpyxl"
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


class DraftGui(HasTraits):

    undrafted = List(Str)
    drafted = List(Str)
    draft = Button()
    undo = Button()
    player_index = Int()

    participants = List(Str)
    participant_idx = Int()
    participant = Property(depends_on="participant_idx")

    participant0 = List(Str)
    participant1 = List(Str)
    participant2 = List(Str)
    participant3 = List(Str)
    participant4 = List(Str)
    participant5 = List(Str)
    participant_views = List()

    draft_round = Int(1)
    incomplete = Bool(True)

    def _draft_fired(self):
        player = self.undrafted.pop(self.player_index)
        self.drafted.append(player)
        self.participant_views[self.participant_idx].append(player)

        # Snake draft (10 players per team)
        if len(self.drafted) == len(self.participants) * 10:
            self.participants.append("Draft Complete!")
            self.participant_idx = -1
            self.incomplete = False
        elif len(self.drafted) % len(self.participants) == 0:
            self.draft_round += 1
            self.participants = self.participants[::-1]
            self.participant_views = self.participant_views[::-1]
            self.participant_idx = 0
        else:
            self.participant_idx += 1

    def _undo_fired(self):
        if len(self.drafted) == len(self.participant_views) * 10:
            self.participants.remove("Draft Complete!")
            self.participant_idx = len(self.participants) - 1
        elif len(self.drafted) % len(self.participants) == 0:
            self.draft_round -= 1
            self.participants = self.participants[::-1]
            self.participant_views = self.participant_views[::-1]
            self.participant_idx = len(self.participants) - 1
        else:
            self.participant_idx -= 1

        player = self.drafted.pop()
        self.undrafted.append(player)
        self.participant_views[self.participant_idx].remove(player)
        self.incomplete = True

    def _get_participant(self):
        return self.participants[self.participant_idx]

    def _participant_views_default(self):
        """
        Notes
        -----
        There can only be a maximum of 6 participants.
        Rather than being clever, all participants are created and sliced.
        """
        all_views = [
            self.participant0,
            self.participant1,
            self.participant2,
            self.participant3,
            self.participant4,
            self.participant5,
        ]
        return all_views[: len(self.participants)]

    def create_view(self):
        return View(
            Group(
                HGroup(
                    UItem(
                        "undrafted",
                        editor=ListStrEditor(
                            title="Undrafted Players",
                            auto_add=True,
                            selected_index="player_index",
                        ),
                    ),
                    UItem(
                        "drafted",
                        editor=ListStrEditor(title="Drafted Players", auto_add=True),
                    ),
                    VGroup(
                        UItem("draft", enabled_when="incomplete"),
                        UItem("undo", enabled_when="len(drafted)>0"),
                        Item("participant", style="readonly"),
                        Item("draft_round", style="readonly"),
                    ),
                ),
                VGroup(
                    HGroup(
                        Item(
                            "participant0",
                            label=self.participants[0]
                            if len(self.participants) >= 1
                            else "",
                            show_label=True,
                            editor=ListStrEditor(auto_add=True),
                            defined_when="len(participants)>=1",
                        ),
                        Item(
                            "participant1",
                            label=self.participants[1]
                            if len(self.participants) >= 2
                            else "",
                            show_label=True,
                            editor=ListStrEditor(auto_add=True),
                            defined_when="len(participants)>=2",
                        ),
                        Item(
                            "participant2",
                            label=self.participants[2]
                            if len(self.participants) >= 3
                            else "",
                            show_label=True,
                            editor=ListStrEditor(auto_add=True),
                            defined_when="len(participants)>=3",
                        ),
                        Item(
                            "participant3",
                            label=self.participants[3]
                            if len(self.participants) >= 4
                            else "",
                            show_label=True,
                            editor=ListStrEditor(auto_add=True),
                            defined_when="len(participants)>=4",
                        ),
                        Item(
                            "participant4",
                            label=self.participants[4]
                            if len(self.participants) >= 5
                            else "",
                            show_label=True,
                            editor=ListStrEditor(auto_add=True),
                            defined_when="len(participants)>=5",
                        ),
                        Item(
                            "participant5",
                            label=self.participants[5]
                            if len(self.participants) >= 6
                            else "",
                            show_label=True,
                            editor=ListStrEditor(auto_add=True),
                            defined_when="len(participants)>=6",
                        ),
                    ),
                ),
            ),
            title="Draft GUI",
            width=0.75,
            height=0.75,
            resizable=True,
            buttons=["Ok", "Cancel"],  # TODO: fix OK button?
        )
