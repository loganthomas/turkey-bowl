"""
Set up functions
"""
# Standard libraries
import calendar
from pathlib import Path
from datetime import datetime

# Third party libraries
import numpy as np


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

# Stopped here create function to cp draft_sheet.xlsx to output_dir and add year
# http://fantasy.espn.com/apis/v3/games/ffl/seasons/2019/segments/0/leagues/1241838?view=mDraftDetail&view=mLiveScoring&view=mMatchupScore&scoringPeriodId=11
# http://fantasy.espn.com/apis/v3/games/ffl/seasons/2019/segments/0/leagues/1241838?view=mLiveScoring&view=mMatchupScore&scoringPeriodId=11

# Use urlencode for week and season
# https://api.fantasy.nfl.com/v2/players/weekstats?&week=12&season=2019

# API docs
# https://api.fantasy.nfl.com/v2/docs/service?serviceName=playersWeekStats
# https://api.fantasy.nfl.com/v2/docs/service?serviceName=playerNgsContent

url_base = 'https://api.fantasy.nfl.com/v2/players/weekstats?'
params = {'season': 2019, 'week':12}

from urllib.parse import urlencode
enc_params = urlencode(params)
url = url_base + enc_params

import requests

response = requests.get(url)
response_json = response.json()

players_list = []
for game in response_json['games']:
    g = response_json['games'].get(game)
    players = g.get('players')
    players_list.extend(players)

players_names = []
players_pos   = []
players_teams = []
for player in players_list:
    player_url = f'https://api.fantasy.nfl.com/v2/player/ngs-content?playerId={player}'
    p_response = requests.get(player_url)
    p_response_json = p_response.json()

    for game in p_response_json['games']:
        g = p_response_json['games'].get(game)
        players = g.get('players')
        name = players[player]['name']
        pos  = players[player]['position']
        team = players[player]['nflTeamAbbr']
        players_names.append(name)
        players_pos.append(pos)
        players_teams.append(team)

for i,n,p,t in zip(players_list, players_names, players_pos, players_teams):
    print(f'{i} <---> {n} {p} {t}')


