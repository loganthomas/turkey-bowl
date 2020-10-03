# Third-party libraries
import pytest

# Local libraries
import aggregate


def test__get_player_pnts_stats_type_raises_error_for_multi_types():
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
        aggregate._get_player_pnts_stat_type(player_pts)

    # Verify
    assert str(error_info.value) in (expected_error1, expected_error2)

    # Verify

    # Cleanup - none necessary


def test__get_player_pnts_stats_type_raises_error_for_unrecognized_type():
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
        aggregate._get_player_pnts_stat_type(player_pts)

    # Verify
    assert str(error_info.value) == expected_error

    # Verify

    # Cleanup - none necessary


@pytest.mark.parametrize(
    "stat_type", ["projectedStats", "stats"], ids=["projected", "actual"]
)
def test__get_player_pnts_stats_type(stat_type):
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
    result = aggregate._get_player_pnts_stat_type(player_pts)

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
