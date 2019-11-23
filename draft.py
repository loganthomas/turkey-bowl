"""
Draft functions
"""
# Standard libraries
import random
import shutil

# Third-party libraries
import pandas as pd


def copy_draft_sheet(year, output_dir):
    """
    Creates a new blank draft sheet within output_dir
    """
    draft_file_name = f'draft_sheet_{year}.xlsx'
    draft_file_path = output_dir.joinpath(draft_file_name)

    shutil.copyfile('draft_sheet.xlsx', draft_file_path)

    return draft_file_path


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
    participant_teams = {p:xlsx.parse(p) for p in xlsx.sheet_names}

    return participant_teams


def make_draft_order(participant_teams):
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
    # Gather list of participants
    draft_order = list(participant_teams.keys())

    # Create random list of participants
    random.shuffle(draft_order)

    return draft_order


