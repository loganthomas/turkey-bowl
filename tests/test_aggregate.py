"""
Unit tests for aggregate.py
"""
# Third-party libraries
import numpy as np
import pandas as pd
import pytest

# Local libraries
import aggregate


@pytest.fixture
def mock_proj_player_pts():
    player_pts = {
        "2504211": {
            "projectedStats": {
                "week": {
                    "2020": {
                        "12": {
                            "1": "1",
                            "14": "0.05",
                            "20": "1.1",
                            "21": "13.11",
                            "22": "0.09",
                            "pts": "2.96",
                        }
                    }
                }
            }
        },
        "310": {
            "projectedStats": {
                "week": {
                    "2020": {
                        "12": {
                            "1": "1",
                            "14": "5.5",
                            "20": "3.3",
                            "21": "17.11",
                            "22": "0.07",
                            "pts": "9.96",
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
        "2504211": {
            "stats": {
                "week": {
                    "2020": {
                        "12": {
                            "1": "1",
                            "14": "0.05",
                            "20": "1.1",
                            "21": "13.11",
                            "22": "0.09",
                            "pts": "2.96",
                        }
                    }
                }
            }
        },
        "310": {
            "stats": {
                "week": {
                    "2020": {
                        "12": {
                            "1": "1",
                            "14": "5.5",
                            "20": "3.3",
                            "21": "17.11",
                            "22": "0.07",
                            "pts": "9.96",
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
        "2504211": proj_player_pts["2504211"],
        "310": actual_player_pts["310"],
    }

    expected_error1 = (
        "More than one unique stats type detected: {'stats', 'projectedStats'}"
    )
    expected_error2 = (
        "More than one unique stats type detected: {'projectedStats', 'stats'}"
    )
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
        "2504211": {
            "bad_stats": {
                "week": {
                    "2020": {
                        "12": {
                            "1": "1",
                            "14": "0.05",
                            "20": "1.1",
                            "21": "13.11",
                            "22": "0.09",
                            "pts": "2.96",
                        }
                    }
                }
            }
        },
        "310": {
            "bad_stats": {
                "week": {
                    "2020": {
                        "12": {
                            "1": "1",
                            "14": "5.5",
                            "20": "3.3",
                            "21": "17.11",
                            "22": "0.07",
                            "pts": "9.96",
                        }
                    }
                }
            }
        },
    }

    expected_error = "Unrecognized stats type: 'bad_stats'. Expected either 'projectedStats' or 'stats'."
    # Exercise
    with pytest.raises(ValueError) as error_info:
        aggregate._get_player_pts_stat_type(player_pts)

    # Verify
    assert str(error_info.value) == expected_error

    # Verify

    # Cleanup - none necessary


@pytest.mark.parametrize(
    "stat_type", ["projectedStats", "stats"], ids=["projected", "actual"]
)
def test__get_player_pts_stats_type(
    stat_type, mock_proj_player_pts, mock_actual_player_pts
):
    # Setup
    if stat_type == "projectedStats":
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
        "stats": {
            "week": {
                str(year): {
                    str(week): {
                        "1": "1",
                        "14": "0.05",
                        "20": "1.1",
                        "21": "13.11",
                        "22": "0.09",
                        "pts": "2.96",
                    }
                }
            }
        }
    }

    expected = {
        "1": "1",
        "14": "0.05",
        "20": "1.1",
        "21": "13.11",
        "22": "0.09",
        "pts": "2.96",
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
        "252": {"projectedStats": {}},
        "310": {"projectedStats": {}},
        "382": {"projectedStats": {}},
    }

    expected_error = "When creating a projected player points dataframe, ``savepath`` must be specified."

    # Exercise
    with pytest.raises(ValueError) as error_info:
        aggregate.create_player_pts_df(year, week, player_pts)

    # Verify
    assert str(error_info.value) == expected_error

    # Cleanup - none necessary


def test_create_player_pts_df_projected_already_exists(tmp_path, capsys):
    # Setup
    year = 2020
    week = 12

    tmp_archive_dir = tmp_path.joinpath("archive")
    tmp_archive_dir.mkdir()

    tmp_year_dir = tmp_archive_dir.joinpath(str(year))
    tmp_year_dir.mkdir()

    tmp_projected_player_pts_path = tmp_path.joinpath(
        f"{year}_{week}_projected_player_pts.csv"
    )

    player_pts = {
        "252": {"projectedStats": {}},
        "310": {"projectedStats": {}},
        "382": {"projectedStats": {}},
    }

    player_pts_df_data = {
        "Player": {0: "Chad Henne", 1: "Matt Ryan", 2: "Joe Flacco"},
        "Team": {0: "KC", 1: "ATL", 2: "NYJ"},
        "PROJ_pts": {0: 0.31, 1: 20.01, 2: 0.84},
        "PROJ_Games_Played": {0: 1, 1: 1, 2: 1},
        "PROJ_Passing_Yards": {0: 6.05, 1: 296.77, 2: 16.93},
        "PROJ_Passing_Touchdowns": {0: 0.03, 1: 1.94, 2: 0.04},
        "PROJ_Interceptions_Thrown": {0: 0.04, 1: 0.74, 2: 0.06},
        "PROJ_Rushing_Yards": {0: 0.06, 1: 9.99, 2: np.nan},
        "PROJ_Fumbles_Lost": {0: 0.01, 1: 0.09, 2: 0.01},
        "PROJ_2-Point_Conversions": {0: 0.02, 1: 0.19, 2: 0.04},
        "PROJ_Rushing_Touchdowns": {0: np.nan, 1: 0.11, 2: 0.01},
        "PROJ_Tackle": {0: np.nan, 1: np.nan, 2: np.nan},
        "PROJ_Assisted_Tackles": {0: np.nan, 1: np.nan, 2: np.nan},
        "PROJ_Sack": {0: np.nan, 1: np.nan, 2: np.nan},
        "PROJ_Defense_Interception": {0: np.nan, 1: np.nan, 2: np.nan},
        "PROJ_Forced_Fumble": {0: np.nan, 1: np.nan, 2: np.nan},
        "PROJ_Fumbles_Recovery": {0: np.nan, 1: np.nan, 2: np.nan},
        "PROJ_Blocked_Kick_(punt,_FG,_PAT)": {0: np.nan, 1: np.nan, 2: np.nan},
        "PROJ_Pass_Defended": {0: np.nan, 1: np.nan, 2: np.nan},
        "PROJ_Receptions": {0: np.nan, 1: np.nan, 2: np.nan},
        "PROJ_Receiving_Yards": {0: np.nan, 1: np.nan, 2: np.nan},
        "PROJ_Receiving_Touchdowns": {0: np.nan, 1: np.nan, 2: np.nan},
        "PROJ_PAT_Made": {0: np.nan, 1: np.nan, 2: np.nan},
        "PROJ_FG_Made_0-19": {0: np.nan, 1: np.nan, 2: np.nan},
        "PROJ_FG_Made_20-29": {0: np.nan, 1: np.nan, 2: np.nan},
        "PROJ_FG_Made_30-39": {0: np.nan, 1: np.nan, 2: np.nan},
        "PROJ_FG_Made_40-49": {0: np.nan, 1: np.nan, 2: np.nan},
        "PROJ_FG_Missed_50+": {0: np.nan, 1: np.nan, 2: np.nan},
        "PROJ_Sacks": {0: np.nan, 1: np.nan, 2: np.nan},
        "PROJ_Interceptions": {0: np.nan, 1: np.nan, 2: np.nan},
        "PROJ_Fumbles_Recovered": {0: np.nan, 1: np.nan, 2: np.nan},
        "PROJ_Safeties": {0: np.nan, 1: np.nan, 2: np.nan},
        "PROJ_Touchdowns": {0: np.nan, 1: np.nan, 2: np.nan},
        "PROJ_Blocked_Kicks": {0: np.nan, 1: np.nan, 2: np.nan},
        "PROJ_Kickoff_and_Punt_Return_Touchdowns": {0: np.nan, 1: np.nan, 2: np.nan},
        "PROJ_Points_Allowed": {0: np.nan, 1: np.nan, 2: np.nan},
        "PROJ_Safety": {0: np.nan, 1: np.nan, 2: np.nan},
        "PROJ_Kickoff_and_Punt_Return_Touchdowns.1": {0: np.nan, 1: np.nan, 2: np.nan},
    }

    player_pts_df = pd.DataFrame(player_pts_df_data)
    player_pts_df = player_pts_df.fillna(0.0)
    player_pts_df.to_csv(tmp_projected_player_pts_path)

    expected_dtypes = {
        "Player": np.dtype("O"),
        "Team": np.dtype("O"),
        "PROJ_pts": np.dtype("float64"),
        "PROJ_Games_Played": np.dtype("int64"),
        "PROJ_Passing_Yards": np.dtype("float64"),
        "PROJ_Passing_Touchdowns": np.dtype("float64"),
        "PROJ_Interceptions_Thrown": np.dtype("float64"),
        "PROJ_Rushing_Yards": np.dtype("float64"),
        "PROJ_Fumbles_Lost": np.dtype("float64"),
        "PROJ_2-Point_Conversions": np.dtype("float64"),
        "PROJ_Rushing_Touchdowns": np.dtype("float64"),
        "PROJ_Tackle": np.dtype("float64"),
        "PROJ_Assisted_Tackles": np.dtype("float64"),
        "PROJ_Sack": np.dtype("float64"),
        "PROJ_Defense_Interception": np.dtype("float64"),
        "PROJ_Forced_Fumble": np.dtype("float64"),
        "PROJ_Fumbles_Recovery": np.dtype("float64"),
        "PROJ_Blocked_Kick_(punt,_FG,_PAT)": np.dtype("float64"),
        "PROJ_Pass_Defended": np.dtype("float64"),
        "PROJ_Receptions": np.dtype("float64"),
        "PROJ_Receiving_Yards": np.dtype("float64"),
        "PROJ_Receiving_Touchdowns": np.dtype("float64"),
        "PROJ_PAT_Made": np.dtype("float64"),
        "PROJ_FG_Made_0-19": np.dtype("float64"),
        "PROJ_FG_Made_20-29": np.dtype("float64"),
        "PROJ_FG_Made_30-39": np.dtype("float64"),
        "PROJ_FG_Made_40-49": np.dtype("float64"),
        "PROJ_FG_Missed_50+": np.dtype("float64"),
        "PROJ_Sacks": np.dtype("float64"),
        "PROJ_Interceptions": np.dtype("float64"),
        "PROJ_Fumbles_Recovered": np.dtype("float64"),
        "PROJ_Safeties": np.dtype("float64"),
        "PROJ_Touchdowns": np.dtype("float64"),
        "PROJ_Blocked_Kicks": np.dtype("float64"),
        "PROJ_Kickoff_and_Punt_Return_Touchdowns": np.dtype("float64"),
        "PROJ_Points_Allowed": np.dtype("float64"),
        "PROJ_Safety": np.dtype("float64"),
        "PROJ_Kickoff_and_Punt_Return_Touchdowns.1": np.dtype("float64"),
    }

    # Exercise
    assert tmp_projected_player_pts_path.exists() is True
    result = aggregate.create_player_pts_df(
        year, week, player_pts, tmp_projected_player_pts_path
    )

    # Verify
    assert result.equals(player_pts_df)
    assert result.isnull().sum().sum() == 0
    assert result.dtypes.to_dict() == expected_dtypes

    captured = capsys.readouterr()
    assert (
        captured.out
        == f"Projected player data already exists at: {tmp_projected_player_pts_path}\n"
    )

    # Cleanup - none necessary


def test_create_player_pts_df_projected_doesnt_exists(tmp_path, capsys):
    # Setup
    year = 2020
    week = 12

    tmp_archive_dir = tmp_path.joinpath("archive")
    tmp_archive_dir.mkdir()

    tmp_year_dir = tmp_archive_dir.joinpath(str(year))
    tmp_year_dir.mkdir()

    tmp_projected_player_pts_path = tmp_path.joinpath(
        f"{year}_{week}_projected_player_pts.csv"
    )

    player_pts = {
        "252": {
            "projectedStats": {
                "week": {
                    "2020": {
                        "12": {
                            "1": "1",
                            "5": "6.05",
                            "6": "0.03",
                            "7": "0.04",
                            "14": "0.06",
                            "30": "0.01",
                            "32": "0.02",
                            "pts": "0.31",
                        }
                    }
                }
            }
        },
        "310": {
            "projectedStats": {
                "week": {
                    "2020": {
                        "12": {
                            "1": "1",
                            "5": "296.77",
                            "6": "1.94",
                            "7": "0.74",
                            "14": "9.99",
                            "15": "0.11",
                            "30": "0.09",
                            "32": "0.19",
                            "pts": "20.01",
                        }
                    }
                }
            }
        },
        "382": {
            "projectedStats": {
                "week": {
                    "2020": {
                        "12": {
                            "1": "1",
                            "5": "16.93",
                            "6": "0.04",
                            "7": "0.06",
                            "15": "0.01",
                            "30": "0.01",
                            "32": "0.04",
                            "pts": "0.84",
                        }
                    }
                }
            }
        },
    }

    player_pts_df_data = {
        "Player": {0: "Chad Henne", 1: "Matt Ryan", 2: "Joe Flacco"},
        "Team": {0: "KC", 1: "ATL", 2: "NYJ"},
        "PROJ_pts": {0: 0.31, 1: 20.01, 2: 0.84},
        "PROJ_Games_Played": {0: 1.0, 1.0: 1.0, 2: 1.0},
        "PROJ_Passing_Yards": {0: 6.05, 1: 296.77, 2: 16.93},
        "PROJ_Passing_Touchdowns": {0: 0.03, 1: 1.94, 2: 0.04},
        "PROJ_Interceptions_Thrown": {0: 0.04, 1: 0.74, 2: 0.06},
        "PROJ_Rushing_Yards": {0: 0.06, 1: 9.99, 2: np.nan},
        "PROJ_Fumbles_Lost": {0: 0.01, 1: 0.09, 2: 0.01},
        "PROJ_2-Point_Conversions": {0: 0.02, 1: 0.19, 2: 0.04},
        "PROJ_Rushing_Touchdowns": {0: np.nan, 1: 0.11, 2: 0.01},
    }

    expected = pd.DataFrame(player_pts_df_data)
    expected = expected.fillna(0.0)
    expected_dtypes = {
        "Player": np.dtype("O"),
        "Team": np.dtype("O"),
        "PROJ_pts": np.dtype("float64"),
        "PROJ_Games_Played": np.dtype("float64"),
        "PROJ_Passing_Yards": np.dtype("float64"),
        "PROJ_Passing_Touchdowns": np.dtype("float64"),
        "PROJ_Interceptions_Thrown": np.dtype("float64"),
        "PROJ_Rushing_Yards": np.dtype("float64"),
        "PROJ_Fumbles_Lost": np.dtype("float64"),
        "PROJ_2-Point_Conversions": np.dtype("float64"),
        "PROJ_Rushing_Touchdowns": np.dtype("float64"),
    }

    # Exercise
    assert tmp_projected_player_pts_path.exists() is False
    result = aggregate.create_player_pts_df(
        year, week, player_pts, tmp_projected_player_pts_path
    )
    result_written = pd.read_csv(tmp_projected_player_pts_path, index_col=0)

    # Verify
    assert result.equals(expected)
    assert result_written.equals(expected)
    assert result.equals(result_written)
    assert result.isnull().sum().sum() == 0
    assert result.dtypes.to_dict() == expected_dtypes

    captured = capsys.readouterr()
    assert (
        captured.out
        == f"\nWriting projected player stats to: {tmp_projected_player_pts_path}...\n"
    )

    # Cleanup - none necessary


def test_create_player_pts_df_actual(tmp_path):
    # Setup
    year = 2020
    week = 12

    tmp_archive_dir = tmp_path.joinpath("archive")
    tmp_archive_dir.mkdir()

    tmp_year_dir = tmp_archive_dir.joinpath(str(year))
    tmp_year_dir.mkdir()

    tmp_projected_player_pts_path = tmp_path.joinpath(
        f"{year}_{week}_projected_player_pts.csv"
    )

    player_pts = {
        "252": {
            "stats": {
                "week": {
                    "2020": {
                        "12": {
                            "1": "1",
                            "5": "6.05",
                            "6": "0.03",
                            "7": "0.04",
                            "14": "0.06",
                            "30": "0.01",
                            "32": "0.02",
                            "pts": "0.31",
                        }
                    }
                }
            }
        },
        "310": {
            "stats": {
                "week": {
                    "2020": {
                        "12": {
                            "1": "1",
                            "5": "296.77",
                            "6": "1.94",
                            "7": "0.74",
                            "14": "9.99",
                            "15": "0.11",
                            "30": "0.09",
                            "32": "0.19",
                            "pts": "20.01",
                        }
                    }
                }
            }
        },
        "382": {
            "stats": {
                "week": {
                    "2020": {
                        "12": {
                            "1": "1",
                            "5": "16.93",
                            "6": "0.04",
                            "7": "0.06",
                            "15": "0.01",
                            "30": "0.01",
                            "32": "0.04",
                            "pts": "0.84",
                        }
                    }
                }
            }
        },
    }

    player_pts_df_data = {
        "Player": {0: "Chad Henne", 1: "Matt Ryan", 2: "Joe Flacco"},
        "Team": {0: "KC", 1: "ATL", 2: "NYJ"},
        "ACTUAL_pts": {0: 0.31, 1: 20.01, 2: 0.84},
        "ACTUAL_Games_Played": {0: 1.0, 1.0: 1.0, 2: 1.0},
        "ACTUAL_Passing_Yards": {0: 6.05, 1: 296.77, 2: 16.93},
        "ACTUAL_Passing_Touchdowns": {0: 0.03, 1: 1.94, 2: 0.04},
        "ACTUAL_Interceptions_Thrown": {0: 0.04, 1: 0.74, 2: 0.06},
        "ACTUAL_Rushing_Yards": {0: 0.06, 1: 9.99, 2: np.nan},
        "ACTUAL_Fumbles_Lost": {0: 0.01, 1: 0.09, 2: 0.01},
        "ACTUAL_2-Point_Conversions": {0: 0.02, 1: 0.19, 2: 0.04},
        "ACTUAL_Rushing_Touchdowns": {0: np.nan, 1: 0.11, 2: 0.01},
    }

    expected = pd.DataFrame(player_pts_df_data)
    expected = expected.fillna(0.0)
    expected_dtypes = {
        "Player": np.dtype("O"),
        "Team": np.dtype("O"),
        "ACTUAL_pts": np.dtype("float64"),
        "ACTUAL_Games_Played": np.dtype("float64"),
        "ACTUAL_Passing_Yards": np.dtype("float64"),
        "ACTUAL_Passing_Touchdowns": np.dtype("float64"),
        "ACTUAL_Interceptions_Thrown": np.dtype("float64"),
        "ACTUAL_Rushing_Yards": np.dtype("float64"),
        "ACTUAL_Fumbles_Lost": np.dtype("float64"),
        "ACTUAL_2-Point_Conversions": np.dtype("float64"),
        "ACTUAL_Rushing_Touchdowns": np.dtype("float64"),
    }

    # Exercise
    assert tmp_projected_player_pts_path.exists() is False
    result = aggregate.create_player_pts_df(
        year, week, player_pts, tmp_projected_player_pts_path
    )

    # Verify
    assert result.equals(expected)
    assert result.isnull().sum().sum() == 0
    assert result.dtypes.to_dict() == expected_dtypes
    assert tmp_projected_player_pts_path.exists() is False

    # Cleanup - none necessary


@pytest.fixture
def mock_participant_teams():
    participant_teams = {
        "Dodd": {
            "Position": {
                0: "QB",
                1: "RB_1",
                2: "RB_2",
                3: "WR_1",
                4: "WR_2",
                5: "TE",
                6: "Flex (RB/WR/TE)",
                7: "K",
                8: "Defense (Team Name)",
                9: "Bench (RB/WR/TE)",
            },
            "Player": {
                0: "Josh Allen",
                1: "David Montgomery",
                2: "Tarik Cohen",
                3: "Allen Robinson",
                4: "Anthony Miller",
                5: "Dawson Knox",
                6: "Jared Cook",
                7: "Cairo Santos",
                8: "Chicago Bears",
                9: "Latavius Murray",
            },
            "Team": {
                0: "BUF",
                1: "CHI",
                2: "CHI",
                3: "CHI",
                4: "CHI",
                5: "BUF",
                6: "NO",
                7: "CHI",
                8: "CHI",
                9: "NO",
            },
        },
        "Becca": {
            "Position": {
                0: "QB",
                1: "RB_1",
                2: "RB_2",
                3: "WR_1",
                4: "WR_2",
                5: "TE",
                6: "Flex (RB/WR/TE)",
                7: "K",
                8: "Defense (Team Name)",
                9: "Bench (RB/WR/TE)",
            },
            "Player": {
                0: "Dak Prescott",
                1: "Adrian Peterson",
                2: "Kerryon Johnson",
                3: "Marvin Jones",
                4: "John Brown",
                5: "T.J. Hockenson",
                6: "Alvin Kamara",
                7: "Matt Prater",
                8: "Detroit Lions",
                9: "Michael Gallup",
            },
            "Team": {
                0: "DAL",
                1: "DET",
                2: "DET",
                3: "DET",
                4: "BUF",
                5: "DET",
                6: "NO",
                7: "DET",
                8: "DET",
                9: "DAL",
            },
        },
        "Logan": {
            "Position": {
                0: "QB",
                1: "RB_1",
                2: "RB_2",
                3: "WR_1",
                4: "WR_2",
                5: "TE",
                6: "Flex (RB/WR/TE)",
                7: "K",
                8: "Defense (Team Name)",
                9: "Bench (RB/WR/TE)",
            },
            "Player": {
                0: "Matt Ryan",
                1: "D'Andre Swift",
                2: "Devin Singletary",
                3: "Russell Gage",
                4: "Amari Cooper",
                5: "Jimmy Graham",
                6: "Michael Thomas",
                7: "Tyler Bass",
                8: "Dallas Cowboys",
                9: "Randall Cobb",
            },
            "Team": {
                0: "ATL",
                1: "DET",
                2: "BUF",
                3: "ATL",
                4: "DAL",
                5: "CHI",
                6: "NO",
                7: "BUF",
                8: "DAL",
                9: "DAL",
            },
        },
    }

    participant_teams = {k: pd.DataFrame(v) for k, v in participant_teams.items()}

    pts_df_data = {
        "Player": {
            0: "Josh Allen",
            1: "David Montgomery",
            2: "Tarik Cohen",
            3: "Allen Robinson",
            4: "Anthony Miller",
            5: "Dawson Knox",
            6: "Jared Cook",
            7: "Cairo Santos",
            8: "Chicago Bears",
            9: "Latavius Murray",
            10: "Dak Prescott",
            11: "Adrian Peterson",
            12: "Kerryon Johnson",
            13: "Marvin Jones",
            14: "John Brown",
            15: "T.J. Hockenson",
            16: "Alvin Kamara",
            17: "Matt Prater",
            18: "Detroit Lions",
            19: "Michael Gallup",
            20: "Matt Ryan",
            21: "D'Andre Swift",
            22: "Devin Singletary",
            23: "Russell Gage",
            24: "Amari Cooper",
            25: "Jimmy Graham",
            26: "Michael Thomas",
            27: "Tyler Bass",
            28: "Dallas Cowboys",
            29: "Randall Cobb",
        },
        "Team": {
            0: "BUF",
            1: "CHI",
            2: "CHI",
            3: "CHI",
            4: "CHI",
            5: "BUF",
            6: "NO",
            7: "CHI",
            8: "CHI",
            9: "NO",
            10: "DAL",
            11: "DET",
            12: "DET",
            13: "DET",
            14: "BUF",
            15: "DET",
            16: "NO",
            17: "DET",
            18: "DET",
            19: "DAL",
            20: "ATL",
            21: "DET",
            22: "BUF",
            23: "ATL",
            24: "DAL",
            25: "CHI",
            26: "NO",
            27: "BUF",
            28: "DAL",
            29: "DAL",
        },
        "ACTUAL_pts": {
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
        "PROJ_pts": {
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
    pts_df["drop_me"] = 0.0

    # Exercise
    participant_teams = aggregate.merge_points(participant_teams, pts_df)

    # Verify
    assert participant_teams["Dodd"]["ACTUAL_pts"].equals(pts_df[:10]["ACTUAL_pts"])
    assert participant_teams["Dodd"]["PROJ_pts"].equals(pts_df[:10]["PROJ_pts"])
    assert "drop_me" not in participant_teams["Dodd"].columns

    assert participant_teams["Becca"]["ACTUAL_pts"].equals(
        pts_df[10:20]["ACTUAL_pts"].reset_index(drop=True)
    )
    assert participant_teams["Becca"]["PROJ_pts"].equals(
        pts_df[10:20]["PROJ_pts"].reset_index(drop=True)
    )
    assert "drop_me" not in participant_teams["Becca"].columns

    assert participant_teams["Logan"]["ACTUAL_pts"].equals(
        pts_df[20:]["ACTUAL_pts"].reset_index(drop=True)
    )
    assert participant_teams["Logan"]["PROJ_pts"].equals(
        pts_df[20:]["PROJ_pts"].reset_index(drop=True)
    )
    assert "drop_me" not in participant_teams["Logan"].columns

    # Cleanup - none necessary


def test_merge_points_prints_warning_if_player_not_found(
    mock_participant_teams, capsys
):
    # Setup
    participant_teams, pts_df = mock_participant_teams

    # Intentional misspell
    participant_teams["Dodd"].loc[0, "Player"] = "Josh Alle"
    participant_teams["Becca"].loc[0, "Player"] = "Dak Prescot"
    participant_teams["Logan"].loc[0, "Player"] = "Matt Rya"

    pts_df["drop_me"] = 0.0

    expected_warning = (
        "WARNING: Dodd has missing players: ['Josh Alle']\n"
        + "WARNING: Becca has missing players: ['Dak Prescot']\n"
        + "WARNING: Logan has missing players: ['Matt Rya']\n"
    )

    # Exercise
    participant_teams = aggregate.merge_points(participant_teams, pts_df)

    # Verify
    captured = capsys.readouterr()
    assert captured.out == expected_warning

    # Cleanup - none necessary


def test_sort_robust_cols(mock_participant_teams):
    # Setup
    participant_teams, _ = mock_participant_teams
    for participant_team in participant_teams.values():

        # Intentionally group PROJ first and ACTUAL second (test sort order)
        participant_team["PROJ_pts"] = 0.0
        participant_team["ACTUAL_pts"] = 0.0
        participant_team["PROJ_A"] = 0.0
        participant_team["PROJ_B"] = 0.0
        participant_team["PROJ_C"] = 0.0
        participant_team["ACTUAL_A"] = 0.0
        participant_team["ACTUAL_B"] = 0.0
        participant_team["ACTUAL_Z"] = 0.0

    # Exercise
    result = aggregate.sort_robust_cols(participant_teams)

    # Verify
    assert list(result.keys()) == ["Dodd", "Becca", "Logan"]

    for participant_team in participant_teams.values():
        assert list(participant_team.columns) == [
            "Position",
            "Player",
            "Team",
            "ACTUAL_pts",
            "PROJ_pts",
            "ACTUAL_A",
            "PROJ_A",
            "ACTUAL_B",
            "PROJ_B",
            "PROJ_C",
            "ACTUAL_Z",
        ]

    # Cleanup - none necessary


def test_write_robust_pariticipant_team_scores(
    mock_participant_teams, tmp_path, capsys
):
    # Setup
    year = 2020
    week = 12

    tmp_archive_dir = tmp_path.joinpath("archive")
    tmp_archive_dir.mkdir()

    tmp_year_dir = tmp_archive_dir.joinpath(str(year))
    tmp_year_dir.mkdir()

    tmp_robust_participant_player_pts_path = tmp_path.joinpath(
        f"{year}_{week}_robust_participant_player_pts.xlsx"
    )

    participant_teams, _ = mock_participant_teams
    for participant_team in participant_teams.values():

        # Intentionally group PROJ first and ACTUAL second (test sort order)
        participant_team["PROJ_pts"] = 0.0
        participant_team["ACTUAL_pts"] = 0.0
        participant_team["PROJ_A"] = 0.0
        participant_team["PROJ_B"] = 0.0
        participant_team["PROJ_C"] = 0.0
        participant_team["ACTUAL_A"] = 0.0
        participant_team["ACTUAL_B"] = 0.0
        participant_team["ACTUAL_Z"] = 0.0

    expected_out = (
        "\nWriting robust player points summary to: "
        + f"{tmp_robust_participant_player_pts_path}...\n"
    )

    # Exercise
    assert tmp_robust_participant_player_pts_path.exists() is False
    aggregate.write_robust_participant_team_scores(
        year, week, participant_teams, tmp_robust_participant_player_pts_path
    )

    # Verify
    assert tmp_robust_participant_player_pts_path.exists()
    written = pd.read_excel(tmp_robust_participant_player_pts_path, sheet_name=None)

    expected_dtypes = {
        "Position": np.dtype("O"),
        "Player": np.dtype("O"),
        "Team": np.dtype("O"),
        "PROJ_pts": np.dtype("float64"),
        "ACTUAL_pts": np.dtype("float64"),
        "PROJ_A": np.dtype("float64"),
        "PROJ_B": np.dtype("float64"),
        "PROJ_C": np.dtype("float64"),
        "ACTUAL_A": np.dtype("float64"),
        "ACTUAL_B": np.dtype("float64"),
        "ACTUAL_Z": np.dtype("float64"),
    }

    for participant, participant_team in written.items():
        participant_team = participant_team.astype(expected_dtypes)
        assert participant_teams[participant].equals(participant_team)

    captured = capsys.readouterr()
    assert captured.out == expected_out

    # Cleanup - none necessary
