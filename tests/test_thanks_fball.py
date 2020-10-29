# Standard libraries
import json
from unittest import mock

# Third-party libraries
import numpy as np
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

    return participant_teams


@pytest.fixture
def mock_projected_player_pts_df():
    with open("assets/for_tests/mock_projected_player_pts.json", "r") as f:
        projected_player_pts = json.load(f)

    projected_player_pts_df = pd.DataFrame(projected_player_pts)

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


def test_MockDraft(
    tmp_path,
    monkeypatch,
    mock_participant_teams,
    mock_projected_player_pts_df,
    mock_actual_player_pts_df,
    mock_participant_teams_robust_sort,
    mock_leader_board_data,
):
    # Setup
    tmp_archive_path = tmp_path.joinpath("archive")
    tmp_archive_path.mkdir()

    tmp_archive_year_path = tmp_path.joinpath("2020")
    tmp_archive_year_path.mkdir()

    participant_teams = mock_participant_teams
    projected_player_pts_df = mock_projected_player_pts_df
    actual_player_pts_df = mock_actual_player_pts_df
    leader_board_data = mock_leader_board_data

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

        projected_player_pts_df.to_csv(
            tmp_archive_year_path.joinpath("2020_2_projected_player_pts.csv")
        )
        actual_player_pts_df.to_csv(
            tmp_archive_year_path.joinpath("2020_2_actual_player_pts.csv")
        )

    monkeypatch.setattr("draft.Draft.setup", mock_setup)
    monkeypatch.setattr(
        "scrape.Scraper.get_nfl_thanksgiving_calendar_week", lambda x: 2
    )
    monkeypatch.setattr(
        "scrape.Scraper.get_projected_player_pts",
        lambda x: {"999": {"projectedStats": {}}},
    )
    monkeypatch.setattr(
        "scrape.Scraper.get_actual_player_pts", lambda x: {"999": {"stats": {}}}
    )

    def mock_update_player_ids(self, projected_player_pts):
        return None

    monkeypatch.setattr("scrape.Scraper.update_player_ids", mock_update_player_ids)

    def mock_create_player_pts_df(year, week, player_pts, savepath):
        stats_type = aggregate._get_player_pts_stat_type(player_pts)

        if stats_type == "projectedStats":
            player_pts_df = pd.read_csv(
                tmp_archive_year_path.joinpath("2020_2_projected_player_pts.csv"),
                index_col=0,
            )

        if stats_type == "stats":
            player_pts_df = pd.read_csv(
                tmp_archive_year_path.joinpath("2020_2_actual_player_pts.csv"),
                index_col=0,
            )

        return player_pts_df

    monkeypatch.setattr("aggregate.create_player_pts_df", mock_create_player_pts_df)

    participant_teams_robust_sorted = mock_participant_teams_robust_sort

    def mock_write_robust_participant_team_scores(
        year, week, participant_teams, savepath
    ):
        savepath = tmp_archive_year_path.joinpath(
            "2020_2_robust_participant_player_pts.xlsx"
        )

        with pd.ExcelWriter(savepath) as writer:
            for participant, participant_team in participant_teams.items():

                # Write data to sheet
                participant_team.to_excel(writer, sheet_name=participant, index=False)

                # Auto-format column lengths and center columns
                worksheet = writer.sheets[participant]
                workbook = writer.book
                center = workbook.add_format()
                center.set_align("center")
                center.set_align("vcenter")

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

    monkeypatch.setattr(
        "aggregate.write_robust_participant_team_scores",
        mock_write_robust_participant_team_scores,
    )
    monkeypatch.setattr("leader_board.LeaderBoard.display", lambda x: None)

    def mock_LeaderBoard_save(self):
        with pd.ExcelWriter(
            tmp_archive_year_path.joinpath("2020_leader_board.xlsx")
        ) as writer:

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

    monkeypatch.setattr("leader_board.LeaderBoard.save", mock_LeaderBoard_save)

    # Exercise
    main()

    # d = main()
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

    # assert d.nfl_thanksgiving_calendar_week == 2

    # assert d == {'999': {'projectedStats': {}}}
    # assert d == {'999': {'stats': {}}}

    # assert d.equals(projected_player_pts_df)
    # assert d.equals(actual_player_pts_df)

    # assert list(d.keys()) == list(participant_teams_robust_sorted.keys())
    # for p, df in d.items():
    #     assert df.equals(participant_teams_robust_sorted[p])

    # assert tmp_archive_year_path.joinpath('2020_2_robust_participant_player_pts.xlsx').exists()

    assert tmp_archive_year_path.joinpath("2020_leader_board.xlsx").exists()
    written_leader_board = pd.read_excel(
        tmp_archive_year_path.joinpath("2020_leader_board.xlsx"), sheet_name=None
    )

    assert list(written_leader_board.keys()) == list(leader_board_data.keys())
    for p, df in written_leader_board.items():
        assert df.equals(leader_board_data[p])

    # Cleanup - none necessary


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


def test_MockDraft_no_actual_player_pts(
    tmp_path,
    monkeypatch,
    mock_participant_teams,
    mock_projected_player_pts_df,
    mock_participant_teams_robust_sort,
    mock_leader_board_data_no_actual,
):
    # Setup
    tmp_archive_path = tmp_path.joinpath("archive")
    tmp_archive_path.mkdir()

    tmp_archive_year_path = tmp_path.joinpath("2020")
    tmp_archive_year_path.mkdir()

    participant_teams = mock_participant_teams
    projected_player_pts_df = mock_projected_player_pts_df
    leader_board_data = mock_leader_board_data_no_actual

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

        projected_player_pts_df.to_csv(
            tmp_archive_year_path.joinpath("2020_2_projected_player_pts.csv")
        )

    monkeypatch.setattr("draft.Draft.setup", mock_setup)
    monkeypatch.setattr(
        "scrape.Scraper.get_nfl_thanksgiving_calendar_week", lambda x: 2
    )
    monkeypatch.setattr(
        "scrape.Scraper.get_projected_player_pts",
        lambda x: {"999": {"projectedStats": {}}},
    )
    monkeypatch.setattr("scrape.Scraper.get_actual_player_pts", lambda x: None)

    def mock_update_player_ids(self, projected_player_pts):
        return None

    monkeypatch.setattr("scrape.Scraper.update_player_ids", mock_update_player_ids)

    def mock_create_player_pts_df(year, week, player_pts, savepath):
        """Only PROJ as actual doesn't exist"""
        player_pts_df = pd.read_csv(
            tmp_archive_year_path.joinpath("2020_2_projected_player_pts.csv"),
            index_col=0,
        )

        return player_pts_df

    monkeypatch.setattr("aggregate.create_player_pts_df", mock_create_player_pts_df)

    participant_teams_robust_sorted = mock_participant_teams_robust_sort

    def mock_write_robust_participant_team_scores(
        year, week, participant_teams, savepath
    ):
        savepath = tmp_archive_year_path.joinpath(
            "2020_2_robust_participant_player_pts.xlsx"
        )

        with pd.ExcelWriter(savepath) as writer:
            for participant, participant_team in participant_teams.items():

                # Write data to sheet
                participant_team.to_excel(writer, sheet_name=participant, index=False)

                # Auto-format column lengths and center columns
                worksheet = writer.sheets[participant]
                workbook = writer.book
                center = workbook.add_format()
                center.set_align("center")
                center.set_align("vcenter")

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

    monkeypatch.setattr(
        "aggregate.write_robust_participant_team_scores",
        mock_write_robust_participant_team_scores,
    )
    monkeypatch.setattr("leader_board.LeaderBoard.display", lambda x: None)

    def mock_LeaderBoard_save(self):
        with pd.ExcelWriter(
            tmp_archive_year_path.joinpath("2020_leader_board.xlsx")
        ) as writer:

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

    monkeypatch.setattr("leader_board.LeaderBoard.save", mock_LeaderBoard_save)

    # Exercise
    # main()

    main()
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

    # assert d.nfl_thanksgiving_calendar_week == 2

    # assert d == {'999': {'projectedStats': {}}}
    # assert d == {'999': {'stats': {}}}

    # assert d.equals(projected_player_pts_df)
    # assert d.equals(actual_player_pts_df)

    # assert list(d.keys()) == list(participant_teams_robust_sorted.keys())
    # for p, df in d.items():
    #     assert df.equals(participant_teams_robust_sorted[p])

    # assert tmp_archive_year_path.joinpath('2020_2_robust_participant_player_pts.xlsx').exists()

    # expected = projected_player_pts_df[['Player', 'Team']].copy()
    # expected['ACTUAL_pts'] = 0.0
    # assert d.equals(expected)

    assert tmp_archive_year_path.joinpath("2020_leader_board.xlsx").exists()
    written_leader_board = pd.read_excel(
        tmp_archive_year_path.joinpath("2020_leader_board.xlsx"), sheet_name=None
    )

    assert list(written_leader_board.keys()) == list(leader_board_data.keys())
    for p, df in written_leader_board.items():
        assert df.equals(leader_board_data[p])

    # Cleanup - none necessary


def test_main():
    """
    https://medium.com/opsops/how-to-test-if-name-main-1928367290cb
    """
    # Local libraries
    import thanks_fball

    with mock.patch.object(thanks_fball, "main", return_value=42):
        with mock.patch.object(thanks_fball, "__name__", "__main__"):
            assert thanks_fball.main() == 42
