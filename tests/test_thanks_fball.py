# import pytest
# import utils
# from draft import Draft
# from thanks_fball import main
# from pathlib import Path
# import mock

# import functools


def mock_setup(self):
    self.output_dir = "tmp_archive_year_path"
    # cls.draft_order_path = tmp_archive_year_path.joinpath('2020_draft_order.json')
    # cls.draft_sheet_path = tmp_archive_year_path.joinpath('2020_draft_sheet.xlsx')


def test_MockDraft(tmp_path):
    tmp_archive_path = tmp_path.joinpath("archive")
    tmp_archive_path.mkdir()

    tmp_archive_year_path = tmp_path.joinpath("2020")
    tmp_archive_year_path.mkdir()

    assert tmp_archive_year_path == ""
    # with mock.patch.object(Draft, 'setup', new=mock_setup):
    #     d = main()
    # assert d.output_dir == 'testing'
