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
    except KeyError:
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

