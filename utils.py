"""
Utility functions
"""
# Standard libraries
import calendar
from pathlib import Path
from datetime import datetime

# Third party libraries
import numpy as np
import pandas as pd


def get_current_year():
    return datetime.now().year


def get_nfl_start_week(curr_year):
    # Set Sunday as first day of week
    calendar.setfirstweekday(calendar.SUNDAY)

    # Gather sept days
    sept = calendar.monthcalendar(curr_year,9)
    sept = np.array(sept)

    # Get all sept mondays
    sept_mondays = sept[:,1]

    # Find first mondays date
    sept_first_monday = min([mon for mon in sept_mondays if mon != 0])

    # Convert to first monday in sept to datetime object
    sept_first_monday_date = datetime(curr_year,9, sept_first_monday)

    # Find calendar week for start of NFL season
    nfl_start_cal_week_num = sept_first_monday_date.isocalendar()[1]

    return nfl_start_cal_week_num


def get_thanksgiving_week(curr_year):
    # Set Sunday as first day of week
    calendar.setfirstweekday(calendar.SUNDAY)

    # Gather nov days
    nov = calendar.monthcalendar(curr_year,11)
    nov = np.array(nov)

    # Find 4th thursday in nov
    nov_thursdays = nov[:,4]
    thanksgiving_day = [thur for thur in nov_thursdays if thur != 0][3]

    # Convert thanksgiving day to datetime object
    thanksgiving_day_date = datetime(curr_year,11,thanksgiving_day)

    # Find calendar week for thanksgiving day
    thanksgiving_cal_week_num = thanksgiving_day_date.isocalendar()[1]

    return thanksgiving_cal_week_num


def calculate_nfl_thanksgiving_week(nfl_start_cal_week_num, thanksgiving_cal_week_num):
    # Find delta between NFL week 1 and Thanksgiving Week
    delta = thanksgiving_cal_week_num - nfl_start_cal_week_num

    # Add one since indexed at 1
    pull_week = delta + 1

    return pull_week


def create_output_dir(curr_year):
    """
    Creates a root directory to house yearly output.
    Directory name is year the script is run.
    """
    # Create a Path object to dir named curr_year
    output_dir = Path(curr_year)

    # Check if dir exists, if not create
    if not output_dir.is_dir():
        output_dir.mkdir()

    return output_dir


def merge_points(participant_teams, players_df):
    """
    Notes:
        Although the 'Bench (RB/WR)' player is reported in the
        player_stats DF, it is not used to calculate the total points for a
        given participant. It is assumed that the 'Bench (RB/WR)' player
        is listed last in the excel spreadsheet.
    """
    for participant, participant_team in participant_teams.items():
        merged = pd.merge(
            participant_team,
            players_df,
            left_on=['Player', 'Team'],
            right_on=['name', 'team'],
            how='left',
        )

        merged = merged.drop(['name', 'team',], axis=1)
        participant_teams[participant] = merged

        # Defensive programming (ignore bench player in case written in as NONE in .xlsx)
        if sum(pd.isna(merged[:-1]['id'])) > 0:
            print(f"WARNING!! {participant}'s merge has missing player ids")

    return participant_teams


def create_leader_board(year, output_dir, participant_teams):
    """
    Notes: Bench player assumed last row in excel sheet.
    Left out of calculation but still shown.
    """
    # Instantiate writer to save leader board and data
    writer = pd.ExcelWriter(output_dir.joinpath(f'{year}_leader_board.xlsx'), engine='xlsxwriter')

    # Instantiate leader board data
    leader_board_data = {}

    for participant, participant_team in participant_teams.items():
        print(f'\n### {participant.upper()} stats ###\n')
        print(participant_team)
        print('\n\n\n')

        # Assumes bench is last row (shown but not included in sum)
        team_pts = participant_team[:-1]['act_pts'].sum()

        leader_board_data[participant] = team_pts

        # Save to sheet in excel
        participant_team.to_excel(writer, sheet_name=participant)

    # Create a DataFrame from point_totals
    leader_board = pd.DataFrame.from_dict(leader_board_data, orient='index', columns=['PTS'])

    # Sort the leader board on highest pts to lowest pts
    leader_board = leader_board.sort_values('PTS', ascending=False)

    # Create column to show how far ahead each participant is compared to next
    leader_board['margin'] = leader_board['PTS'].diff(-1)

    # Create column to show how far out of lead they are
    leader_board['pts_back'] = leader_board.iloc[0,0] - leader_board['PTS'].values

    # Print details on points
    print(f'\n{leader_board.index[0]} winning with {round(leader_board.iloc[0,0],2)} pts\n')
    print(leader_board)
    print('\n')

    # Save leader board as sheet in excel
    leader_board.to_excel(writer, sheet_name='leader_board')
    writer.save()

