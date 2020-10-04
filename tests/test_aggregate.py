# Third-party libraries
import numpy as np
import pandas as pd
import pytest

# Local libraries
import aggregate


def test__get_player_pts_stats_type_raises_error_for_multi_types():
    # Setup
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
def test__get_player_pts_stats_type(stat_type):
    # Setup
    player_pts = {
        "2504211": {
            stat_type: {
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
            stat_type: {
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
        "PROJ_Games_Played": {0: 1, 1: 1, 2: 1},
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
        "PROJ_Games_Played": np.dtype("int64"),
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
        "ACTUAL_Games_Played": {0: 1, 1: 1, 2: 1},
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
        "ACTUAL_Games_Played": np.dtype("int64"),
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
