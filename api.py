"""
API functions

Notes:
    2018 used ESPN web scraping. ESPN changed API in 2019 and broke everything. The below calls
    work for the new API.
    http://fantasy.espn.com/apis/v3/games/ffl/seasons/2019/segments/0/leagues/1241838?
        view=mDraftDetail&view=mLiveScoring&view=mMatchupScore&scoringPeriodId=11
    http://fantasy.espn.com/apis/v3/games/ffl/seasons/2019/segments/0/leagues/1241838?
        view=mLiveScoring&view=mMatchupScore&scoringPeriodId=11

    2019 uses NFL.com instead of ESPN. API docs found below:
    https://api.fantasy.nfl.com/v2/docs/service?serviceName=playersWeekStats
    https://api.fantasy.nfl.com/v2/docs/service?serviceName=playersWeekProjectedStats
    https://api.fantasy.nfl.com/v2/docs/service?serviceName=playerNgsContent
"""
# Standard libraries
from urllib.parse import urlencode
from collections  import namedtuple

# Third-party libraries
import requests
import pandas as pd


def create_query_url(year, week, stats_type):
    """
    Creates a url for web scrapping (or API calling) player fantasy points.

    The base url used will always remain the same. However, this function
    creates a query url for the desired week and year to scrape data from.

    Args:
        year (int): The specific NFL year to query.
        week (int): The specific NFL week to query.
        stats_type (str): Which stats to pull. Can be 'actual' or 'projected'.

    Returns:
        url (str): The query url used to scrape fantasy player points from.
    """
    # Defensive programming
    assert stats_type in ('actual', 'projected'), (
        f"Invalid stats_type. Must be 'actual' or 'projected'. Did not recognize '{stats_type}'."
    )

    # Base url
    if stats_type == 'actual':
        url_base = 'https://api.fantasy.nfl.com/v2/players/weekstats?'
    else:
        url_base = 'https://api.fantasy.nfl.com/v2/players/weekprojectedstats?'

    # Encode week and year
    params = {'season': year, 'week': week}
    enc_params = urlencode(params)

    # Query url
    url = url_base + enc_params

    return url


def create_api_response(url):
    """
    Calls API via requests library and returns response.
    """
    response = requests.get(url)

    if response.status_code == requests.codes.ok:
        print(f'Successful API response obtained for: {url}')
    else:
        print(f'WARNING API response unsuccessful for: {url}')

    return response


def collect_player_ids_pts(response):
    """
    Each player is keyed by id. The value is a dict keyed by:

        {'stats': {'week': {<str year>: {<str week>: '1':'1'...'pts'}}}}

        {'projectedStats': {'week': {<str year>: {<str week>: '1':'1'...'pts'}}}}
    """
    # Convert API response to json format
    response_json = response.json()

    # Get the game id (this isn't an actual game, just an identifier)
    game_id = response_json['systemConfig'].get('currentGameId')

    # Get players metadata (keyed by id)
    player_ids_pts = response_json['games'][game_id].get('players')

    return player_ids_pts


def run_query_and_collection(year, week, stats_type):
    url            = create_query_url(year, week, stats_type)
    response       = create_api_response(url)
    player_ids_pts = collect_player_ids_pts(response)

    return player_ids_pts


def get_player_metadata(player_id):
    """
    Pulls a player's name, position, team, and injury status from API.
    """
    url           = f'https://api.fantasy.nfl.com/v2/player/ngs-content?playerId={player_id}'
    response      = create_api_response(url)
    response_json = response.json()
    game_id       = list(response_json['games'].keys())[0]  # Identifier not really game id

    metadata = response_json['games'][game_id]['players'][player_id]
    name     = metadata.get('name')
    pos      = metadata.get('position')
    team     = metadata.get('nflTeamAbbr')
    injury   = metadata.get('injuryGameStatus')

    return name, pos, team, injury


def get_player_pts(year, week, player_ids_pts, player_id, stats_type):
    # Defensive programming
    assert stats_type in ('stats', 'projectedStats'), (
        f"Invalid stats_type. Must be 'stats' or 'projectedStats'. Didn't recognize '{stats_type}'."
    )

    # Not all players will exist in both actual and projected
    try:
        pts = player_ids_pts[player_id][stats_type]['week'][str(year)][str(week)].get('pts')
    except (KeyError, TypeError):
        pts = 0.0

    # Convert to float, change None to 0.0
    if pts:
        pts = float(pts)
    else:
        pts = 0.0

    return pts


def instantiate_players(year, week, actual_player_ids_pts, projected_player_ids_pts):
    """
    Instantiate all players with id, projected points, and actual points.
    """
    # Create namedtuple to house player date (think Player obj)
    Player = namedtuple(
        typename    = 'Player',
        field_names = ['name', 'id', 'team', 'pos', 'injury','proj_pts', 'act_pts'],
        defaults    = [    '',  0.0,     '',    '',       '',       0.0,       0.0],
    )

    # Gather all unique players within projected and actual
    act_player_ids  = list(actual_player_ids_pts.keys())
    proj_player_ids = list(projected_player_ids_pts.keys())
    player_ids      = list(set(act_player_ids + proj_player_ids))

    # Instantiate output
    players = []

    for pid in player_ids:
        name, pos, team, injury = get_player_metadata(pid)

        act_pts  = get_player_pts(year, week, actual_player_ids_pts, pid, 'stats')
        proj_pts = get_player_pts(year, week, projected_player_ids_pts, pid, 'projectedStats')

        player = Player(
            name     = name,
            id       = pid,
            team     = team,
            pos      = pos,
            injury   = injury,
            act_pts  = act_pts,
            proj_pts = proj_pts
        )
        players.append(player)

    return players


def create_players_df(players):
    """
    Converts players (list of namedtuples) into pd.DataFrame
    """
    return pd.DataFrame(players)


def save_players_df(prior_players_df_path, players_df):
    # Sort by actual points and then projected points
    players_df = players_df.sort_values(['act_pts', 'proj_pts'], ascending=False)
    players_df = players_df.reset_index(drop=True)

    # Write to csv
    players_df.to_csv(prior_players_df_path)


def create_prior_players_file_path(year, week, output_dir):
    """
    Creates a path to the file where prior player dataframe should be saved.
    """
    prior_players_df_path = output_dir.joinpath(f'yr{year}_wk{week}_player_data.csv')

    return prior_players_df_path


def check_prior_players_file_exists(year, week, prior_players_df_path):
    """
    Checks whether the file located at prior_players_df_path exists.
    If not, pull the necessary data and save to the path.

    Notes:
        Need to pull week prior to gather all players (with injury reports/projections).
        Current week only has player ids and pulling prior week helps identify players by name.
        One time costly, but easy to join for updating scores later on.

    TODO: update to include handling of Connection Error?
    """
    # If the file doesn't exist, pull data and create the file
    if not prior_players_df_path.is_file():

        prior_act_ids_pts  = run_query_and_collection(year, week, stats_type='actual')
        prior_proj_ids_pts = run_query_and_collection(year, week, stats_type='projected')

        prior_players = instantiate_players(year, week, prior_act_ids_pts, prior_proj_ids_pts)
        prior_players_df = create_players_df(prior_players)

        prior_players_df_path = save_players_df(prior_players_df_path, prior_players_df)
        print(f'Saved prior week ({week}) players data to {prior_players_df_path}')

    else:
        print(f'Prior week ({week}) players data already exists at {prior_players_df_path}')
        prior_players_df = pd.read_csv(prior_players_df_path, index_col=0)

    return prior_players_df


def update_pts(year, week, participant_teams, stats_type):
    # Pull ids and points from API
    player_ids_pts = run_query_and_collection(year, week, stats_type)

    # Make correct labels
    if stats_type == 'actual':
        stats_label = 'stats'
        col_label   = 'act_pts'
    else:
        stats_label = 'projectedStats'
        col_label   = 'proj_pts'

    for participant, participant_team in participant_teams.items():

        updated_pts = []
        for pid in participant_team['id']:
            try:
                pid = round(pid)
            except (ValueError, TypeError):
                pid = pid

            # Look up points (not an API call)
            pts = get_player_pts(year, week, player_ids_pts, str(pid), stats_label)

            updated_pts.append(pts)

        participant_team[col_label] = updated_pts

    return participant_teams

