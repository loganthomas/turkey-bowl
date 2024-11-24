"""
Unit tests for aggregate.py
"""

import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import responses

from turkey_bowl import aggregate, utils


@pytest.fixture
def mock_proj_player_pts():
    player_pts = {
        '2504211': {
            'projectedStats': {
                'week': {
                    '2020': {
                        '12': {
                            '1': '1',
                            '14': '0.05',
                            '20': '1.1',
                            '21': '13.11',
                            '22': '0.09',
                            'pts': '2.96',
                        }
                    }
                }
            }
        },
        '310': {
            'projectedStats': {
                'week': {
                    '2020': {
                        '12': {
                            '1': '1',
                            '14': '5.5',
                            '20': '3.3',
                            '21': '17.11',
                            '22': '0.07',
                            'pts': '9.96',
                        }
                    }
                }
            }
        },
    }

    return player_pts


@pytest.fixture
def mock_actual_player_pts():
    player_pts = {
        '2504211': {
            'stats': {
                'week': {
                    '2020': {
                        '12': {
                            '1': '1',
                            '14': '0.05',
                            '20': '1.1',
                            '21': '13.11',
                            '22': '0.09',
                            'pts': '2.96',
                        }
                    }
                }
            }
        },
        '310': {
            'stats': {
                'week': {
                    '2020': {
                        '12': {
                            '1': '1',
                            '14': '5.5',
                            '20': '3.3',
                            '21': '17.11',
                            '22': '0.07',
                            'pts': '9.96',
                        }
                    }
                }
            }
        },
    }

    return player_pts


def test__get_player_pts_stats_type_raises_error_for_multi_types(
    mock_proj_player_pts, mock_actual_player_pts
):
    # Setup
    proj_player_pts = mock_proj_player_pts
    actual_player_pts = mock_actual_player_pts

    # Intentionally mix proj and actual to raise an error
    player_pts = {
        '2504211': proj_player_pts['2504211'],
        '310': actual_player_pts['310'],
    }

    expected_error1 = "More than one unique stats type detected: {'stats', 'projectedStats'}"
    expected_error2 = "More than one unique stats type detected: {'projectedStats', 'stats'}"
    # Exercise
    with pytest.raises(ValueError) as error_info:
        aggregate._get_player_pts_stat_type(player_pts)

    # Verify
    assert str(error_info.value) in (expected_error1, expected_error2)

    # Verify

    # Cleanup - none necessary


def test__get_player_pts_stats_type_raises_error_for_unrecognized_type():
    # Setup
    player_pts = {
        '2504211': {
            'bad_stats': {
                'week': {
                    '2020': {
                        '12': {
                            '1': '1',
                            '14': '0.05',
                            '20': '1.1',
                            '21': '13.11',
                            '22': '0.09',
                            'pts': '2.96',
                        }
                    }
                }
            }
        },
        '310': {
            'bad_stats': {
                'week': {
                    '2020': {
                        '12': {
                            '1': '1',
                            '14': '5.5',
                            '20': '3.3',
                            '21': '17.11',
                            '22': '0.07',
                            'pts': '9.96',
                        }
                    }
                }
            }
        },
    }

    expected_error = (
        "Unrecognized stats type: 'bad_stats'. Expected either 'projectedStats' or 'stats'."
    )
    # Exercise
    with pytest.raises(ValueError) as error_info:
        aggregate._get_player_pts_stat_type(player_pts)

    # Verify
    assert str(error_info.value) == expected_error

    # Verify

    # Cleanup - none necessary


@pytest.mark.parametrize('stat_type', ['projectedStats', 'stats'], ids=['projected', 'actual'])
def test__get_player_pts_stats_type(stat_type, mock_proj_player_pts, mock_actual_player_pts):
    # Setup
    if stat_type == 'projectedStats':
        player_pts = mock_proj_player_pts
    else:
        player_pts = mock_actual_player_pts

    # Exercise
    result = aggregate._get_player_pts_stat_type(player_pts)

    # Verify
    assert result == stat_type

    # Verify

    # Cleanup - none necessary


def test__unpack_player_pts():
    # Setup
    year = 2020
    week = 12

    single_player_pts_dict = {
        'stats': {
            'week': {
                str(year): {
                    str(week): {
                        '1': '1',
                        '14': '0.05',
                        '20': '1.1',
                        '21': '13.11',
                        '22': '0.09',
                        'pts': '2.96',
                    }
                }
            }
        }
    }

    expected = {
        '1': '1',
        '14': '0.05',
        '20': '1.1',
        '21': '13.11',
        '22': '0.09',
        'pts': '2.96',
    }

    # Exercise
    result = aggregate._unpack_player_pts(year, week, single_player_pts_dict)

    # Verify
    assert result == expected

    # Cleanup - none necessary


def test_create_player_pts_df_raises_error_when_projected_and_no_savepath():
    # Setup
    year = 2020
    week = 12
    player_pts = {
        '252': {'projectedStats': {}},
        '310': {'projectedStats': {}},
        '382': {'projectedStats': {}},
    }

    expected_error = (
        'When creating a projected player points dataframe, ``savepath`` must be specified.'
    )

    # Exercise
    with pytest.raises(ValueError) as error_info:
        aggregate.create_player_pts_df(year, week, player_pts)

    # Verify
    assert str(error_info.value) == expected_error

    # Cleanup - none necessary


def test_projected_player_pts_pulled_true(tmp_path, caplog):
    # Setup
    caplog.set_level(logging.INFO)
    year = 2020
    week = 12

    tmp_archive_dir = tmp_path.joinpath('archive')
    tmp_archive_dir.mkdir()

    tmp_year_dir = tmp_archive_dir.joinpath(str(year))
    tmp_year_dir.mkdir()

    tmp_projected_player_pts_path = tmp_path.joinpath(f'{year}_{week}_projected_player_pts.csv')

    player_pts_df_data = {
        'Player': {0: 'Chad Henne', 1: 'Matt Ryan', 2: 'Joe Flacco'},
        'Team': {0: 'KC', 1: 'IND', 2: 'NYJ'},
        'PROJ_pts': {0: 0.31, 1: 20.01, 2: 0.84},
        'PROJ_Games_Played': {0: 1, 1: 1, 2: 1},
        'PROJ_Passing_Yards': {0: 6.05, 1: 296.77, 2: 16.93},
        'PROJ_Passing_Touchdowns': {0: 0.03, 1: 1.94, 2: 0.04},
        'PROJ_Interceptions_Thrown': {0: 0.04, 1: 0.74, 2: 0.06},
        'PROJ_Rushing_Yards': {0: 0.06, 1: 9.99, 2: np.nan},
        'PROJ_Fumbles_Lost': {0: 0.01, 1: 0.09, 2: 0.01},
        'PROJ_2-Point_Conversions': {0: 0.02, 1: 0.19, 2: 0.04},
        'PROJ_Rushing_Touchdowns': {0: np.nan, 1: 0.11, 2: 0.01},
        'PROJ_Tackle': {0: np.nan, 1: np.nan, 2: np.nan},
        'PROJ_Assisted_Tackles': {0: np.nan, 1: np.nan, 2: np.nan},
        'PROJ_Sack': {0: np.nan, 1: np.nan, 2: np.nan},
        'PROJ_Defense_Interception': {0: np.nan, 1: np.nan, 2: np.nan},
        'PROJ_Forced_Fumble': {0: np.nan, 1: np.nan, 2: np.nan},
        'PROJ_Fumbles_Recovery': {0: np.nan, 1: np.nan, 2: np.nan},
        'PROJ_Blocked_Kick_(punt,_FG,_PAT)': {0: np.nan, 1: np.nan, 2: np.nan},
        'PROJ_Pass_Defended': {0: np.nan, 1: np.nan, 2: np.nan},
        'PROJ_Receptions': {0: np.nan, 1: np.nan, 2: np.nan},
        'PROJ_Receiving_Yards': {0: np.nan, 1: np.nan, 2: np.nan},
        'PROJ_Receiving_Touchdowns': {0: np.nan, 1: np.nan, 2: np.nan},
        'PROJ_PAT_Made': {0: np.nan, 1: np.nan, 2: np.nan},
        'PROJ_FG_Made_0-19': {0: np.nan, 1: np.nan, 2: np.nan},
        'PROJ_FG_Made_20-29': {0: np.nan, 1: np.nan, 2: np.nan},
        'PROJ_FG_Made_30-39': {0: np.nan, 1: np.nan, 2: np.nan},
        'PROJ_FG_Made_40-49': {0: np.nan, 1: np.nan, 2: np.nan},
        'PROJ_FG_Missed_50+': {0: np.nan, 1: np.nan, 2: np.nan},
        'PROJ_Sacks': {0: np.nan, 1: np.nan, 2: np.nan},
        'PROJ_Interceptions': {0: np.nan, 1: np.nan, 2: np.nan},
        'PROJ_Fumbles_Recovered': {0: np.nan, 1: np.nan, 2: np.nan},
        'PROJ_Safeties': {0: np.nan, 1: np.nan, 2: np.nan},
        'PROJ_Touchdowns': {0: np.nan, 1: np.nan, 2: np.nan},
        'PROJ_Blocked_Kicks': {0: np.nan, 1: np.nan, 2: np.nan},
        'PROJ_Kickoff_and_Punt_Return_Touchdowns': {0: np.nan, 1: np.nan, 2: np.nan},
        'PROJ_Points_Allowed': {0: np.nan, 1: np.nan, 2: np.nan},
        'PROJ_Safety': {0: np.nan, 1: np.nan, 2: np.nan},
        'PROJ_Kickoff_and_Punt_Return_Touchdowns.1': {0: np.nan, 1: np.nan, 2: np.nan},
    }

    player_pts_df = pd.DataFrame(player_pts_df_data)
    player_pts_df = player_pts_df.fillna(0.0)
    player_pts_df.to_csv(tmp_projected_player_pts_path)

    # Exercise
    assert tmp_projected_player_pts_path.exists() is True
    result = aggregate.projected_player_pts_pulled(year, week, tmp_projected_player_pts_path)

    # Verify
    assert result is True

    assert f'Projected player data already exists at {tmp_projected_player_pts_path}' in caplog.text

    # Cleanup - none necessary


def test_projected_player_pts_pulled_false(tmp_path):
    # Setup
    year = 2020
    week = 12

    tmp_archive_dir = tmp_path.joinpath('archive')
    tmp_archive_dir.mkdir()

    tmp_year_dir = tmp_archive_dir.joinpath(str(year))
    tmp_year_dir.mkdir()

    tmp_projected_player_pts_path = tmp_path.joinpath(f'{year}_{week}_projected_player_pts.csv')

    # Exercise
    assert tmp_projected_player_pts_path.exists() is False
    result = aggregate.projected_player_pts_pulled(year, week, tmp_projected_player_pts_path)

    # Verify
    assert result is False

    # Cleanup - none necessary


@responses.activate
def test_create_player_pts_df_projected_doesnt_exists(tmp_path, caplog):
    # Setup
    caplog.set_level(logging.INFO)
    year = 2020
    week = 12

    tmp_archive_dir = tmp_path.joinpath('archive')
    tmp_archive_dir.mkdir()

    tmp_year_dir = tmp_archive_dir.joinpath(str(year))
    tmp_year_dir.mkdir()

    tmp_projected_player_pts_path = tmp_path.joinpath(f'{year}_{week}_projected_player_pts.csv')

    player_pts = {
        '2555260': {
            'projectedStats': {
                'week': {
                    '2020': {
                        '12': {
                            '1': '1',
                            '5': '6.05',
                            '6': '0.03',
                            '7': '0.04',
                            '14': '0.06',
                            '30': '0.01',
                            '32': '0.02',
                            'pts': '0.31',
                        }
                    }
                }
            }
        },
        '2555334': {
            'projectedStats': {
                'week': {
                    '2020': {
                        '12': {
                            '1': '1',
                            '5': '296.77',
                            '6': '1.94',
                            '7': '0.74',
                            '14': '9.99',
                            '15': '0.11',
                            '30': '0.09',
                            '32': '0.19',
                            'pts': '20.01',
                        }
                    }
                }
            }
        },
        '2568216': {
            'projectedStats': {
                'week': {
                    '2020': {
                        '12': {
                            '1': '1',
                            '5': '16.93',
                            '6': '0.04',
                            '7': '0.06',
                            '15': '0.01',
                            '30': '0.01',
                            '32': '0.04',
                            'pts': '0.84',
                        }
                    }
                }
            }
        },
    }

    player_pts_df_data = {
        'Player': {0: 'Dak Prescott', 1: 'Jared Goff', 2: 'Brock Purdy'},
        'Team': {0: 'DAL', 1: 'DET', 2: 'SF'},
        'PROJ_Position': {0: 'QB', 1: 'QB', 2: 'QB'},
        'PROJ_pts': {0: 0.31, 1: 20.01, 2: 0.84},
        'PROJ_Games_Played': {0: 1.0, 1.0: 1.0, 2: 1.0},
        'PROJ_Passing_Yards': {0: 6.05, 1: 296.77, 2: 16.93},
        'PROJ_Passing_Touchdowns': {0: 0.03, 1: 1.94, 2: 0.04},
        'PROJ_Interceptions_Thrown': {0: 0.04, 1: 0.74, 2: 0.06},
        'PROJ_Rushing_Yards': {0: 0.06, 1: 9.99, 2: np.nan},
        'PROJ_Fumbles_Lost': {0: 0.01, 1: 0.09, 2: 0.01},
        'PROJ_2-Point_Conversions': {0: 0.02, 1: 0.19, 2: 0.04},
        'PROJ_Rushing_Touchdowns': {0: np.nan, 1: 0.11, 2: 0.01},
    }

    expected = pd.DataFrame(player_pts_df_data)
    expected = expected.fillna(0.0)
    expected_dtypes = {
        'Player': np.dtype('O'),
        'Team': np.dtype('O'),
        'PROJ_Position': np.dtype('O'),
        'PROJ_pts': np.dtype('float64'),
        'PROJ_Games_Played': np.dtype('float64'),
        'PROJ_Passing_Yards': np.dtype('float64'),
        'PROJ_Passing_Touchdowns': np.dtype('float64'),
        'PROJ_Interceptions_Thrown': np.dtype('float64'),
        'PROJ_Rushing_Yards': np.dtype('float64'),
        'PROJ_Fumbles_Lost': np.dtype('float64'),
        'PROJ_2-Point_Conversions': np.dtype('float64'),
        'PROJ_Rushing_Touchdowns': np.dtype('float64'),
    }

    # Mock undocumented player request
    url_2555260 = 'https://api.fantasy.nfl.com/v2/player/ngs-content?playerId=2555260'
    request_json_2555260 = {
        'games': {
            '102023': {
                'players': {
                    '2555260': {
                        'playerId': '2555260',
                        'nflGlobalEntityId': '32005052-4528-5723-d1b2-96e92ebc1241',
                        'esbId': 'PRE285723',
                        'name': 'Dak Prescott',
                        'firstName': 'Dak',
                        'lastName': 'Prescott',
                        'position': 'QB',
                        'nflTeamAbbr': 'DAL',
                        'nflTeamId': '8',
                        'injuryGameStatus': np.nan,
                        'imageUrl': 'https://static.www.nfl.com/image/private/w_200,h_200,c_fill/league/knx0jxponzfkusnyvjkn',
                        'smallImageUrl': 'https://static.www.nfl.com/image/private/w_65,h_90,c_fill/league/knx0jxponzfkusnyvjkn',
                        'largeImageUrl': 'https://static.www.nfl.com/image/private/w_1400,h_1000,c_fill/league/knx0jxponzfkusnyvjkn',
                        'byeWeek': '7',
                        'cancelledWeeks': [],
                        'archetypes': [],
                        'isUndroppable': False,
                        'isReserveStatus': False,
                        'lastVideoTimestamp': np.nan,
                    }
                }
            }
        }
    }
    responses.add(method=responses.GET, url=url_2555260, json=request_json_2555260, status=200)

    url_2555334 = 'https://api.fantasy.nfl.com/v2/player/ngs-content?playerId=2555334'
    request_json_2555334 = {
        'games': {
            '102023': {
                'players': {
                    '2555334': {
                        'playerId': '2555334',
                        'nflGlobalEntityId': '3200474f-4621-9636-7354-d2eb6365d257',
                        'esbId': 'GOF219636',
                        'name': 'Jared Goff',
                        'firstName': 'Jared',
                        'lastName': 'Goff',
                        'position': 'QB',
                        'nflTeamAbbr': 'DET',
                        'nflTeamId': '10',
                        'injuryGameStatus': np.nan,
                        'imageUrl': 'https://static.www.nfl.com/image/private/w_200,h_200,c_fill/league/nyitt4ybuzopzjzddafi',
                        'smallImageUrl': 'https://static.www.nfl.com/image/private/w_65,h_90,c_fill/league/nyitt4ybuzopzjzddafi',
                        'largeImageUrl': 'https://static.www.nfl.com/image/private/w_1400,h_1000,c_fill/league/nyitt4ybuzopzjzddafi',
                        'byeWeek': '9',
                        'cancelledWeeks': [],
                        'archetypes': [],
                        'isUndroppable': False,
                        'isReserveStatus': False,
                        'lastVideoTimestamp': np.nan,
                    }
                }
            }
        }
    }
    responses.add(method=responses.GET, url=url_2555334, json=request_json_2555334, status=200)

    url_2568216 = 'https://api.fantasy.nfl.com/v2/player/ngs-content?playerId=2568216'
    request_json_2568216 = {
        'games': {
            '102023': {
                'players': {
                    '2568216': {
                        'playerId': '2568216',
                        'nflGlobalEntityId': '32005055-5224-3289-b108-8aab5e23b748',
                        'esbId': np.nan,
                        'name': 'Brock Purdy',
                        'firstName': 'Brock',
                        'lastName': 'Purdy',
                        'position': 'QB',
                        'nflTeamAbbr': 'SF',
                        'nflTeamId': '29',
                        'injuryGameStatus': np.nan,
                        'imageUrl': 'https://static.www.nfl.com/image/private/w_200,h_200,c_fill/league/hdwbdlyiose4znenx5ed',
                        'smallImageUrl': 'https://static.www.nfl.com/image/private/w_65,h_90,c_fill/league/hdwbdlyiose4znenx5ed',
                        'largeImageUrl': 'https://static.www.nfl.com/image/private/w_1400,h_1000,c_fill/league/hdwbdlyiose4znenx5ed',
                        'byeWeek': '9',
                        'cancelledWeeks': [],
                        'archetypes': [],
                        'isUndroppable': False,
                        'isReserveStatus': False,
                        'lastVideoTimestamp': np.nan,
                    }
                }
            }
        }
    }
    responses.add(method=responses.GET, url=url_2568216, json=request_json_2568216, status=200)

    # Exercise
    assert tmp_projected_player_pts_path.exists() is False
    result = aggregate.create_player_pts_df(year, week, player_pts, tmp_projected_player_pts_path)
    result_written = pd.read_csv(tmp_projected_player_pts_path, index_col=0)

    # Verify
    assert result.to_html() == expected.to_html()
    assert result.equals(expected)
    assert result_written.equals(expected)
    assert result.equals(result_written)
    assert result.isnull().sum().sum() == 0
    assert result.dtypes.to_dict() == expected_dtypes

    assert 'All player ids in pulled player points exist in player_ids.json' in caplog.text
    assert f'Writing projected player stats to {tmp_projected_player_pts_path}...' in caplog.text
    # Cleanup - none necessary


@responses.activate
def test_create_player_pts_df_actual(tmp_path):
    # Setup
    year = 2020
    week = 12

    tmp_archive_dir = tmp_path.joinpath('archive')
    tmp_archive_dir.mkdir()

    tmp_year_dir = tmp_archive_dir.joinpath(str(year))
    tmp_year_dir.mkdir()

    tmp_projected_player_pts_path = tmp_path.joinpath(f'{year}_{week}_projected_player_pts.csv')

    player_pts = {
        '2555260': {
            'stats': {
                'week': {
                    '2020': {
                        '12': {
                            '1': '1',
                            '5': '6.05',
                            '6': '0.03',
                            '7': '0.04',
                            '14': '0.06',
                            '30': '0.01',
                            '32': '0.02',
                            'pts': '0.31',
                        }
                    }
                }
            }
        },
        '2555334': {
            'stats': {
                'week': {
                    '2020': {
                        '12': {
                            '1': '1',
                            '5': '296.77',
                            '6': '1.94',
                            '7': '0.74',
                            '14': '9.99',
                            '15': '0.11',
                            '30': '0.09',
                            '32': '0.19',
                            'pts': '20.01',
                        }
                    }
                }
            }
        },
        '2568216': {
            'stats': {
                'week': {
                    '2020': {
                        '12': {
                            '1': '1',
                            '5': '16.93',
                            '6': '0.04',
                            '7': '0.06',
                            '15': '0.01',
                            '30': '0.01',
                            '32': '0.04',
                            'pts': '0.84',
                        }
                    }
                }
            }
        },
    }

    player_pts_df_data = {
        'Player': {0: 'Dak Prescott', 1: 'Jared Goff', 2: 'Brock Purdy'},
        'Team': {0: 'DAL', 1: 'DET', 2: 'SF'},
        'PROJ_Position': {0: 'QB', 1: 'QB', 2: 'QB'},
        'ACTUAL_pts': {0: 0.31, 1: 20.01, 2: 0.84},
        'ACTUAL_Games_Played': {0: 1.0, 1.0: 1.0, 2: 1.0},
        'ACTUAL_Passing_Yards': {0: 6.05, 1: 296.77, 2: 16.93},
        'ACTUAL_Passing_Touchdowns': {0: 0.03, 1: 1.94, 2: 0.04},
        'ACTUAL_Interceptions_Thrown': {0: 0.04, 1: 0.74, 2: 0.06},
        'ACTUAL_Rushing_Yards': {0: 0.06, 1: 9.99, 2: np.nan},
        'ACTUAL_Fumbles_Lost': {0: 0.01, 1: 0.09, 2: 0.01},
        'ACTUAL_2-Point_Conversions': {0: 0.02, 1: 0.19, 2: 0.04},
        'ACTUAL_Rushing_Touchdowns': {0: np.nan, 1: 0.11, 2: 0.01},
    }

    expected = pd.DataFrame(player_pts_df_data)
    expected = expected.fillna(0.0)
    expected_dtypes = {
        'Player': np.dtype('O'),
        'Team': np.dtype('O'),
        'PROJ_Position': np.dtype('O'),
        'ACTUAL_pts': np.dtype('float64'),
        'ACTUAL_Games_Played': np.dtype('float64'),
        'ACTUAL_Passing_Yards': np.dtype('float64'),
        'ACTUAL_Passing_Touchdowns': np.dtype('float64'),
        'ACTUAL_Interceptions_Thrown': np.dtype('float64'),
        'ACTUAL_Rushing_Yards': np.dtype('float64'),
        'ACTUAL_Fumbles_Lost': np.dtype('float64'),
        'ACTUAL_2-Point_Conversions': np.dtype('float64'),
        'ACTUAL_Rushing_Touchdowns': np.dtype('float64'),
    }

    # Mock undocumented player request
    url_2555260 = 'https://api.fantasy.nfl.com/v2/player/ngs-content?playerId=2555260'
    request_json_2555260 = {
        'games': {
            '102023': {
                'players': {
                    '2555260': {
                        'playerId': '2555260',
                        'nflGlobalEntityId': '32005052-4528-5723-d1b2-96e92ebc1241',
                        'esbId': 'PRE285723',
                        'name': 'Dak Prescott',
                        'firstName': 'Dak',
                        'lastName': 'Prescott',
                        'position': 'QB',
                        'nflTeamAbbr': 'DAL',
                        'nflTeamId': '8',
                        'injuryGameStatus': np.nan,
                        'imageUrl': 'https://static.www.nfl.com/image/private/w_200,h_200,c_fill/league/knx0jxponzfkusnyvjkn',
                        'smallImageUrl': 'https://static.www.nfl.com/image/private/w_65,h_90,c_fill/league/knx0jxponzfkusnyvjkn',
                        'largeImageUrl': 'https://static.www.nfl.com/image/private/w_1400,h_1000,c_fill/league/knx0jxponzfkusnyvjkn',
                        'byeWeek': '7',
                        'cancelledWeeks': [],
                        'archetypes': [],
                        'isUndroppable': False,
                        'isReserveStatus': False,
                        'lastVideoTimestamp': np.nan,
                    }
                }
            }
        }
    }
    responses.add(method=responses.GET, url=url_2555260, json=request_json_2555260, status=200)

    url_2555334 = 'https://api.fantasy.nfl.com/v2/player/ngs-content?playerId=2555334'
    request_json_2555334 = {
        'games': {
            '102023': {
                'players': {
                    '2555334': {
                        'playerId': '2555334',
                        'nflGlobalEntityId': '3200474f-4621-9636-7354-d2eb6365d257',
                        'esbId': 'GOF219636',
                        'name': 'Jared Goff',
                        'firstName': 'Jared',
                        'lastName': 'Goff',
                        'position': 'QB',
                        'nflTeamAbbr': 'DET',
                        'nflTeamId': '10',
                        'injuryGameStatus': np.nan,
                        'imageUrl': 'https://static.www.nfl.com/image/private/w_200,h_200,c_fill/league/nyitt4ybuzopzjzddafi',
                        'smallImageUrl': 'https://static.www.nfl.com/image/private/w_65,h_90,c_fill/league/nyitt4ybuzopzjzddafi',
                        'largeImageUrl': 'https://static.www.nfl.com/image/private/w_1400,h_1000,c_fill/league/nyitt4ybuzopzjzddafi',
                        'byeWeek': '9',
                        'cancelledWeeks': [],
                        'archetypes': [],
                        'isUndroppable': False,
                        'isReserveStatus': False,
                        'lastVideoTimestamp': np.nan,
                    }
                }
            }
        }
    }
    responses.add(method=responses.GET, url=url_2555334, json=request_json_2555334, status=200)

    url_2568216 = 'https://api.fantasy.nfl.com/v2/player/ngs-content?playerId=2568216'
    request_json_2568216 = {
        'games': {
            '102023': {
                'players': {
                    '2568216': {
                        'playerId': '2568216',
                        'nflGlobalEntityId': '32005055-5224-3289-b108-8aab5e23b748',
                        'esbId': np.nan,
                        'name': 'Brock Purdy',
                        'firstName': 'Brock',
                        'lastName': 'Purdy',
                        'position': 'QB',
                        'nflTeamAbbr': 'SF',
                        'nflTeamId': '29',
                        'injuryGameStatus': np.nan,
                        'imageUrl': 'https://static.www.nfl.com/image/private/w_200,h_200,c_fill/league/hdwbdlyiose4znenx5ed',
                        'smallImageUrl': 'https://static.www.nfl.com/image/private/w_65,h_90,c_fill/league/hdwbdlyiose4znenx5ed',
                        'largeImageUrl': 'https://static.www.nfl.com/image/private/w_1400,h_1000,c_fill/league/hdwbdlyiose4znenx5ed',
                        'byeWeek': '9',
                        'cancelledWeeks': [],
                        'archetypes': [],
                        'isUndroppable': False,
                        'isReserveStatus': False,
                        'lastVideoTimestamp': np.nan,
                    }
                }
            }
        }
    }
    responses.add(method=responses.GET, url=url_2568216, json=request_json_2568216, status=200)

    # Exercise
    assert tmp_projected_player_pts_path.exists() is False
    result = aggregate.create_player_pts_df(year, week, player_pts, tmp_projected_player_pts_path)

    # Verify
    assert result.to_html() == expected.to_html()  # for debugging unequal dataframes
    assert result.equals(expected)
    assert result.isnull().sum().sum() == 0
    assert result.dtypes.to_dict() == expected_dtypes
    assert tmp_projected_player_pts_path.exists() is False

    # Cleanup - none necessary


@pytest.fixture
def standard_scoring_factors():
    scoring_factors = {
        'Passing_Yards': lambda x: x / 25,  # 1 pt per 25 yds
        'Passing_Touchdowns': lambda x: x * 4,
        'Interceptions_Thrown': lambda x: x * -2,
        'Rushing_Yards': lambda x: x / 10,  # 1 pt per 10 yds
        'Rushing_Touchdowns': lambda x: x * 6,
        'Receptions': lambda x: x * 1,
        'Receiving_Yards': lambda x: x / 10,  # 1 pt per 10 yds
        'Receiving_Touchdowns': lambda x: x * 6,
        'Kickoff_and_Punt_Return_Touchdowns': lambda x: x * 6,
        'Fumble_Recovered_for_TD': lambda x: x * 6,
        '2-Point_Conversions': lambda x: x * 2,
        'Fumbles_Lost': lambda x: x * -2,
        'PAT_Made': lambda x: x * 1,
        'FG_Made_0-19': lambda x: x * 3,
        'FG_Made_20-29': lambda x: x * 3,
        'FG_Made_30-39': lambda x: x * 3,
        'FG_Made_40-49': lambda x: x * 3,
        'FG_Made_50+': lambda x: x * 5,
        'Sacks': lambda x: x * 1,
        'Interceptions': lambda x: x * 2,
        'Fumbles_Recovered': lambda x: x * 2,
        'Safeties': lambda x: x * 2,
        'Touchdowns': lambda x: x * 6,
        'Team_Kickoff_and_Punt_Return_Touchdowns': lambda x: x * 6,
        'Points_Allowed_0': lambda x: x * 10,
        'Points_Allowed_1-6': lambda x: x * 7,
        'Points_Allowed_7-13': lambda x: x * 4,
        'Points_Allowed_14-20': lambda x: x * 1,
        'Points_Allowed_21-27': lambda x: x * 0,
        'Points_Allowed_28-34': lambda x: x * -1,
        'Points_Allowed_35+': lambda x: x * -4,
    }
    return scoring_factors


def test_standard_scoring_factors_projected(standard_scoring_factors):
    """
    See https://support.nfl.com/hc/en-us/articles/4989179237404-Scoring

    Notes
    -----
    This test does not pull updated scores (i.e. it does not test
    whether or not the API and scoring has changed).
    It only tests an example for existing data (mostly a way to show how
    scores are calculated).
    """
    # Setup
    with open('assets/for_tests/mock_projected_player_pts.json') as f:
        projs_raw = json.load(f)

    projs_df = pd.DataFrame(projs_raw)
    projs = projs_df.filter(like='PROJ').rename(columns=lambda col: col.replace('PROJ_', ''))
    projs['Player'] = projs_df['Player']
    scoring_factors = standard_scoring_factors

    # cannot use df.apply() as some columns in scoring factors will not exist in df
    for col, eq in scoring_factors.items():
        if col in projs:
            projs[f'{col}_calc'] = projs[col].apply(eq)

    assert projs['pts'].equals(projs.filter(like='calc').sum(axis=1).round(2))


def test_standard_scoring_factors_actual(standard_scoring_factors):
    """
    See https://support.nfl.com/hc/en-us/articles/4989179237404-Scoring

    Notes
    -----
    This test does not pull updated scores (i.e. it does not test
    whether or not the API and scoring has changed).
    It only tests an example for existing data (mostly a way to show how
    scores are calculated).
    """
    # Setup
    with open('assets/for_tests/mock_actual_player_pts.json') as f:
        actuals_raw = json.load(f)

    actuals_df = pd.DataFrame(actuals_raw)
    actuals = actuals_df.filter(like='ACTUAL').rename(
        columns=lambda col: col.replace('ACTUAL_', '')
    )
    actuals['Player'] = actuals_df['Player']
    scoring_factors = standard_scoring_factors

    # cannot use df.apply() as some columns in scoring factors will not exist in df
    for col, eq in scoring_factors.items():
        if col in actuals:
            actuals[f'{col}_calc'] = actuals[col].apply(eq)

    assert actuals['pts'].equals(actuals.filter(like='calc').sum(axis=1).round(2))


@responses.activate
def test_create_player_pts_df_undocumented_players(tmp_path, caplog, mocker):
    # Setup
    caplog.set_level(logging.INFO)
    year = 2020
    week = 12

    tmp_archive_dir = tmp_path.joinpath('archive')
    tmp_archive_dir.mkdir()

    tmp_year_dir = tmp_archive_dir.joinpath(str(year))
    tmp_year_dir.mkdir()

    tmp_projected_player_pts_path = tmp_path.joinpath(f'{year}_{week}_projected_player_pts.csv')

    # Mock assets/player_ids.json
    # see https://www.freblogg.com/pytest-functions-mocking-1
    # mocked_player_ids = {
    #     'year': 2020,
    #     '2555260': {'name': 'Dak Prescott', 'position': 'QB', 'team': 'DAL', 'injury': None},
    #     '310': {'name': 'Matt Ryan', 'position': 'QB', 'team': 'IND', 'injury': None},
    #     '2504211': {'name': 'Tom Brady', 'position': 'QB', 'team': 'TB', 'injury': None},
    # }
    # mocker.patch('turkey_bowl.utils.load_from_json', return_value=mocked_player_ids)

    # These are "actual points"; pulled an a new previously undocumented player exists in this pull
    # that doesn't exist in the current player_ids.json nor projected_player_pts.csv
    undocumented_player_id = '123456789'  # fake pid for Logan Thomas

    player_ids_json_path = Path('assets/player_ids.json')
    current_player_ids = utils.load_from_json(player_ids_json_path)
    assert undocumented_player_id not in current_player_ids

    player_pts = {
        # "2555260": {
        #     "stats": {
        #         "week": {
        #             "2020": {
        #                 "12": {
        #                     "1": "1",
        #                     "5": "6.05",
        #                     "6": "0.03",
        #                     "7": "0.04",
        #                     "14": "0.06",
        #                     "30": "0.01",
        #                     "32": "0.02",
        #                     "pts": "0.31",
        #                 }
        #             }
        #         }
        #     }
        # },
        # "310": {
        #     "stats": {
        #         "week": {
        #             "2020": {
        #                 "12": {
        #                     "1": "1",
        #                     "5": "296.77",
        #                     "6": "1.94",
        #                     "7": "0.74",
        #                     "14": "9.99",
        #                     "15": "0.11",
        #                     "30": "0.09",
        #                     "32": "0.19",
        #                     "pts": "20.01",
        #                 }
        #             }
        #         }
        #     }
        # },
        # "2504211": {
        #     "stats": {
        #         "week": {
        #             "2020": {
        #                 "12": {
        #                     "1": "1",
        #                     "5": "16.93",
        #                     "6": "0.04",
        #                     "7": "0.06",
        #                     "15": "0.01",
        #                     "30": "0.01",
        #                     "32": "0.04",
        #                     "pts": "0.84",
        #                 }
        #             }
        #         }
        #     }
        # },
        # Undocumented Player (Logan Thomas)
        undocumented_player_id: {
            'stats': {
                'week': {
                    '2020': {
                        '12': {
                            '1': '1',
                            '5': '42.42',
                            '6': '0.42',
                            '7': '0.42',
                            '15': '0.42',
                            '30': '0.42',
                            '32': '0.42',
                            'pts': '0.42',
                        }
                    }
                }
            }
        },
    }

    # Mock undocumented player request
    url = f'https://api.fantasy.nfl.com/v2/player/ngs-content?playerId={undocumented_player_id}'
    request_json = {
        'games': {
            '102022': {
                'players': {
                    undocumented_player_id: {
                        'playerId': '2543767',
                        'nflGlobalEntityId': '32005448-4f29-6280-e212-928e7f08f1ce',
                        'esbId': 'THO296280',
                        'name': 'Logan Thomas',
                        'firstName': 'Logan',
                        'lastName': 'Thomas',
                        'position': 'TE',
                        'nflTeamAbbr': 'WAS',
                        'nflTeamId': '32',
                        'injuryGameStatus': None,
                        'imageUrl': 'https://static.www.nfl.com/image/private/w_200,h_200,c_fill/league/wzb0lbrvqknwfcgnj5sq',
                        'smallImageUrl': 'https://static.www.nfl.com/image/private/w_65,h_90,c_fill/league/wzb0lbrvqknwfcgnj5sq',
                        'largeImageUrl': 'https://static.www.nfl.com/image/private/w_1400,h_1000,c_fill/league/wzb0lbrvqknwfcgnj5sq',
                        'byeWeek': '14',
                        'cancelledWeeks': [],
                        'archetypes': [],
                        'isUndroppable': False,
                        'isReserveStatus': False,
                        'lastVideoTimestamp': '1969-12-31T16:00:00-08:00',
                    }
                }
            }
        }
    }
    responses.add(method=responses.GET, url=url, json=request_json, status=200)

    # Exercise
    _ = aggregate.create_player_pts_df(year, week, player_pts, tmp_projected_player_pts_path)

    # Verify
    updated_player_ids = utils.load_from_json(player_ids_json_path)
    assert undocumented_player_id in updated_player_ids
    del updated_player_ids[undocumented_player_id]
    utils.write_to_json(updated_player_ids, player_ids_json_path)

    assert f'Undocumented player {undocumented_player_id}: Logan Thomas' in caplog.text

    # Cleanup - none necessary


@pytest.fixture
def mock_participant_teams():
    participant_teams = {
        'Dodd': {
            'Position': {
                0: 'QB',
                1: 'RB_1',
                2: 'RB_2',
                3: 'WR_1',
                4: 'WR_2',
                5: 'TE',
                6: 'Flex (RB/WR/TE)',
                7: 'K',
                8: 'Defense (Team Name)',
                9: 'Bench (RB/WR/TE)',
            },
            'Player': {
                0: 'Josh Allen',
                1: 'David Montgomery',
                2: 'Tarik Cohen',
                3: 'Allen Robinson',
                4: 'Anthony Miller',
                5: 'Dawson Knox',
                6: 'Jared Cook',
                7: 'Cairo Santos',
                8: 'Chicago Bears',
                9: 'Latavius Murray',
            },
            'Team': {
                0: 'BUF',
                1: 'CHI',
                2: 'CHI',
                3: 'CHI',
                4: 'CHI',
                5: 'BUF',
                6: 'NO',
                7: 'CHI',
                8: 'CHI',
                9: 'NO',
            },
        },
        'Becca': {
            'Position': {
                0: 'QB',
                1: 'RB_1',
                2: 'RB_2',
                3: 'WR_1',
                4: 'WR_2',
                5: 'TE',
                6: 'Flex (RB/WR/TE)',
                7: 'K',
                8: 'Defense (Team Name)',
                9: 'Bench (RB/WR/TE)',
            },
            'Player': {
                0: 'Dak Prescott',
                1: 'Adrian Peterson',
                2: 'Kerryon Johnson',
                3: 'Marvin Jones',
                4: 'John Brown',
                5: 'T.J. Hockenson',
                6: 'Alvin Kamara',
                7: 'Matt Prater',
                8: 'Detroit Lions',
                9: 'Michael Gallup',
            },
            'Team': {
                0: 'DAL',
                1: 'DET',
                2: 'DET',
                3: 'DET',
                4: 'BUF',
                5: 'DET',
                6: 'NO',
                7: 'DET',
                8: 'DET',
                9: 'DAL',
            },
        },
        'Logan': {
            'Position': {
                0: 'QB',
                1: 'RB_1',
                2: 'RB_2',
                3: 'WR_1',
                4: 'WR_2',
                5: 'TE',
                6: 'Flex (RB/WR/TE)',
                7: 'K',
                8: 'Defense (Team Name)',
                9: 'Bench (RB/WR/TE)',
            },
            'Player': {
                0: 'Matt Ryan',
                1: "D'Andre Swift",
                2: 'Devin Singletary',
                3: 'Russell Gage',
                4: 'Amari Cooper',
                5: 'Jimmy Graham',
                6: 'Michael Thomas',
                7: 'Tyler Bass',
                8: 'Dallas Cowboys',
                9: 'Randall Cobb',
            },
            'Team': {
                0: 'IND',
                1: 'DET',
                2: 'BUF',
                3: 'ATL',
                4: 'DAL',
                5: 'CHI',
                6: 'NO',
                7: 'BUF',
                8: 'DAL',
                9: 'DAL',
            },
        },
    }

    participant_teams = {k: pd.DataFrame(v) for k, v in participant_teams.items()}

    pts_df_data = {
        'Player': {
            0: 'Josh Allen',
            1: 'David Montgomery',
            2: 'Tarik Cohen',
            3: 'Allen Robinson',
            4: 'Anthony Miller',
            5: 'Dawson Knox',
            6: 'Jared Cook',
            7: 'Cairo Santos',
            8: 'Chicago Bears',
            9: 'Latavius Murray',
            10: 'Dak Prescott',
            11: 'Adrian Peterson',
            12: 'Kerryon Johnson',
            13: 'Marvin Jones',
            14: 'John Brown',
            15: 'T.J. Hockenson',
            16: 'Alvin Kamara',
            17: 'Matt Prater',
            18: 'Detroit Lions',
            19: 'Michael Gallup',
            20: 'Matt Ryan',
            21: "D'Andre Swift",
            22: 'Devin Singletary',
            23: 'Russell Gage',
            24: 'Amari Cooper',
            25: 'Jimmy Graham',
            26: 'Michael Thomas',
            27: 'Tyler Bass',
            28: 'Dallas Cowboys',
            29: 'Randall Cobb',
        },
        'Team': {
            0: 'BUF',
            1: 'CHI',
            2: 'CHI',
            3: 'CHI',
            4: 'CHI',
            5: 'BUF',
            6: 'NO',
            7: 'CHI',
            8: 'CHI',
            9: 'NO',
            10: 'DAL',
            11: 'DET',
            12: 'DET',
            13: 'DET',
            14: 'BUF',
            15: 'DET',
            16: 'NO',
            17: 'DET',
            18: 'DET',
            19: 'DAL',
            20: 'IND',
            21: 'DET',
            22: 'BUF',
            23: 'ATL',
            24: 'DAL',
            25: 'CHI',
            26: 'NO',
            27: 'BUF',
            28: 'DAL',
            29: 'DAL',
        },
        'ACTUAL_pts': {
            0: 1.8499999999999999,
            1: 3.51,
            2: 84.19,
            3: 93.97,
            4: 31.31,
            5: 11.75,
            6: 96.39,
            7: 42.54,
            8: 19.580000000000002,
            9: 97.33000000000001,
            10: 21.2,
            11: 33.45,
            12: 59.5,
            13: 90.16999999999999,
            14: 47.29,
            15: 86.6,
            16: 47.05,
            17: 76.46,
            18: 95.21,
            19: 9.610000000000001,
            20: 69.14,
            21: 59.099999999999994,
            22: 42.93,
            23: 23.25,
            24: 59.699999999999996,
            25: 8.02,
            26: 72.6,
            27: 0.59,
            28: 19.759999999999998,
            29: 38.879999999999995,
        },
        'PROJ_pts': {
            0: 75.33999999999999,
            1: 49.830000000000005,
            2: 81.96,
            3: 24.04,
            4: 51.68000000000001,
            5: 87.45,
            6: 0.7100000000000001,
            7: 89.53999999999999,
            8: 3.7900000000000005,
            9: 72.98,
            10: 76.75,
            11: 19.85,
            12: 44.07,
            13: 52.7,
            14: 87.09,
            15: 40.11,
            16: 7.449999999999999,
            17: 31.680000000000003,
            18: 64.44,
            19: 59.489999999999995,
            20: 84.59,
            21: 86.03,
            22: 69.37,
            23: 44.800000000000004,
            24: 24.11,
            25: 80.84,
            26: 85.68,
            27: 46.989999999999995,
            28: 50.949999999999996,
            29: 36.35,
        },
    }

    pts_df = pd.DataFrame(pts_df_data)

    return participant_teams, pts_df


def test_merge_points(mock_participant_teams):
    # Setup
    participant_teams, pts_df = mock_participant_teams
    pts_df['drop_me'] = 0.0

    # Exercise
    participant_teams = aggregate.merge_points(participant_teams, pts_df, verbose=False)

    # Verify
    assert participant_teams['Dodd']['ACTUAL_pts'].equals(pts_df[:10]['ACTUAL_pts'])
    assert participant_teams['Dodd']['PROJ_pts'].equals(pts_df[:10]['PROJ_pts'])
    assert 'drop_me' not in participant_teams['Dodd'].columns

    assert participant_teams['Becca']['ACTUAL_pts'].equals(
        pts_df[10:20]['ACTUAL_pts'].reset_index(drop=True)
    )
    assert participant_teams['Becca']['PROJ_pts'].equals(
        pts_df[10:20]['PROJ_pts'].reset_index(drop=True)
    )
    assert 'drop_me' not in participant_teams['Becca'].columns

    assert participant_teams['Logan']['ACTUAL_pts'].equals(
        pts_df[20:]['ACTUAL_pts'].reset_index(drop=True)
    )
    assert participant_teams['Logan']['PROJ_pts'].equals(
        pts_df[20:]['PROJ_pts'].reset_index(drop=True)
    )
    assert 'drop_me' not in participant_teams['Logan'].columns

    # Cleanup - none necessary


def test_merge_points_prints_warning_if_player_not_found(mock_participant_teams, caplog):
    # Setup
    caplog.set_level(logging.INFO)
    participant_teams, pts_df = mock_participant_teams

    # Intentional misspell
    participant_teams['Dodd'].loc[0, 'Player'] = 'Josh Alle'
    participant_teams['Becca'].loc[0, 'Player'] = 'Dak Prescot'
    participant_teams['Logan'].loc[0, 'Player'] = 'Matt Rya'

    pts_df['drop_me'] = 0.0

    # Exercise
    participant_teams = aggregate.merge_points(participant_teams, pts_df, verbose=True)

    # Verify
    assert "WARNING: Dodd has players with NaN values: ['Josh Alle']" in caplog.text
    assert "WARNING: Becca has players with NaN values: ['Dak Prescot']" in caplog.text
    assert "WARNING: Logan has players with NaN values: ['Matt Rya']" in caplog.text

    # Cleanup - none necessary


def test_sort_robust_cols(mock_participant_teams):
    # Setup
    participant_teams, _ = mock_participant_teams
    for participant_team in participant_teams.values():
        # Intentionally group PROJ first and ACTUAL second (test sort order)
        participant_team['PROJ_pts'] = 0.0
        participant_team['ACTUAL_pts'] = 0.0
        participant_team['PROJ_A'] = 0.0
        participant_team['PROJ_B'] = 0.0
        participant_team['PROJ_C'] = 0.0
        participant_team['ACTUAL_A'] = 0.0
        participant_team['ACTUAL_B'] = 0.0
        participant_team['ACTUAL_Z'] = 0.0

    # Exercise
    result = aggregate.sort_robust_cols(participant_teams)

    # Verify
    assert list(result.keys()) == ['Dodd', 'Becca', 'Logan']

    for participant_team in participant_teams.values():
        assert list(participant_team.columns) == [
            'Position',
            'Player',
            'Team',
            'ACTUAL_pts',
            'PROJ_pts',
            'ACTUAL_A',
            'PROJ_A',
            'ACTUAL_B',
            'PROJ_B',
            'PROJ_C',
            'ACTUAL_Z',
        ]

    # Cleanup - none necessary


def test_write_robust_participant_team_scores(mock_participant_teams, tmp_path, caplog):
    # Setup
    caplog.set_level(logging.INFO)
    year = 2020
    week = 12

    tmp_archive_dir = tmp_path.joinpath('archive')
    tmp_archive_dir.mkdir()

    tmp_year_dir = tmp_archive_dir.joinpath(str(year))
    tmp_year_dir.mkdir()

    tmp_robust_participant_player_pts_path = tmp_path.joinpath(
        f'{year}_{week}_robust_participant_player_pts.xlsx'
    )

    participant_teams, _ = mock_participant_teams
    for participant_team in participant_teams.values():
        # Intentionally group PROJ first and ACTUAL second (test sort order)
        participant_team['PROJ_pts'] = 0.0
        participant_team['ACTUAL_pts'] = 0.0
        participant_team['PROJ_A'] = 0.0
        participant_team['PROJ_B'] = 0.0
        participant_team['PROJ_C'] = 0.0
        participant_team['ACTUAL_A'] = 0.0
        participant_team['ACTUAL_B'] = 0.0
        participant_team['ACTUAL_Z'] = 0.0

    expected_out = (
        f'Writing robust player points summary to {tmp_robust_participant_player_pts_path}...'
    )

    # Exercise
    assert tmp_robust_participant_player_pts_path.exists() is False
    aggregate.write_robust_participant_team_scores(
        participant_teams, tmp_robust_participant_player_pts_path
    )

    # Verify
    assert tmp_robust_participant_player_pts_path.exists()
    written = pd.read_excel(tmp_robust_participant_player_pts_path, sheet_name=None)

    expected_dtypes = {
        'Position': np.dtype('O'),
        'Player': np.dtype('O'),
        'Team': np.dtype('O'),
        'PROJ_pts': np.dtype('float64'),
        'ACTUAL_pts': np.dtype('float64'),
        'PROJ_A': np.dtype('float64'),
        'PROJ_B': np.dtype('float64'),
        'PROJ_C': np.dtype('float64'),
        'ACTUAL_A': np.dtype('float64'),
        'ACTUAL_B': np.dtype('float64'),
        'ACTUAL_Z': np.dtype('float64'),
    }

    for participant, participant_team in written.items():
        participant_team = participant_team.astype(expected_dtypes)
        assert participant_teams[participant].equals(participant_team)

    assert expected_out in caplog.text

    # Cleanup - none necessary
