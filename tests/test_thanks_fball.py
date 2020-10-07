# Standard libraries
import json

# Third-party libraries
import pandas as pd
import pytest

# Local libraries
from draft import Draft
from thanks_fball import main


# TODO: update with 2020 week 2
@pytest.fixture
def mock_participant_teams():
    participant_teams = {
        "Dodd": {
            "Position": {
                0: "QB",
                1: "RB_1",
                2: "RB_2",
                3: "WR_1",
                4: "WR_2",
                5: "TE",
                6: "Flex (RB/WR/TE)",
                7: "K",
                8: "Defense (Team Name)",
                9: "Bench (RB/WR/TE)",
            },
            "Player": {
                0: "Josh Allen",
                1: "David Montgomery",
                2: "Tarik Cohen",
                3: "Allen Robinson",
                4: "Anthony Miller",
                5: "Dawson Knox",
                6: "Jared Cook",
                7: "Cairo Santos",
                8: "Chicago Bears",
                9: "Latavius Murray",
            },
            "Team": {
                0: "BUF",
                1: "CHI",
                2: "CHI",
                3: "CHI",
                4: "CHI",
                5: "BUF",
                6: "NO",
                7: "CHI",
                8: "CHI",
                9: "NO",
            },
        },
        "Becca": {
            "Position": {
                0: "QB",
                1: "RB_1",
                2: "RB_2",
                3: "WR_1",
                4: "WR_2",
                5: "TE",
                6: "Flex (RB/WR/TE)",
                7: "K",
                8: "Defense (Team Name)",
                9: "Bench (RB/WR/TE)",
            },
            "Player": {
                0: "Dak Prescott",
                1: "Adrian Peterson",
                2: "Kerryon Johnson",
                3: "Marvin Jones",
                4: "John Brown",
                5: "T.J. Hockenson",
                6: "Alvin Kamara",
                7: "Matt Prater",
                8: "Detroit Lions",
                9: "Michael Gallup",
            },
            "Team": {
                0: "DAL",
                1: "DET",
                2: "DET",
                3: "DET",
                4: "BUF",
                5: "DET",
                6: "NO",
                7: "DET",
                8: "DET",
                9: "DAL",
            },
        },
        "Logan": {
            "Position": {
                0: "QB",
                1: "RB_1",
                2: "RB_2",
                3: "WR_1",
                4: "WR_2",
                5: "TE",
                6: "Flex (RB/WR/TE)",
                7: "K",
                8: "Defense (Team Name)",
                9: "Bench (RB/WR/TE)",
            },
            "Player": {
                0: "Matt Ryan",
                1: "D'Andre Swift",
                2: "Devin Singletary",
                3: "Russell Gage",
                4: "Amari Cooper",
                5: "Jimmy Graham",
                6: "Michael Thomas",
                7: "Tyler Bass",
                8: "Dallas Cowboys",
                9: "Randall Cobb",
            },
            "Team": {
                0: "ATL",
                1: "DET",
                2: "BUF",
                3: "ATL",
                4: "DAL",
                5: "CHI",
                6: "NO",
                7: "BUF",
                8: "DAL",
                9: "DAL",
            },
        },
    }

    participant_teams = {k: pd.DataFrame(v) for k, v in participant_teams.items()}

    return participant_teams


def test_MockDraft(tmp_path, monkeypatch, mock_participant_teams):
    # Setup
    tmp_archive_path = tmp_path.joinpath("archive")
    tmp_archive_path.mkdir()

    tmp_archive_year_path = tmp_path.joinpath("2020")
    tmp_archive_year_path.mkdir()

    participant_teams = mock_participant_teams

    def mock_setup(self):
        self.output_dir = tmp_archive_year_path
        self.draft_order_path = tmp_archive_year_path.joinpath("2020_draft_order.json")
        self.draft_sheet_path = tmp_archive_year_path.joinpath("2020_draft_sheet.xlsx")

        mock_draft_order = {"dodd": 1, "becca": 2, "logan": 3}

        with open(tmp_archive_year_path.joinpath("2020_draft_order.json"), "w") as f:
            json.dump(mock_draft_order, f)

        with pd.ExcelWriter(
            tmp_archive_year_path.joinpath("2020_draft_sheet.xlsx")
        ) as writer:
            for participant, participant_team in participant_teams.items():
                participant_team.to_excel(
                    writer, sheet_name=participant.title(), index=False
                )

    monkeypatch.setattr("draft.Draft.setup", mock_setup)
    monkeypatch.setattr("scrape.Scraper.nfl_thanksgiving_calendar_week", 2)

    # Exercise
    d = main()

    # Verify
    # assert d.output_dir == tmp_archive_year_path
    # assert d.draft_order_path == tmp_archive_year_path.joinpath('2020_draft_order.json')
    # assert d.draft_sheet_path == tmp_archive_year_path.joinpath('2020_draft_sheet.xlsx')

    # assert d.draft_order_path.exists()

    # with open(d.draft_order_path, 'r') as f:
    #     written_draft_order = json.load(f)

    # assert written_draft_order == {'dodd': 1, 'becca': 2, 'logan': 3}

    # assert d.draft_sheet_path.exists()
    # written_draft_sheet = pd.read_excel(d.draft_sheet_path, sheet_name=None)
    # assert list(written_draft_sheet.keys()) == [*(map(str.title, written_draft_order.keys()))]

    # for participant, participant_team in written_draft_sheet.items():
    #     assert participant_team.equals(participant_teams[participant])
    # written_draft_sheet = pd.read_excel(tmp_archive_year_path.joinpath('2020_draft_sheet.xlsx'), sheet_name=None)

    # assert list(written_draft_sheet.keys()) == list(participant_teams.keys())

    # for participant, participant_team in d.items():
    #     assert participant_team.equals(written_draft_sheet[participant])

    # TODO: make a getter and setter for week (make your life easier in future)
    assert d.nfl_thanksgiving_calendar_week == 2
    # Cleanup - none necessary
