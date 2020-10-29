"""
Unit tests for draft.py
"""
# Standard libraries
import json
import random

# Third-party libraries
import pandas as pd

# Local libraries
from draft import Draft


def test_Draft_instantiation():
    # Setup - none necessary

    # Exercise
    draft = Draft(2020)

    # Verify
    assert draft.year == 2020
    assert draft.output_dir.as_posix() == "archive/2020"
    assert draft.draft_order_path.as_posix() == "archive/2020/2020_draft_order.json"
    assert draft.draft_sheet_path.as_posix() == "archive/2020/2020_draft_sheet.xlsx"

    assert draft.__repr__() == "Draft(2020)"
    assert draft.__str__() == "Turkey Bowl Draft: 2020"

    # Cleanup - none necessary


def test_Draft_setup_nothing_exists(tmp_path, monkeypatch, capsys):
    """ Test Draft.setup() when no directories exist in root. """
    # Setup - create temp archive dir (assumed to always exist)
    tmp_archive_dir = tmp_path.joinpath("archive")
    tmp_archive_dir.mkdir()

    # Ensure nothing exists prior to Draft.setup() call
    assert tmp_archive_dir.joinpath("2020").exists() is False
    assert tmp_archive_dir.joinpath("2020/2020_draft_order.json").exists() is False
    assert tmp_archive_dir.joinpath("2020/2020_draft_sheet.xlsx").exists() is False

    # Exercise
    draft = Draft(2020)

    # Override input() func to always return same list of participants
    monkeypatch.setattr("builtins.input", lambda _: "logan, becca, dodd")

    # Override output dirs to temp path created for testing
    draft.output_dir = tmp_archive_dir.joinpath("2020")
    draft.draft_order_path = tmp_archive_dir.joinpath("2020/2020_draft_order.json")
    draft.draft_sheet_path = tmp_archive_dir.joinpath("2020/2020_draft_sheet.xlsx")

    # Set random seed for draft order consistency in testing
    random.seed(42)
    draft.setup()

    # Verify
    assert draft.year == 2020
    assert draft.output_dir == tmp_archive_dir.joinpath("2020")
    assert draft.draft_order_path == tmp_archive_dir.joinpath(
        "2020/2020_draft_order.json"
    )
    assert draft.draft_sheet_path == tmp_archive_dir.joinpath(
        "2020/2020_draft_sheet.xlsx"
    )

    assert tmp_archive_dir.joinpath("2020").exists() is True
    assert tmp_archive_dir.joinpath("2020/2020_draft_order.json").exists() is True
    assert tmp_archive_dir.joinpath("2020/2020_draft_sheet.xlsx").exists() is True

    assert draft.participant_list == ["logan", "becca", "dodd"]
    assert draft.draft_order == ["dodd", "logan", "becca"]

    with open(
        tmp_archive_dir.joinpath("2020/2020_draft_order.json"), "r"
    ) as written_json:
        loaded_json = json.load(written_json)

    assert list(loaded_json.keys()) == ["dodd", "logan", "becca"]

    draft_sheet_data = pd.read_excel(
        tmp_archive_dir.joinpath("2020/2020_draft_sheet.xlsx"),
        sheet_name=None,
        engine="xlrd",
    )

    assert list(draft_sheet_data) == ["Dodd", "Logan", "Becca"]

    for participant_draft_info in draft_sheet_data.values():
        assert list(participant_draft_info.columns) == ["Position", "Player", "Team"]
        assert participant_draft_info["Position"].equals(
            pd.Series(
                [
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
                ]
            )
        )

    captured = capsys.readouterr()
    assert captured.out == (
        "\n\tDraft Order: ['dodd', 'logan', 'becca']\n"
        + f"\tSaved draft order to {tmp_archive_dir.joinpath('2020/2020_draft_order.json')}\n"
    )
    # Cleanup - none necessary


def test_Draft_setup_already_exists(tmp_path, capsys):
    """ Test Draft.setup() when files exist in root. """
    # Setup
    tmp_archive_dir = tmp_path.joinpath("archive")
    tmp_archive_dir.mkdir()

    tmp_year_dir = tmp_archive_dir.joinpath("2020")
    tmp_year_dir.mkdir()

    existing_draft_order = ["yeager", "emily", "dodd", "logan", "becca_hud", "cindy"]
    existing_draft_order_dict = {
        "yeager": 1,
        "emily": 2,
        "dodd": 3,
        "logan": 4,
        "becca_hud": 5,
        "cindy": 6,
    }

    with open(tmp_year_dir.joinpath("2020_draft_order.json"), "w") as written_json:
        json.dump(existing_draft_order_dict, written_json)

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
        "Player": [" "] * 10,
        "Team": [" "] * 10,
    }
    draft_df = pd.DataFrame(draft_info)

    with pd.ExcelWriter(tmp_year_dir.joinpath("2020_draft_sheet.xlsx")) as writer:
        for participant in existing_draft_order:
            draft_df.to_excel(writer, sheet_name=participant.title(), index=False)

    # Ensure everything exists prior to Draft.setup() call
    assert tmp_archive_dir.joinpath("2020").exists() is True
    assert tmp_archive_dir.joinpath("2020/2020_draft_order.json").exists() is True
    assert tmp_archive_dir.joinpath("2020/2020_draft_sheet.xlsx").exists() is True

    # Exercise
    draft = Draft(2020)

    # Override output dirs to temp path crated for testing
    draft.output_dir = tmp_archive_dir.joinpath("2020")
    draft.draft_order_path = tmp_archive_dir.joinpath("2020/2020_draft_order.json")
    draft.draft_sheet_path = tmp_archive_dir.joinpath("2020/2020_draft_sheet.xlsx")

    draft.setup()

    # Verify
    assert draft.year == 2020
    assert draft.output_dir == tmp_archive_dir.joinpath("2020")

    assert draft.__repr__() == "Draft(2020)"
    assert draft.__str__() == "Turkey Bowl Draft: 2020"

    assert draft.draft_order_path == tmp_archive_dir.joinpath(
        "2020/2020_draft_order.json"
    )
    assert draft.draft_sheet_path == tmp_archive_dir.joinpath(
        "2020/2020_draft_sheet.xlsx"
    )

    assert tmp_archive_dir.joinpath("2020").exists() is True
    assert tmp_archive_dir.joinpath("2020/2020_draft_order.json").exists() is True
    assert tmp_archive_dir.joinpath("2020/2020_draft_sheet.xlsx").exists() is True

    assert draft.participant_list == existing_draft_order
    assert draft.draft_order == existing_draft_order

    captured = capsys.readouterr()
    assert captured.out == (
        f"\nDraft order already exists at {tmp_archive_dir.joinpath('2020/2020_draft_order.json')}\n"
        + f"\n\tDraft Order: {existing_draft_order}\n"
    )

    # Cleanup - none necessary


def test_Draft_load(tmp_path):
    # Setup
    tmp_archive_dir = tmp_path.joinpath("archive")
    tmp_archive_dir.mkdir()

    tmp_year_dir = tmp_archive_dir.joinpath("2005")
    tmp_year_dir.mkdir()

    existing_draft_order = ["yeager", "emily", "dodd", "logan", "becca_hud", "cindy"]
    existing_draft_order_dict = {
        "yeager": 1,
        "emily": 2,
        "dodd": 3,
        "logan": 4,
        "becca_hud": 5,
        "cindy": 6,
    }

    with open(tmp_year_dir.joinpath("2005_draft_order.json"), "w") as written_json:
        json.dump(existing_draft_order_dict, written_json)

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
        "Player": ["test"] * 10,
        "Team": ["test"] * 10,
    }
    draft_df = pd.DataFrame(draft_info)

    with pd.ExcelWriter(tmp_year_dir.joinpath("2005_draft_sheet.xlsx")) as writer:
        for participant in existing_draft_order:
            draft_df.to_excel(writer, sheet_name=participant.title(), index=False)

    # Ensure everything exists prior to Draft.setup() call
    assert tmp_archive_dir.joinpath("2005").exists() is True
    assert tmp_archive_dir.joinpath("2005/2005_draft_order.json").exists() is True
    assert tmp_archive_dir.joinpath("2005/2005_draft_sheet.xlsx").exists() is True

    # Exercise
    draft = Draft(2005)

    # Override output dirs to temp path crated for testing
    draft.output_dir = tmp_archive_dir.joinpath("2005")
    draft.draft_order_path = tmp_archive_dir.joinpath("2005/2005_draft_order.json")
    draft.draft_sheet_path = tmp_archive_dir.joinpath("2005/2005_draft_sheet.xlsx")

    draft.setup()
    result = draft.load()

    # Verify
    assert list(result.keys()) == [
        "Yeager",
        "Emily",
        "Dodd",
        "Logan",
        "Becca_Hud",
        "Cindy",
    ]

    assert draft.year == 2005
    assert draft.output_dir == tmp_archive_dir.joinpath("2005")

    assert draft.__repr__() == "Draft(2005)"
    assert draft.__str__() == "Turkey Bowl Draft: 2005"

    assert draft.draft_order_path == tmp_archive_dir.joinpath(
        "2005/2005_draft_order.json"
    )
    assert draft.draft_sheet_path == tmp_archive_dir.joinpath(
        "2005/2005_draft_sheet.xlsx"
    )

    assert tmp_archive_dir.joinpath("2005").exists() is True
    assert tmp_archive_dir.joinpath("2005/2005_draft_order.json").exists() is True
    assert tmp_archive_dir.joinpath("2005/2005_draft_sheet.xlsx").exists() is True

    assert draft.participant_list == existing_draft_order
    assert draft.draft_order == existing_draft_order

    # Cleanup - none necessary


def test_Draft_load_stripping_whitespace(tmp_path):
    # Setup
    expected_players = [
        "QB with spaces",
        "RB_1 with spaces",
        "RB_2 with spaces",
        "WR_1",
        "WR_2",
        "TE",
        "Luke Weyman Thomas",
        "Logan Thomas",
        "Chicago Bears",
        "Hudson Thomas",
    ]

    expected_teams = [
        "MIA",
        "DAL",
        "CHI",
        "NE",
        "HOU",
        "GB",
        "PIT",
        "Logan Thomas",
        "Chicago Bears",
        "Hudson Thomas",
    ]

    tmp_archive_dir = tmp_path.joinpath("archive")
    tmp_archive_dir.mkdir()

    tmp_year_dir = tmp_archive_dir.joinpath("2005")
    tmp_year_dir.mkdir()

    existing_draft_order = ["yeager", "emily", "dodd", "logan", "becca_hud", "cindy"]
    existing_draft_order_dict = {
        "yeager": 1,
        "emily": 2,
        "dodd": 3,
        "logan": 4,
        "becca_hud": 5,
        "cindy": 6,
    }

    with open(tmp_year_dir.joinpath("2005_draft_order.json"), "w") as written_json:
        json.dump(existing_draft_order_dict, written_json)

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
        "Player": [
            "   QB with spaces    ",
            " RB_1 with spaces ",
            "RB_2 with spaces ",
            "WR_1           ",
            "           WR_2",
            "TE         ",
            " Luke Weyman Thomas ",
            "  Logan Thomas    ",
            "    Chicago Bears   ",
            " Hudson Thomas       ",
        ],
        "Team": [
            "   MIA    ",
            " DAL ",
            "CHI ",
            "NE           ",
            "           HOU",
            "GB         ",
            " PIT ",
            "  Logan Thomas    ",
            "    Chicago Bears   ",
            " Hudson Thomas       ",
        ],
    }
    draft_df = pd.DataFrame(draft_info)

    with pd.ExcelWriter(tmp_year_dir.joinpath("2005_draft_sheet.xlsx")) as writer:
        for participant in existing_draft_order:
            draft_df.to_excel(writer, sheet_name=participant.title(), index=False)

    # Exercise
    draft = Draft(2005)

    # Override output dirs to temp path crated for testing
    draft.output_dir = tmp_archive_dir.joinpath("2005")
    draft.draft_order_path = tmp_archive_dir.joinpath("2005/2005_draft_order.json")
    draft.draft_sheet_path = tmp_archive_dir.joinpath("2005/2005_draft_sheet.xlsx")

    draft.setup()
    result = draft.load()

    # Verify
    assert list(result.keys()) == [
        "Yeager",
        "Emily",
        "Dodd",
        "Logan",
        "Becca_Hud",
        "Cindy",
    ]

    for participant, participant_team in result.items():
        assert participant_team["Player"].tolist() == expected_players
        assert participant_team["Team"].tolist() == expected_teams


def test_Draft_check_players_have_been_drafted_false():
    # Setup
    mock_player_data = {"Player": ["", "", ""]}
    mock_participant_teams = {
        "Logan": pd.DataFrame(mock_player_data),
        "Dodd": pd.DataFrame(mock_player_data),
        "Becca": pd.DataFrame(mock_player_data),
    }

    # Exercise
    draft = Draft(2020)
    result = draft.check_players_have_been_drafted(mock_participant_teams)

    # Verify
    assert result is False

    # Cleanup - none necessary


def test_Draft_check_players_have_been_drafted_true():
    # Setup
    mock_player_data = {"Player": ["Matt Ryan", "Tom Brady", "Trogdor"]}
    mock_participant_teams = {
        "Logan": pd.DataFrame(mock_player_data),
        "Dodd": pd.DataFrame(mock_player_data),
        "Becca": pd.DataFrame(mock_player_data),
    }

    # Exercise
    draft = Draft(2020)
    result = draft.check_players_have_been_drafted(mock_participant_teams)

    # Verify
    assert result is True

    # Cleanup - none necessary
