"""
Thanksgiving Football module

@author: Logan Thomas
"""
# Standard Libraries
import os
import datetime as dt
from urllib.parse import urlencode

# Third-party libraries
import pandas as pd
import numpy as np

# Set option for nice DataFrame display
pd.options.display.width = None


def _check_default(value_name, value):
    """
    Determines whether to use or overwrite a default value.

    The default week is 12 (as this is a Thanksgiving tradition)
    and the default year is the current year. This helper function
    asks the user if they'd like to use the default value for week
    and/or year; if not, a prompt is used to collect the desired
    value.

    Args:
        value_name (str): The value name to check (i.e., 'week' or 'year').
        value (int): The integer default value to check (i.e., 12 or 2018).

    Returns:
        value (int): The integer value to use for the given value name.

    Raises:
        ValueError: If 'y' or 'n' not used to answer prompt.
    """
    use = input('Use default {}: {}? [y/n]: '.format(value_name, value))

    if use not in ('y', 'n'):
        raise ValueError('Did not recognize {}. Must be y or n'.format(use))
    if use == 'n':
        value = int(input('Enter {} as integer (Example: {}): '.format(value_name, value)))

    return value


def get_week_year():
    """
    Collects the week and year to run.

    There are specific weeks within the NFL season. This function gathers
    to correct week and year to use.

    Args:
        None

    Returns:
        week (int): Specific week to run. Defaults to 12.
        year (int): Specific year to run. Defaults to current year.
    """
    week = 12
    year = dt.datetime.today().year

    week = _check_default('week', week)
    year = _check_default('year', year)

    return week, year


def get_draft_data(xlsx):
    """
    Parses an excel spreadsheet into participant teams.

    The drafted teams should be collected within one excel spreadsheet
    in which each participant is a separate sheet. The sheet names
    correspond to the names of the participants and each sheet should have
    a 'Position' column and a 'Player' column. For the time being, the
    draft-able positions are as follows:
        'QB', 'RB_1', 'RB_2', 'WR_1', 'WR_2', 'TE',
        'Flex (RB/WR)', 'K', 'Defense (Team Name)', 'Bench (RB/WR)'.

    Args:
        xlsx (str): Path to excel spreadsheet. Ideally, each year will have
            its own directory and the excel spreadsheet would be named
            draft_sheet_{year}.xlsx. For example, in the year 2018,
            xlsx = '/2018/draft_sheet_2018.xlsx'.

    Returns:
        participant_teams (dict):

    # TODO: Update this to read the sheet rather than use the return of pd
    ########################################################################
    """
    # Collect participant names
    participants = xlsx.sheet_names

    # Get each participant's drafted players
    participant_teams = {}
    for participant in participants:
        participant_teams[participant] = xlsx.parse(participant)

    return participant_teams


def _create_query_url(week, year):
    url_base = 'http://games.espn.com/ffl/leaders?&'
    params = {'scoringPeriodId': week, 'seasonId': year}
    enc_params = urlencode(params)
    url = url_base + enc_params

    return url


def _make_df(list_of_dfs, player_split_char):
    df = pd.concat(list_of_dfs).reset_index(drop=True)
    df = df.replace('--', 0).fillna(0)
    df = df[[col for col in df.columns if 'Unnamed' not in col]]
    df['Player'], _ = df['PLAYER, TEAM POS'].str.split(player_split_char, 1).str
    df = df.drop('PLAYER, TEAM POS', axis=1)
    df = df[['Player'] + [col for col in df.columns if col != 'Player']]
    return df


def _convert_cols_num(df):
    # Membership testing faster for sets
    non_num_cols = set(['Player', 'OPP', 'STATUS ET', 'C/A', '1-39', '40-49', '50+', 'TOT', 'XP'])
    df_non_num_cols = [col for col in df.columns if col in non_num_cols]

    df = df.set_index(df_non_num_cols)
    df = df.apply(pd.to_numeric)
    df = df.reset_index()

    return df


def gather_points(week, year):
    # Specify url to query from
    url = _create_query_url(week, year)

    # Instantiate lists for gathering info from url
    players  = []
    kickers  = []
    defenses = []

    # Each page has 50 players; loop until 900
    for i in range(0, 950, 50):
        page_url = url + '&startIndex={}'.format(i)

        # Use pandas to search for all <table> elements and only grab <td> elements therein
        tables = pd.read_html(page_url, header=1)

        # Order matters; each page has players at a minimum, then kickers, then teams
        try:
            players.append(tables[1])
            kickers.append(tables[2])
            defenses.append(tables[3])

        except IndexError:
            continue

    players_df  = _make_df(players , player_split_char=',')
    kickers_df  = _make_df(kickers , player_split_char=',')
    defenses_df = _make_df(defenses, player_split_char=' D/ST')  # make sure space in front

    players_df  = _convert_cols_num(players_df)
    kickers_df  = _convert_cols_num(kickers_df)
    defenses_df = _convert_cols_num(defenses_df)

    return players_df, kickers_df, defenses_df


def merge_points(participant_teams, players_df, kickers_df, defenses_df):

    # Instantiate output
    detailed_points = {}
    point_totals = []

    # Loop over participants and their drafted players, joining point stats
    for participant, participant_team in participant_teams.items():
        player_stats  = participant_team.merge( players_df , on='Player')
        kicker_stats  = participant_team.merge( kickers_df , on='Player')
        defense_stats = participant_team.merge( defenses_df, on='Player')
        stats         = [player_stats, kicker_stats, defense_stats]

        # Collect participants players, kicker, defense stats
        detailed_points[participant] = stats

        # Collect participants point total (sum of players, kicker, defense PTs)
        # Assumes Bench player is last player listed and should not be included
        # (i.e., take only first 7 players to sum in player_stats)
        points = [stat['PTS'].values[:7] for stat in stats]
        point_total = sum(np.hstack(points))
        point_totals.append((participant, point_total))

    return detailed_points, point_totals


def _print_detailed_points(participant, detailed_points):
        print('### {} stats ###\n'.format(participant.upper()))
        print(*detailed_points[participant], sep='\n\n')


def create_leader_board(detailed_points, point_totals):
    leader_board = pd.DataFrame(point_totals, columns=['participant', 'PTS'])
    leader_board = leader_board.sort_values('PTS', ascending=False).reset_index(drop=True)
    leader_board['margin'] = leader_board['PTS'].diff(-1)
    leader_board['pts_back'] = leader_board.iloc[0,1] - leader_board['PTS'].values

    print('\n{} winning with {} pts\n'.format(leader_board.iloc[0,0], leader_board.iloc[0,1]))
    print(leader_board)
    print('\n')

    for person in leader_board['participant']:
        _print_detailed_points(person, detailed_points)
        print('\n\n\n')

    return leader_board


def main():
    # Get specific week and year for NFL season
    week, year = get_week_year()

    # Read in draft workbook (should have players drafted by position)
    print('\nLoading draft data...')
    f_path = os.path.join(os.getcwd(), str(year), 'draft_sheet_{}.xlsx'.format(year))
    xlsx = pd.ExcelFile(f_path)
    print('Loaded {}'.format(f_path))

    # Determine each participant's drafted team
    print('\nGathering participant drafted teams')
    participant_teams = get_draft_data(xlsx)
    print('Successfully gathered drafted teams')

    # Collect player scores for given week and year
    print('\nGathering points for week {} year {} by scraping the web...'.format(week, year))
    players_df, kickers_df, defenses_df = gather_points(week, year)
    print('Successfully gathered players, kickers, and defenses points')

    # Determine participant's draft player scores
    print('\nMerging points to drafted teams...')
    detailed_pnts, pnt_totals = merge_points(participant_teams, players_df, kickers_df, defenses_df)
    print('Successfully merged points to participants drafted teams')

    # Create and print leader board
    leader_board = create_leader_board(detailed_pnts, pnt_totals)
    print('\n{} winning with {} pts\n'.format(leader_board.iloc[0,0], leader_board.iloc[0,1]))
    print(leader_board)

    # TODO:
    # Consider returning some of these things (leader_board, detailed_scores, etc.)
    # so that entire main doesn't need to be run each time


if __name__ == '__main__':
    main()

