"""
Unit tests for leader_board.py
"""

import logging
import textwrap

import pandas as pd
import pytest

from turkey_bowl.leader_board import LeaderBoard


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
                2: 'Ryan Nall',
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
            'ACTUAL_pts': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_pts': {
                0: 20.22,
                1: 14.68,
                2: 2.4,
                3: 14.39,
                4: 6.19,
                5: 5.54,
                6: 0.0,
                7: 6.46,
                8: 6.66,
                9: 6.98,
            },
            'PROJ_Games_Played': {
                0: 1,
                1: 1,
                2: 1,
                3: 1,
                4: 1,
                5: 1,
                6: 1,
                7: 1,
                8: 1,
                9: 1,
            },
            'PROJ_Passing_Yards': {
                0: 240.26,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_Passing_Touchdowns': {
                0: 1.65,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_Interceptions_Thrown': {
                0: 0.78,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_Rushing_Yards': {
                0: 37.73,
                1: 78.49,
                2: 6.17,
                3: 1.74,
                4: 0.13,
                5: 0.04,
                6: 0.09,
                7: 0.0,
                8: 0.0,
                9: 34.23,
            },
            'PROJ_Fumbles_Lost': {
                0: 0.16,
                1: 0.12,
                2: 0.01,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_2-Point_Conversions': {
                0: 0.13,
                1: 0.01,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_Rushing_Touchdowns': {
                0: 0.31,
                1: 0.51,
                2: 0.04,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.0,
                9: 0.22,
            },
            'PROJ_Receptions': {
                0: 0.0,
                1: 1.9,
                2: 0.74,
                3: 5.14,
                4: 2.17,
                5: 1.93,
                6: 3.55,
                7: 0.0,
                8: 0.0,
                9: 1.22,
            },
            'PROJ_Receiving_Yards': {
                0: 0.0,
                1: 14.88,
                2: 7.02,
                3: 65.53,
                4: 29.86,
                5: 26.41,
                6: 46.72,
                7: 0.0,
                8: 0.0,
                9: 8.33,
            },
            'PROJ_Receiving_Touchdowns': {
                0: 0.0,
                1: 0.1,
                2: 0.02,
                3: 0.42,
                4: 0.17,
                5: 0.16,
                6: 0.37,
                7: 0.0,
                8: 0.0,
                9: 0.03,
            },
            'PROJ_PAT_Made': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 1.9,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_FG_Made_0-19': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.02,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_FG_Made_20-29': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.48,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_FG_Made_30-39': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.54,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_FG_Made_40-49': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.48,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_FG_Missed_50+': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.15,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_Sacks': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 2.46,
                9: 0.0,
            },
            'PROJ_Interceptions': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.78,
                9: 0.0,
            },
            'PROJ_Fumbles_Recovered': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.63,
                9: 0.0,
            },
            'PROJ_Safeties': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.03,
                9: 0.0,
            },
            'PROJ_Touchdowns': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.15,
                9: 0.0,
            },
            'PROJ_Blocked_Kicks': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.07,
                9: 0.0,
            },
            'PROJ_Team_Kickoff_and_Punt_Return_Touchdowns': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.07,
                9: 0.0,
            },
            'PROJ_Points_Allowed': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 23.74,
                9: 0.0,
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
            'ACTUAL_pts': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_pts': {
                0: 21.55,
                1: 12.88,
                2: 6.95,
                3: 11.24,
                4: 10.72,
                5: 9.32,
                6: 21.77,
                7: 7.34,
                8: 6.74,
                9: 14.37,
            },
            'PROJ_Games_Played': {
                0: 1,
                1: 1,
                2: 1,
                3: 1,
                4: 1,
                5: 1,
                6: 1,
                7: 1,
                8: 1,
                9: 1,
            },
            'PROJ_Passing_Yards': {
                0: 299.72,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_Passing_Touchdowns': {
                0: 1.98,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_Interceptions_Thrown': {
                0: 0.78,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_Rushing_Yards': {
                0: 18.18,
                1: 68.77,
                2: 32.4,
                3: 0.29,
                4: 0.16,
                5: 0.06,
                6: 56.78,
                7: 0.0,
                8: 0.0,
                9: 0.05,
            },
            'PROJ_Fumbles_Lost': {
                0: 0.04,
                1: 0.07,
                2: 0.06,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.03,
                7: 0.0,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_2-Point_Conversions': {
                0: 0.13,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.09,
                7: 0.0,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_Rushing_Touchdowns': {
                0: 0.2,
                1: 0.51,
                2: 0.24,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.34,
                7: 0.0,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_Receptions': {
                0: 0.0,
                1: 1.45,
                2: 1.09,
                3: 3.68,
                4: 3.1,
                5: 3.47,
                6: 6.6,
                7: 0.0,
                8: 0.0,
                9: 4.14,
            },
            'PROJ_Receiving_Yards': {
                0: 0.0,
                1: 12.76,
                2: 8.8,
                3: 54.31,
                4: 51.47,
                5: 41.04,
                6: 50.5,
                7: 0.0,
                8: 0.0,
                9: 72.89,
            },
            'PROJ_Receiving_Touchdowns': {
                0: 0.0,
                1: 0.06,
                2: 0.07,
                3: 0.35,
                4: 0.41,
                5: 0.29,
                6: 0.37,
                7: 0.0,
                8: 0.0,
                9: 0.49,
            },
            'PROJ_PAT_Made': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 2.72,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_FG_Made_0-19': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.06,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_FG_Made_20-29': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.48,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_FG_Made_30-39': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.49,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_FG_Made_40-49': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.51,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_FG_Missed_50+': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.28,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_Sacks': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 2.66,
                9: 0.0,
            },
            'PROJ_Interceptions': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.83,
                9: 0.0,
            },
            'PROJ_Fumbles_Recovered': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.65,
                9: 0.0,
            },
            'PROJ_Safeties': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.05,
                9: 0.0,
            },
            'PROJ_Touchdowns': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.14,
                9: 0.0,
            },
            'PROJ_Blocked_Kicks': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.07,
                9: 0.0,
            },
            'PROJ_Team_Kickoff_and_Punt_Return_Touchdowns': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.03,
                9: 0.0,
            },
            'PROJ_Points_Allowed': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 22.96,
                9: 0.0,
            },
            'PROJ_Kickoff_and_Punt_Return_Touchdowns': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.01,
                7: 0.0,
                8: 0.0,
                9: 0.0,
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
                0: 'ATL',
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
            'ACTUAL_pts': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_pts': {
                0: 20.01,
                1: 7.15,
                2: 13.38,
                3: 8.78,
                4: 16.72,
                5: 7.74,
                6: 0.0,
                7: 6.15,
                8: 7.4,
                9: 0.0,
            },
            'PROJ_Games_Played': {
                0: 1.0,
                1: 1.0,
                2: 1.0,
                3: 1.0,
                4: 1.0,
                5: 1.0,
                6: 1.0,
                7: 1.0,
                8: 1.0,
                9: 0.0,
            },
            'PROJ_Passing_Yards': {
                0: 296.77,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_Passing_Touchdowns': {
                0: 1.94,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_Interceptions_Thrown': {
                0: 0.74,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_Rushing_Yards': {
                0: 9.99,
                1: 15.62,
                2: 56.29,
                3: 0.99,
                4: 0.35,
                5: 0.11,
                6: 0.23,
                7: 0.0,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_Fumbles_Lost': {
                0: 0.09,
                1: 0.02,
                2: 0.06,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_2-Point_Conversions': {
                0: 0.19,
                1: 0.0,
                2: 0.01,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_Rushing_Touchdowns': {
                0: 0.11,
                1: 0.12,
                2: 0.35,
                3: 0.01,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_Receptions': {
                0: 0.0,
                1: 2.19,
                2: 2.49,
                3: 3.39,
                4: 5.93,
                5: 2.96,
                6: 7.18,
                7: 0.0,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_Receiving_Yards': {
                0: 0.0,
                1: 19.41,
                2: 25.41,
                3: 37.86,
                4: 81.79,
                5: 32.11,
                6: 83.25,
                7: 0.0,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_Receiving_Touchdowns': {
                0: 0.0,
                1: 0.13,
                2: 0.12,
                3: 0.24,
                4: 0.43,
                5: 0.26,
                6: 0.5,
                7: 0.0,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_PAT_Made': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 2.01,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_FG_Made_0-19': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.03,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_FG_Made_20-29': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.48,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_FG_Made_30-39': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.45,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_FG_Made_40-49': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.42,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_FG_Missed_50+': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.17,
                8: 0.0,
                9: 0.0,
            },
            'PROJ_Sacks': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 3.04,
                9: 0.0,
            },
            'PROJ_Interceptions': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.89,
                9: 0.0,
            },
            'PROJ_Fumbles_Recovered': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.66,
                9: 0.0,
            },
            'PROJ_Safeties': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.06,
                9: 0.0,
            },
            'PROJ_Touchdowns': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.16,
                9: 0.0,
            },
            'PROJ_Blocked_Kicks': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.07,
                9: 0.0,
            },
            'PROJ_Team_Kickoff_and_Punt_Return_Touchdowns': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 0.03,
                9: 0.0,
            },
            'PROJ_Points_Allowed': {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 17.2,
                9: 0.0,
            },
        },
    }

    participant_teams = {k: pd.DataFrame(v) for k, v in participant_teams.items()}
    return participant_teams


def test_LeaderBoard_instantiation(mock_participant_teams):
    # Setup
    year = 2020
    participant_teams = mock_participant_teams

    # Exercise
    board = LeaderBoard(year, participant_teams)

    # Verify
    assert board.year == 2020
    assert board.participant_teams == participant_teams
    assert board.filter_cols == ['Position', 'Player', 'Team', 'ACTUAL_pts', 'PROJ_pts']

    assert board.__repr__() == 'LeaderBoard(2020, participant_teams={})'
    assert board.__str__() == 'Turkey Bowl Leader Board: 2020'

    # Cleanup - none necessary


def test_LeaderBoard_data_no_acutal_pts(mock_participant_teams):
    # Setup
    year = 2020
    participant_teams = mock_participant_teams
    expected_data = {
        'PTS': {'Dodd': 0.0, 'Becca': 0.0, 'Logan': 0.0},
        'margin': {'Dodd': 0.0, 'Becca': 0.0, 'Logan': None},
        'pts_back': {'Dodd': 0.0, 'Becca': 0.0, 'Logan': 0.0},
    }

    expected_board_data_df = pd.DataFrame(expected_data)

    # Exercise
    board = LeaderBoard(year, participant_teams)
    result = board.data
    # Verify
    assert result.equals(expected_board_data_df)

    # Cleanup - none necessary


def test_LeaderBoard_data_with_acutal_pts(mock_participant_teams):
    # Setup
    year = 2020
    participant_teams = mock_participant_teams
    participant_teams['Dodd']['ACTUAL_pts'] = [
        1.0,
        2.0,
        3.0,
        4.0,
        5.0,
        6.0,
        7.0,
        8.0,
        9.0,
        10.0,
    ]
    participant_teams['Becca']['ACTUAL_pts'] = [
        1.0,
        2.0,
        3.0,
        4.0,
        5.0,
        6.0,
        7.0,
        8.0,
        10.0,
        11.0,
    ]
    participant_teams['Logan']['ACTUAL_pts'] = [
        10.0,
        11.0,
        12.0,
        13.0,
        14.0,
        15.0,
        16.0,
        17.0,
        18.0,
        19.0,
    ]

    # Bench (last value) doesn't count
    expected_data = {
        'PTS': {'Logan': 126.0, 'Becca': 46.0, 'Dodd': 45.0},
        'margin': {'Logan': 80.0, 'Becca': 1.0, 'Dodd': None},
        'pts_back': {'Logan': 0.0, 'Becca': 80.0, 'Dodd': 81.0},
    }

    expected_board_data_df = pd.DataFrame(expected_data)

    # Exercise
    board = LeaderBoard(year, participant_teams)
    result = board.data
    # Verify
    assert result.equals(expected_board_data_df)

    # Cleanup - none necessary


def test_LeaderBoard_display_no_actual_pts(mock_participant_teams, caplog):
    # Setup
    caplog.set_level(logging.INFO)
    participant_teams = mock_participant_teams

    expected_out_dodd = """
        ### DODD stats ###
                      Position            Player Team  ACTUAL_pts  PROJ_pts
        0                   QB        Josh Allen  BUF         0.0     20.22
        1                 RB_1  David Montgomery  CHI         0.0     14.68
        2                 RB_2         Ryan Nall  CHI         0.0      2.40
        3                 WR_1    Allen Robinson  CHI         0.0     14.39
        4                 WR_2    Anthony Miller  CHI         0.0      6.19
        5                   TE       Dawson Knox  BUF         0.0      5.54
        6      Flex (RB/WR/TE)        Jared Cook   NO         0.0      0.00
        7                    K      Cairo Santos  CHI         0.0      6.46
        8  Defense (Team Name)     Chicago Bears  CHI         0.0      6.66
        9     Bench (RB/WR/TE)   Latavius Murray   NO         0.0      6.98
        """

    expected_out_becca = """
        ### BECCA stats ###
                      Position           Player Team  ACTUAL_pts  PROJ_pts
        0                   QB     Dak Prescott  DAL         0.0     21.55
        1                 RB_1  Adrian Peterson  DET         0.0     12.88
        2                 RB_2  Kerryon Johnson  DET         0.0      6.95
        3                 WR_1     Marvin Jones  DET         0.0     11.24
        4                 WR_2       John Brown  BUF         0.0     10.72
        5                   TE   T.J. Hockenson  DET         0.0      9.32
        6      Flex (RB/WR/TE)     Alvin Kamara   NO         0.0     21.77
        7                    K      Matt Prater  DET         0.0      7.34
        8  Defense (Team Name)    Detroit Lions  DET         0.0      6.74
        9     Bench (RB/WR/TE)   Michael Gallup  DAL         0.0     14.37
        """

    expected_out_logan = """
        ### LOGAN stats ###
                      Position            Player Team  ACTUAL_pts  PROJ_pts
        0                   QB         Matt Ryan  ATL         0.0     20.01
        1                 RB_1     D'Andre Swift  DET         0.0      7.15
        2                 RB_2  Devin Singletary  BUF         0.0     13.38
        3                 WR_1      Russell Gage  ATL         0.0      8.78
        4                 WR_2      Amari Cooper  DAL         0.0     16.72
        5                   TE      Jimmy Graham  CHI         0.0      7.74
        6      Flex (RB/WR/TE)    Michael Thomas   NO         0.0      0.00
        7                    K        Tyler Bass  BUF         0.0      6.15
        8  Defense (Team Name)    Dallas Cowboys  DAL         0.0      7.40
        9     Bench (RB/WR/TE)      Randall Cobb  DAL         0.0      0.00
        """

    expected_out_winning_top = 'Dodd winning with 0.0 pts'
    expected_out_winning_stats = """
               PTS  margin  pts_back
        Dodd   0.0     0.0       0.0
        Becca  0.0     0.0       0.0
        Logan  0.0     NaN       0.0
        """

    # Exercise
    year = 2020
    board = LeaderBoard(year, participant_teams)
    board.display()

    # Verify
    assert textwrap.dedent(expected_out_dodd) in caplog.text
    assert textwrap.dedent(expected_out_becca) in caplog.text
    assert textwrap.dedent(expected_out_logan) in caplog.text
    assert expected_out_winning_top in caplog.text
    assert textwrap.dedent(expected_out_winning_stats) in caplog.text

    # Cleanup - none necessary


def test_LeaderBoard_display_with_actual_pts(mock_participant_teams, caplog):
    # Setup
    caplog.set_level(logging.INFO)
    participant_teams = mock_participant_teams
    participant_teams['Dodd']['ACTUAL_pts'] = [
        1.0,
        2.0,
        3.0,
        4.0,
        5.0,
        6.0,
        7.0,
        8.0,
        9.0,
        10.0,
    ]
    participant_teams['Becca']['ACTUAL_pts'] = [
        1.0,
        2.0,
        3.0,
        4.0,
        5.0,
        6.0,
        7.0,
        8.0,
        10.0,
        11.0,
    ]
    participant_teams['Logan']['ACTUAL_pts'] = [
        10.0,
        11.0,
        12.0,
        13.0,
        14.0,
        15.0,
        16.0,
        17.0,
        18.0,
        19.0,
    ]

    expected_out_dodd = """
        ### DODD stats ###
                      Position            Player Team  ACTUAL_pts  PROJ_pts
        0                   QB        Josh Allen  BUF         1.0     20.22
        1                 RB_1  David Montgomery  CHI         2.0     14.68
        2                 RB_2         Ryan Nall  CHI         3.0      2.40
        3                 WR_1    Allen Robinson  CHI         4.0     14.39
        4                 WR_2    Anthony Miller  CHI         5.0      6.19
        5                   TE       Dawson Knox  BUF         6.0      5.54
        6      Flex (RB/WR/TE)        Jared Cook   NO         7.0      0.00
        7                    K      Cairo Santos  CHI         8.0      6.46
        8  Defense (Team Name)     Chicago Bears  CHI         9.0      6.66
        9     Bench (RB/WR/TE)   Latavius Murray   NO        10.0      6.98
        """
    expected_out_becca = """
        ### BECCA stats ###
                      Position           Player Team  ACTUAL_pts  PROJ_pts
        0                   QB     Dak Prescott  DAL         1.0     21.55
        1                 RB_1  Adrian Peterson  DET         2.0     12.88
        2                 RB_2  Kerryon Johnson  DET         3.0      6.95
        3                 WR_1     Marvin Jones  DET         4.0     11.24
        4                 WR_2       John Brown  BUF         5.0     10.72
        5                   TE   T.J. Hockenson  DET         6.0      9.32
        6      Flex (RB/WR/TE)     Alvin Kamara   NO         7.0     21.77
        7                    K      Matt Prater  DET         8.0      7.34
        8  Defense (Team Name)    Detroit Lions  DET        10.0      6.74
        9     Bench (RB/WR/TE)   Michael Gallup  DAL        11.0     14.37
        """

    expected_out_logan = """
        ### LOGAN stats ###
                      Position            Player Team  ACTUAL_pts  PROJ_pts
        0                   QB         Matt Ryan  ATL        10.0     20.01
        1                 RB_1     D'Andre Swift  DET        11.0      7.15
        2                 RB_2  Devin Singletary  BUF        12.0     13.38
        3                 WR_1      Russell Gage  ATL        13.0      8.78
        4                 WR_2      Amari Cooper  DAL        14.0     16.72
        5                   TE      Jimmy Graham  CHI        15.0      7.74
        6      Flex (RB/WR/TE)    Michael Thomas   NO        16.0      0.00
        7                    K        Tyler Bass  BUF        17.0      6.15
        8  Defense (Team Name)    Dallas Cowboys  DAL        18.0      7.40
        9     Bench (RB/WR/TE)      Randall Cobb  DAL        19.0      0.00
        """

    expected_out_winning_top = 'Logan winning with 126.0 pts'
    expected_out_winning_stats = """
                 PTS  margin  pts_back
        Logan  126.0    80.0       0.0
        Becca   46.0     1.0      80.0
        Dodd    45.0     NaN      81.0
        """

    # Exercise
    year = 2020
    board = LeaderBoard(year, participant_teams)
    board.display()

    # Verify
    assert textwrap.dedent(expected_out_dodd) in caplog.text
    assert textwrap.dedent(expected_out_becca) in caplog.text
    assert textwrap.dedent(expected_out_logan) in caplog.text
    assert expected_out_winning_top in caplog.text
    assert textwrap.dedent(expected_out_winning_stats) in caplog.text

    # Cleanup - none necessary


def test_LeaderBoard_save(mock_participant_teams, tmp_path, caplog):
    # Setup
    caplog.set_level(logging.INFO)
    year = 2020
    participant_teams = mock_participant_teams
    participant_teams['Dodd']['ACTUAL_pts'] = [
        1.0,
        2.0,
        3.0,
        4.0,
        5.0,
        6.0,
        7.0,
        8.0,
        9.0,
        10.0,
    ]
    participant_teams['Becca']['ACTUAL_pts'] = [
        1.0,
        2.0,
        3.0,
        4.0,
        5.0,
        6.0,
        7.0,
        8.0,
        10.0,
        11.0,
    ]
    participant_teams['Logan']['ACTUAL_pts'] = [
        10.0,
        11.0,
        12.0,
        13.0,
        14.0,
        15.0,
        16.0,
        17.0,
        18.0,
        19.0,
    ]

    tmp_archive_dir = tmp_path.joinpath('archive')
    tmp_archive_dir.mkdir()

    tmp_year_dir = tmp_archive_dir.joinpath(str(year))
    tmp_year_dir.mkdir()

    tmp_leader_board_path = tmp_path.joinpath(f'{year}_leader_board.xlsx')

    # Bench (last value) doesn't count
    expected_data = {
        'PTS': {'Logan': 126.0, 'Becca': 46.0, 'Dodd': 45.0},
        'margin': {'Logan': 80.0, 'Becca': 1.0, 'Dodd': None},
        'pts_back': {'Logan': 0.0, 'Becca': 80.0, 'Dodd': 81.0},
    }

    expected_board_data_df = pd.DataFrame(expected_data)

    expected_out = f'Saving LeaderBoard to {tmp_leader_board_path}...'
    # Exercise
    assert tmp_leader_board_path.exists() is False
    board = LeaderBoard(year, participant_teams)
    board.save(tmp_leader_board_path)

    # Verify
    assert tmp_leader_board_path.exists()

    participant_dtypes = {'ACTUAL_pts': 'float64', 'PROJ_pts': 'float64'}

    written_board = pd.read_excel(
        tmp_leader_board_path,
        sheet_name='Leader Board',
        index_col=0,
        engine='openpyxl',
    )
    written_board = written_board.astype('float64')

    written_dodd = pd.read_excel(tmp_leader_board_path, sheet_name='Dodd', engine='openpyxl')
    written_dodd = written_dodd.astype(participant_dtypes)

    written_becca = pd.read_excel(tmp_leader_board_path, sheet_name='Becca', engine='openpyxl')
    written_becca = written_becca.astype(participant_dtypes)

    written_logan = pd.read_excel(tmp_leader_board_path, sheet_name='Logan', engine='openpyxl')
    written_logan = written_logan.astype(participant_dtypes)

    assert written_board.equals(expected_board_data_df)
    assert written_dodd.equals(
        participant_teams['Dodd'][['Position', 'Player', 'Team', 'ACTUAL_pts', 'PROJ_pts']]
    )

    assert expected_out in caplog.text

    # Cleanup - none necessary
