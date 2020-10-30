# Standard libraries
import json
import random

# Third-party libraries
import pandas as pd
import pytest

# Local libraries
import aggregate
from thanks_fball import main


@pytest.fixture
def mock_participant_teams():
    with open("assets/for_tests/mock_participant_teams.json", "r") as f:
        participant_teams = json.load(f)

    participant_teams = {k: pd.DataFrame(v) for k, v in participant_teams.items()}

    # Ensure indexes are equivalent to pandas DataFrame style RangeIndex
    # use pandas.util.testing.assert_frame_equal for detailed diffs
    for p, df in participant_teams.items():
        participant_teams[p].index = range(0, 10)

    return participant_teams


@pytest.fixture
def mock_projected_player_pts_df():
    with open("assets/for_tests/mock_projected_player_pts.json", "r") as f:
        projected_player_pts = json.load(f)

    projected_player_pts_df = pd.DataFrame(projected_player_pts)

    # Ensure indexes are equivalent to pandas DataFrame style RangeIndex
    # use pandas.util.testing.assert_frame_equal for detailed diffs
    projected_player_pts_df.index = range(0, 30)

    return projected_player_pts_df


@pytest.fixture
def mock_actual_player_pts_df():
    with open("assets/for_tests/mock_actual_player_pts.json", "r") as f:
        actual_player_pts = json.load(f)

    actual_player_pts_df = pd.DataFrame(actual_player_pts)

    return actual_player_pts_df


@pytest.fixture
def mock_participant_teams_robust_sort():
    with open("assets/for_tests/mock_robust_participant_player_pts.json", "r") as f:
        participant_teams = json.load(f)

    participant_teams = {k: pd.DataFrame(v) for k, v in participant_teams.items()}

    # Ensure indexes are equivalent to pandas DataFrame style RangeIndex
    # use pandas.util.testing.assert_frame_equal for detailed diffs
    for p, df in participant_teams.items():
        participant_teams[p].index = range(0, 10)

    return participant_teams


@pytest.fixture
def mock_leader_board_data():
    with open("assets/for_tests/mock_leader_board.json", "r") as f:
        total_board_data = json.load(f)

    total_board_data = {k: pd.DataFrame(v) for k, v in total_board_data.items()}

    # Ensure indexes are equivalent to pandas DataFrame style RangeIndex
    # use pandas.util.testing.assert_frame_equal for detailed diffs
    for k, df in total_board_data.items():
        if k == "Leader Board":
            df.index = range(0, 3)
        else:
            df.index = range(0, 10)
        total_board_data[k] = df

    return total_board_data


@pytest.fixture
def mock_leader_board_data_no_actual():
    with open("assets/for_tests/mock_leader_board_no_actual_pts.json", "r") as f:
        total_board_data = json.load(f)

    total_board_data = {k: pd.DataFrame(v) for k, v in total_board_data.items()}

    # Ensure indexes are equivalent to pandas DataFrame style RangeIndex
    # use pandas.util.testing.assert_frame_equal for detailed diffs
    for k, df in total_board_data.items():
        if k == "Leader Board":
            df.index = range(0, 3)
        else:
            df.index = range(0, 10)
        total_board_data[k] = df

    return total_board_data


@pytest.mark.freeze_time
def test_MockDraft_projected_exists_not_all_players_drafted(
    freezer, tmp_path, monkeypatch, mock_projected_player_pts_df, capsys
):
    # Setup
    freezer.move_to("2005-01-01")

    tmp_archive_path = tmp_path.joinpath("archive")
    tmp_archive_path.mkdir()

    tmp_archive_year_path = tmp_path.joinpath("2005")
    tmp_archive_year_path.mkdir()

    # Mock Draft.__init__ so data saved to tmp_path
    def mock_init(self, year):
        self.year = year
        self.output_dir = tmp_archive_year_path
        self.draft_order_path = tmp_archive_year_path.joinpath("2005_draft_order.json")
        self.draft_sheet_path = tmp_archive_year_path.joinpath("2005_draft_sheet.xlsx")

    monkeypatch.setattr("draft.Draft.__init__", mock_init)

    # Override input() func to always return same list of participants
    monkeypatch.setattr("builtins.input", lambda _: "logan, becca, dodd")

    # Set random seed for draft order consistency in testing
    random.seed(42)

    # Write projected_player_pts_df to tmp_path so it appears to exist
    projected_player_pts_df = mock_projected_player_pts_df
    projected_player_pts_df.to_csv(
        tmp_archive_year_path.joinpath("2005_12_projected_player_pts.csv")
    )

    # Exercise (wrap since main will exist in this case)
    with pytest.raises(SystemExit) as e:
        main()

    # Verify
    assert e.type == SystemExit
    assert e.value.code is None
    assert pd.options.display.width is None
    assert tmp_archive_year_path.joinpath("2005_draft_order.json").exists()
    assert tmp_archive_year_path.joinpath("2005_draft_sheet.xlsx").exists()

    captured = capsys.readouterr()
    assert captured.out == (
        "\n----- 2005 Turkey Bowl -----\n"
        + "\n\tDraft Order: ['dodd', 'logan', 'becca']\n"
        + f"\tSaved draft order to {tmp_archive_year_path.joinpath('2005_draft_order.json')}\n"
        + f"\nProjected player data already exists at {tmp_archive_year_path.joinpath('2005_12_projected_player_pts.csv')}\n"
        + "\nNot all players have been drafted yet! Please complete the draft for 2005.\n"
    )

    # Cleanup - none necessary


@pytest.mark.freeze_time
def test_MockDraft_projected_dont_exists_not_all_players_drafted(
    freezer, tmp_path, monkeypatch, mock_projected_player_pts_df, capsys
):
    # Setup
    freezer.move_to("2005-01-01")

    tmp_archive_path = tmp_path.joinpath("archive")
    tmp_archive_path.mkdir()

    tmp_archive_year_path = tmp_path.joinpath("2005")
    tmp_archive_year_path.mkdir()

    # Mock Draft.__init__ so data saved to tmp_path
    def mock_init(self, year):
        self.year = year
        self.output_dir = tmp_archive_year_path
        self.draft_order_path = tmp_archive_year_path.joinpath("2005_draft_order.json")
        self.draft_sheet_path = tmp_archive_year_path.joinpath("2005_draft_sheet.xlsx")

    monkeypatch.setattr("draft.Draft.__init__", mock_init)

    # Override input() func to always return same list of participants
    monkeypatch.setattr("builtins.input", lambda _: "logan, becca, dodd")

    # Set random seed for draft order consistency in testing
    random.seed(42)

    # Mock scraper methods so no requests call
    def mock_get_projected_player_pts(self):
        print("\nCollecting projected player points...")
        print(
            "\tSuccessful API response obtained for: https://api.fantasy.nfl.com/v2/players/weekprojectedstats?season=2005&week=12"
        )

    monkeypatch.setattr(
        "scrape.Scraper.get_projected_player_pts", mock_get_projected_player_pts
    )

    def mock_update_player_ids(self, projected_player_pts):
        print("\tPlayer ids are up to date at player_ids.json")

    monkeypatch.setattr("scrape.Scraper.update_player_ids", mock_update_player_ids)

    # Mock aggregate.create_players_pts_df to return testing dataframe asset
    def mock_create_player_pts_df(year, week, player_pts, savepath):
        print(
            f"\tWriting projected player stats to {tmp_archive_year_path.joinpath('2005_12_projected_player_pts.csv')}"
        )
        projected_player_pts_df = mock_projected_player_pts_df
        return projected_player_pts_df

    monkeypatch.setattr("aggregate.create_player_pts_df", mock_create_player_pts_df)

    # Ensure projected doesn't exist
    assert not tmp_archive_year_path.joinpath(
        "2005_12_projected_player_pts.csv"
    ).exists()

    # Exercise (wrap since main will exist in this case)
    with pytest.raises(SystemExit) as e:
        main()

    # Verify
    assert e.type == SystemExit
    assert e.value.code is None
    assert pd.options.display.width is None
    assert tmp_archive_year_path.joinpath("2005_draft_order.json").exists()
    assert tmp_archive_year_path.joinpath("2005_draft_sheet.xlsx").exists()

    captured = capsys.readouterr()
    assert captured.out == (
        "\n----- 2005 Turkey Bowl -----\n"
        + "\n\tDraft Order: ['dodd', 'logan', 'becca']\n"
        + f"\tSaved draft order to {tmp_archive_year_path.joinpath('2005_draft_order.json')}\n"
        + "\nCollecting projected player points...\n"
        + "\tSuccessful API response obtained for: https://api.fantasy.nfl.com/v2/players/weekprojectedstats?season=2005&week=12\n"
        + "\tPlayer ids are up to date at player_ids.json\n"
        + f"\tWriting projected player stats to {tmp_archive_year_path.joinpath('2005_12_projected_player_pts.csv')}\n"
        + "\nNot all players have been drafted yet! Please complete the draft for 2005.\n"
    )

    # Cleanup - none necessary


@pytest.mark.freeze_time
@pytest.mark.parametrize("actual_pts_exist", [True, False])
def test_MockDraft(
    freezer,
    tmp_path,
    monkeypatch,
    mock_participant_teams,
    mock_projected_player_pts_df,
    mock_actual_player_pts_df,
    mock_participant_teams_robust_sort,
    mock_leader_board_data,
    mock_leader_board_data_no_actual,
    actual_pts_exist,
):
    # Setup
    freezer.move_to("2005-01-01")

    tmp_archive_path = tmp_path.joinpath("archive")
    tmp_archive_path.mkdir()

    tmp_archive_year_path = tmp_path.joinpath("2005")
    tmp_archive_year_path.mkdir()

    participant_teams = mock_participant_teams
    projected_player_pts_df = mock_projected_player_pts_df
    actual_player_pts_df = mock_actual_player_pts_df
    participant_teams_robust_sorted = mock_participant_teams_robust_sort

    if actual_pts_exist:
        leader_board_data = mock_leader_board_data
    else:
        leader_board_data = mock_leader_board_data_no_actual

    mock_draft_order = {"dodd": 1, "becca": 2, "logan": 3}

    with open(tmp_archive_year_path.joinpath("2005_draft_order.json"), "w") as f:
        json.dump(mock_draft_order, f)

    with pd.ExcelWriter(
        tmp_archive_year_path.joinpath("2005_draft_sheet.xlsx")
    ) as writer:
        for participant, participant_team in participant_teams.items():
            participant_team.to_excel(
                writer, sheet_name=participant.title(), index=False
            )

    projected_player_pts_df.to_csv(
        tmp_archive_year_path.joinpath("2005_12_projected_player_pts.csv")
    )
    actual_player_pts_df.to_csv(
        tmp_archive_year_path.joinpath("2005_12_actual_player_pts.csv")
    )

    # Mock Draft.__init__ so data saved to tmp_path
    def mock_init(self, year):
        self.year = year
        self.output_dir = tmp_archive_year_path
        self.draft_order_path = tmp_archive_year_path.joinpath("2005_draft_order.json")
        self.draft_sheet_path = tmp_archive_year_path.joinpath("2005_draft_sheet.xlsx")

    monkeypatch.setattr("draft.Draft.__init__", mock_init)

    # Mock scraper methods so no requests call
    # monkeypatch.setattr(
    #     "scrape.Scraper.get_projected_player_pts",
    #     lambda x: {"999": {"projectedStats": {}}},
    # )

    if actual_pts_exist:
        monkeypatch.setattr(
            "scrape.Scraper.get_actual_player_pts", lambda x: {"999": {"stats": {}}}
        )
    else:
        monkeypatch.setattr("scrape.Scraper.get_actual_player_pts", lambda _: None)

    # def mock_update_player_ids(self, projected_player_pts):
    #     return None

    # monkeypatch.setattr("scrape.Scraper.update_player_ids", mock_update_player_ids)

    # Mock aggregate.create_players_pts_df to return testing dataframe asset
    def mock_create_player_pts_df(year, week, player_pts, savepath):
        stats_type = aggregate._get_player_pts_stat_type(player_pts)

        # if stats_type == "projectedStats":
        #     player_pts_df = pd.read_csv(
        #         tmp_archive_year_path.joinpath("2005_12_projected_player_pts.csv"),
        #         index_col=0,
        #     )

        if stats_type == "stats":
            player_pts_df = pd.read_csv(
                tmp_archive_year_path.joinpath("2005_12_actual_player_pts.csv"),
                index_col=0,
            )

        return player_pts_df

    monkeypatch.setattr("aggregate.create_player_pts_df", mock_create_player_pts_df)

    # Exercise
    main()

    # Verify pandas display
    assert pd.options.display.width is None

    # Verify draft order
    assert tmp_archive_year_path.joinpath("2005_draft_order.json").exists()
    with open(tmp_archive_year_path.joinpath("2005_draft_order.json"), "r") as f:
        written_draft_order = json.load(f)
    assert written_draft_order == mock_draft_order

    # Verify draft sheet
    assert tmp_archive_year_path.joinpath("2005_draft_sheet.xlsx").exists()
    written_participant_teams = pd.read_excel(
        tmp_archive_year_path.joinpath("2005_draft_sheet.xlsx"), sheet_name=None
    )
    assert list(written_participant_teams.keys()) == list(participant_teams)
    for p, df in written_participant_teams.items():
        assert df.equals(participant_teams[p])

    # Verify projected player points
    assert tmp_archive_year_path.joinpath("2005_12_projected_player_pts.csv").exists()
    written_projected_player_pts = pd.read_csv(
        tmp_archive_year_path.joinpath("2005_12_projected_player_pts.csv"), index_col=0
    )
    assert written_projected_player_pts.equals(projected_player_pts_df)

    # Verify robust participant player points
    assert tmp_archive_year_path.joinpath(
        "2005_12_robust_participant_player_pts.xlsx"
    ).exists()
    written_robust_participant_player_pts = pd.read_excel(
        tmp_archive_year_path.joinpath("2005_12_robust_participant_player_pts.xlsx"),
        sheet_name=None,
    )
    for p, df in written_robust_participant_player_pts.items():
        col_types = {}
        for c in df.columns:
            if c in ("Player", "Team", "Position"):
                col_types[c] = "object"
            else:
                col_types[c] = "float64"

        df = df.astype(col_types)
        participant_teams_robust_sorted[p] = participant_teams_robust_sorted[p].astype(
            col_types
        )

        if not actual_pts_exist:
            drop_cols = [c for c in participant_teams_robust_sorted[p] if "ACTUAL" in c]

            participant_teams_robust_sorted[p] = participant_teams_robust_sorted[
                p
            ].drop(drop_cols, axis=1)

            participant_teams_robust_sorted[p].insert(3, "ACTUAL_pts", 0.0)

        assert df.equals(participant_teams_robust_sorted[p])

    # Verify Leader Board
    assert tmp_archive_year_path.joinpath("2005_leader_board.xlsx").exists()
    written_leader_board = pd.read_excel(
        tmp_archive_year_path.joinpath("2005_leader_board.xlsx"), sheet_name=None
    )

    assert list(written_leader_board.keys()) == list(leader_board_data.keys())

    for p, df in written_leader_board.items():
        assert df.equals(leader_board_data[p])

    # Cleanup - none necessary
