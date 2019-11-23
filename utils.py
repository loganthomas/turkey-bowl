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


def create_players_df(players):
    """
    Converts players (list of namedtuples) into pd.DataFrame
    """
    return pd.DataFrame(players)


def save_players_df(year, week, output_dir, players_df):
    players_df_path = output_dir.joinpath(f'yr{year}_wk{week}_player_data.csv')

    # Sort by actual points and then projected points
    players_df = players_df.sort_values(['act_pts', 'proj_pts'], ascending=False)
    players_df = players_df.reset_index(drop=True)

    # Write to csv
    players_df.to_csv(players_df_path)

    return players_df_path

