# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 17:10:41 2016

@author: thomlo02
"""

# Standard Libraries
from collections import OrderedDict

# Custom Libraries
import requests
from bs4 import BeautifulSoup as soup
import pandas as pd
import numpy as np


def gather_participants(xls):
    # Collect participant names (grabs sheet names)
    participants = xls.sheet_names

    # Create teams dictionary where key is participant name and
    # value is position/player dataframe
    participant_teams = {}
    for participant in participants:
        participant_teams[participant] = xls.parse(participant)

    return participants, participant_teams


def gather_player_scores(week, year):
    url_base = 'http://games.espn.com/ffl/leaders'

    # loop from 0 to 900 for all html pages (50 players per page in order or scoring)
    for i in np.arange(0, 950, 50):
        params = OrderedDict([
            ('scoringPeriodId', week),
            ('seasonId', year),
            ('startIndex', i)
        ])
        response = requests.get(url_base, params=params)
        successful = response.status_code == requests.codes.ok
        print('Succussful connection for index{i}: {successful}'.format(**locals()))

        html = soup(response.text, 'html.parser')
        column_subheaders = [
            'Player',
            'Comp/Atts',
            'Pass_Yds',
            'Pass_TD',
            'Int_Thrown',
            'Rush_Att',
            'Rush_Yds',
            'Rush_TD',
            'Receps',
            'Rec_Yds',
            'Rec_TD',
            'Rec_Targets',
            '2PC',
            'Fumb_Lost',
            'Return_TD',
            'Total_Pts'
        ]

        # Relevant table rows start at line 3 and on
        data_rows = html.findAll('tr')[3:]
        player_data = [[td.getText() for td in data_rows[i].findAll('td')] for i in range(len(data_rows))]
        df = pd.DataFrame(player_data)

        # Drop Irrelevant columns (opponent, status, spacing cols, etc.)
        df.drop([1, 2, 3, 4, 9, 13, 18, 22], inplace=True, axis=1)

        # Name columns
        df.columns = column_subheaders

        # Collect Player name only (strip defense names to team name only)
        df['Player'] = [x.split(',')[0] for x in df['Player']]
        df['Player'] = df['Player'].str.replace(' D/ST D/ST', '')

        # Aggregate all player scores together
        if i == 0:
            player_scores = df
        else:
            player_scores = player_scores.append(df, ignore_index=True)
    print('Player scores successfully collected and aggregated')
    return player_scores


def merge_scores(participant_teams, player_scores):
    for participant in participant_teams.keys():
        participant_teams[participant] = pd.merge(participant_teams.get(participant),
                                                  player_scores,
                                                  on='Player',
                                                  how='left')
    return participant_teams
            

def create_leader_board(participant_teams):
    leader_board = []
    for participant in participant_teams.keys():
        leader_board.append([participant, pd.to_numeric(participant_teams.get(participant)['Total_Pts'], errors='coerce').sum()])
    leader_board = pd.DataFrame(leader_board, columns=['member', 'score'])
    leader_board = leader_board.sort_values('score', ascending=False).reset_index(drop=True)
    print('Leader: ', leader_board.loc[0, 'member'])
    print('Beating', leader_board.loc[1, 'member'], 'by', leader_board.loc[0, 'score'] - leader_board.loc[1, 'score'])
    return leader_board


def main():
    # Gather year and week for player scores
    year = input('Enter year as integer (Example: 2016): ')
    week = input('Enter week as integer (Example: 12): ')

    # Read in draft workbook (should have players drafted by position)
    xls = pd.ExcelFile('Draft_Workbook_Test.xlsx')

    # Determine participants and participant's drafted team
    participants, participant_teams = gather_participants(xls)

    # Collect player scores for given week and year
    player_scores = gather_player_scores(week, year)

    # Determine participant's draft player scores
    participant_teams = merge_scores(participant_teams, player_scores)

    # Create and print leader board
    leader_board = create_leader_board(participant_teams)
    print(leader_board)

if __name__ == '__main__':
    main()
