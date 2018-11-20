"""
Thanksgiving Football module

@author: Logan Thomas
"""
# Standard Libraries
import os
import sys
import random
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

    The default week is 12 (as this is a Thanksgiving tradition),
    the default year is the current year, the default path to
    load the draft data is '{year}/draft_sheet_{year}.xlsx', and
    the default create_draft_order is 'y'. This helper function asks
    the user if they'd like to use these default values; if not,
    a prompt is used to collect the desired values.

    Args:
        value_name (str): The value name to check.
        value (int or str): The default value to check.

    Returns:
        value (int or str): The value to use for the given value name.

    Raises:
        ValueError: If 'y' or 'n' not used to answer prompt.
    """
    # Should default be used?
    use = input('Use default {}: {}? [y/n]: '.format(value_name, value))

    # Prompt answer must by 'y' or 'n'
    if use not in ('y', 'n'):
        raise ValueError('Did not recognize {}. Must be y or n'.format(use))

    # If 'n', user defines value
    if use == 'n':

        if isinstance(value, int):
            value = int(input('Enter {} as integer (Example: {}): '.format(value_name, value)))
        else:
            value = input('Enter {} as string (Example: {}): '.format(value_name, value))

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
    # Default values
    week = 12
    year = dt.datetime.today().year

    # Check whether to use default values
    week = _check_default('week', week)
    year = _check_default('year', year)

    return week, year


def get_draft_data(xlsx_path):
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
        xlsx_path (str): Path to excel spreadsheet. Ideally, each year will
            have its own directory and the excel spreadsheet would be named
            'draft_sheet_{year}.xlsx'. For example, in the year 2018,
            xlsx_path = '2018/draft_sheet_2018.xlsx'.

    Returns:
        participant_teams (dict): A dictionary of participant (str),
        team (pandas DataFrame) key, value pairs.
        (i.e., each participants drafted team as a DF housed in a dict).
    """
    # Load excel sheet
    xlsx = pd.ExcelFile(xlsx_path)

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


def _create_query_url(week, year):
    """
    Creates a url for web scrapping player fantasy points.

    The base url used will always remain the same. However, this function
    creates a query url for the desired week and year to scrape data from.

    Args:
        week (int): The specific NFL week to query.
        year (int): The specific NFL year to query.

    Returns:
        url (str): The query url used to scrape fantasy player points from.
    """
    # Base url
    url_base = 'http://games.espn.com/ffl/leaders?&'

    # Encode week and year
    params = {'scoringPeriodId': week, 'seasonId': year}
    enc_params = urlencode(params)

    # Query url
    url = url_base + enc_params

    return url


def _make_df(list_of_dfs, player_split_char):
    """
    Concatenates a list of pandas DataFrames into one master DataFrame.

    The web scrapping process must pull from different pages as only 50
    players appear on a page at once. This helper function collects
    separate DataFrames from scrapping individual pages into one master
    DataFrame. There are also a number of cleaning steps that occur.
    For instance, filling '--' chars with 0's and dropping 'Unnamed' cols.

    Args:
        list_of_dfs (list of pandas DataFrames): List of DFs to concatenate.
        player_split_char (str): The delimiter to use when splitting a
            player's name. (Position players and kickers use ',' while
            team defenses use ' D/ST').

    Returns:
        df (pandas DataFrame): The aggregated and cleaned DFs in
            one master DataFrame.
    """
    # Aggregate/concatenate DFs into one DF
    df = pd.concat(list_of_dfs).reset_index(drop=True)

    # Replace missing with zeros
    df = df.replace('--', 0).fillna(0)

    # Drop 'Unnamed' columns
    df = df[[col for col in df.columns if 'Unnamed' not in col]]

    # Only collect player name (not team names or positions)
    df['Player'], _ = df['PLAYER, TEAM POS'].str.split(player_split_char, 1).str
    df = df.drop('PLAYER, TEAM POS', axis=1)

    # Reorder columns so player name is first column
    df = df[['Player'] + [col for col in df.columns if col != 'Player']]

    return df


def _convert_cols_num(df):
    """
    Converts all columns that should be numeric to numeric.

    When scrapping, it is not guaranteed that columns in a table are
    represented as numbers. This helper function converts all columns that
    should be represented as numbers to a numerical representation.

    Args:
        df (pandas DataFrame): The DF to convert certain columns to numeric.

    Returns:
        df_numeric (pandas DataFrame): The new DF with numerical columns.
    """
    # Set of non-numeric columns
    # (membership testing faster for sets)
    non_num_cols = set(
        ['Player', 'OPP', 'STATUS ET', 'C/A', '1-39', '40-49', '50+', 'TOT', 'XP']
    )

    # Convert all numeric columns to numeric
    df_non_num_cols = [col for col in df.columns if col in non_num_cols]
    df_numeric = df.set_index(df_non_num_cols)
    df_numeric = df_numeric.apply(pd.to_numeric)
    df_numeric = df_numeric.reset_index()

    return df_numeric


def gather_points(week, year):
    """
    Gathers player fantasy points for given week and year of the NFL season.

    This function scapes the web in order to gather each player's fantasy
    points for the provided week and year of the NFL season. Since the
    players, kickers, and team defenses are housed in separate tables,
    a separate list is used to collect each of these tables individually.
    Also, one single web page only stores information on 50 players at once.
    Thus, the pages must be scrapped iteratively (from 50 to 900 with
    50 player increments). Order matters as the players table appears first,
    followed by the kickers and then the team defenses.

    Args:
        week (int): The specific NFL week to query.
        year (int): The specific NFL year to query.

    Returns:
        players_df (pandas DataFrame): A DF that houses all player points.
        kickers_df (pandas DataFrame): A DF that houses all kicker points.
        defenses_df (pandas DataFrame): A DF that houses all defense points.
    """
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

    # Aggregate and clean DFs
    players_df  = _make_df(players , player_split_char=',')
    kickers_df  = _make_df(kickers , player_split_char=',')
    defenses_df = _make_df(defenses, player_split_char=' D/ST')  # make sure space in front

    players_df  = _convert_cols_num(players_df)
    kickers_df  = _convert_cols_num(kickers_df)
    defenses_df = _convert_cols_num(defenses_df)

    return players_df, kickers_df, defenses_df


def merge_points(participant_teams, players_df, kickers_df, defenses_df):
    """
    Creates a total point breakdown for each participant given their team.

    Gathers fantasy points for each participant's team by merging
    each participant team with the players, kickers, and defenses DFs.
    Since an inner join is used, only those players that have been drafted
    by a given participant are carried through.

    Args:
        participant_teams (dict): A dictionary of participant (str),
            team (pandas DataFrame) key, value pairs.
        players_df (pandas DataFrame): A DF that houses all player points.
        kickers_df (pandas DataFrame): A DF that houses all kicker points.
        defenses_df (pandas DataFrame): A DF that houses all defense points.

    Returns:
        detailed_points (dict): A dictionary of participant (str),
            stats (list of DFs) key, value pairs. The stats list contains
            each participant's specific player, kicker, and defense DFs.
        point_totals (list of tuples): A list of (participant, total point)
            tuples. Total points are the sum of player, kicker, and defense
            points (excluding the 'Bench (RB/WR)' player) for each
            participant.

    Notes:
        Although the 'Bench (RB/WR)' player is reported in the
        player_stats DF, it is not used to calculate the total points for a
        given participant. It is assumed that the 'Bench (RB/WR)' player
        is listed last in the excel spreadsheet.
    """
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
    """
    Prints detailed player stats (points) for a given participant's team.

    Since the detailed points are a list of DFs, each DF is printed to the
    console for convenience. The DFs represent a participant's player,
    kicker, and defense point summary (in that order).

    Args:
        participant (str): The specific participant to print points.
        detailed_points (list of pandas DataFrames): A list containing
            a player_stats DF, a kicker_stats DF, and a defense_stats DF.

    Returns:
        None
    """
    print('### {} stats ###\n'.format(participant.upper()))
    print(*detailed_points[participant], sep='\n\n')


def create_leader_board(detailed_points, point_totals):
    """
    Creates a summary of participants' total points and prints details.

    Participant total points are collected and compared to be placed in
    ranking order. A 'margin' column is created to show how many points
    each participant is beating the next participant by. A 'pts_back'
    column is created to show how many points each participant is behind
    the overall leader. A summary is printed to show who the current overall
    leader is (and by how many points). Each participant's detailed scores
    are printed in order of points (highest to lowest).

    Args:
         detailed_points (dict): A dictionary of participant (str),
            stats (list of DFs) key, value pairs.
        point_totals (list of tuples): A list of (participant, total point)
            tuples.

    Returns:
        leader_board (pandas DataFrame): A DF that shows each participant's
            total points compared to all others in ranked order.
    """
    # Create a DataFrame from point_totals
    leader_board = pd.DataFrame(point_totals, columns=['participant', 'PTS'])

    # Sort the leader board on highest pts to lowest pts
    leader_board = leader_board.sort_values('PTS', ascending=False).reset_index(drop=True)

    # Create column to show how far ahead each participant is compared to next
    leader_board['margin'] = leader_board['PTS'].diff(-1)

    # Create column to show how far out of lead they are
    leader_board['pts_back'] = leader_board.iloc[0,1] - leader_board['PTS'].values

    # Print details on points
    print('\n{} winning with {} pts\n'.format(leader_board.iloc[0,0], leader_board.iloc[0,1]))
    print(leader_board)
    print('\n')

    for person in leader_board['participant']:
        _print_detailed_points(person, detailed_points)
        print('\n\n\n')

    return leader_board


def main():
    """
    TODO:
    Consider returning some of these things
    (leader_board, detailed_scores, etc.) so that entire main
    doesn't need to be run each time
    """
    # Get specific week and year for NFL season
    week, year = get_week_year()

    # Read in draft_sheet_{year}.xlsx
    # Each participant in separate sheet with players drafted by position
    draft_path = os.path.join(str(year), 'draft_sheet_{}.xlsx'.format(year))
    draft_path = _check_default('draft_path', draft_path)

    # Determine each participant's drafted team
    print('\nGathering participant drafted teams...')
    participant_teams = get_draft_data(draft_path)
    print('Successfully gathered drafted teams')

    # Create a random draft order
    create_draft_order = 'y'
    create_draft_order = _check_default('create_draft_order', create_draft_order)

    if create_draft_order == 'y':
        draft_order = make_draft_order(participant_teams)
        print('The draft order is: ')
        print(*draft_order, sep='\n')
        sys.exit()

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


if __name__ == '__main__':
    main()

