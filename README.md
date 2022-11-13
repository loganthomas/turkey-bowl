# Turkey Bowl
[![Tests: main](https://img.shields.io/github/workflow/status/loganthomas/turkey-bowl/test-suite/main?label=tests%3A%20main&logo=GitHub)](https://github.com/loganthomas/turkey-bowl/actions/workflows/test-suite.yml)
[![Tests: dev](https://img.shields.io/github/workflow/status/loganthomas/turkey-bowl/test-suite/dev?label=tests%3A%20dev&logo=GitHub)](https://github.com/loganthomas/turkey-bowl/actions/workflows/test-suite.yml)
[![codecov](https://codecov.io/gh/loganthomas/turkey-bowl/branch/master/graph/badge.svg)](https://codecov.io/gh/loganthomas/turkey-bowl)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/0f1564fd54f74bc081398ae0b982d4fb)](https://www.codacy.com/gh/loganthomas/turkey-bowl/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=loganthomas/turkey-bowl&amp;utm_campaign=Badge_Grade)
[![Maintainability](https://api.codeclimate.com/v1/badges/08d1578979aeb217b85a/maintainability)](https://codeclimate.com/github/loganthomas/turkey-bowl/maintainability)
[![Auto Release](https://img.shields.io/github/workflow/status/loganthomas/turkey-bowl/auto-release?label=auto-release&logo=GitHub)](https://github.com/loganthomas/turkey-bowl/actions/workflows/auto-release.yml)


This repo contains Turkey Bowl fantasy football draft and scoring code.

Every year during Thanksgiving, my family has a fantasy football draft.
We *only include the teams that are playing on Thanksgiving* and limit the positions of
the draft in order to keep it simple. This has become a holiday tradition and been
a nice distraction from the amount of calories I consume at the dinner table.

A few things to note:
- The code is written in `Python (3.7.5)` and uses `requests` for web scrapping
- The player scores are grabbed from NFL.com (using their API)
- Player stats are manipulated using `pandas`

## Fantasy Scoring Details
__*Standard* scoring__ is used to aggregate points (see [nfl.com scoring](https://support.nfl.com/hc/en-us/articles/4989179237404-Scoring) for details; there is also a `tests/test_aggregate.test_standard_scoring_factors_*() unittest`)

### Offense
| Stat                               | Scoring Details      |
| ---------------------------------- | ---------------      |
| Passing                            | 1 point per 25 yards |
| Passing Touchdowns                 | 4 points             |
| Interceptions Thrown               | -2 Points            |
| Rushing                            | 1 point per 10 yards |
| Rushing Touchdowns                 | 6 points             |
| Receptions                         | 1 point              |
| Receiving Yards                    | 1 point per 10 yards |
| Receiving Touchdowns               | 6 points             |
| Kickoff and Punt Return Touchdowns | 6 points             |
| Fumble Recovered for TD            | 6 points             |
| 2-Point Conversions                | 2 points             |
| Fumbles Lost                       | -2 points            |

### Kicking
| Stat           | Scoring Details |
| -------------- | --------------- |
| PAT Made       | 1 point         |
| FG Made (0-49) | 3 points        |
| FG Made (50+)  | 5 points        |

### Team Defense and Special Teams
| Stat                            | Scoring Details |
| ------------------------------- | --------------- |
| Sack                            | 1 point         |
| Interception                    | 2 points        |
| Fumble Recovered                | 2 points        |
| Safety                          | 2 points        |
| Defensive Touchdowns            | 6 points        |
| Kick and Punt Return Touchdowns | 6 points        |
| 0 Points Allowed                | 10 points       |
| 1-6 Points Allowed              | 7 points        |
| 7-13 Points Allowed             | 4 points        |
| 14-20 Points Allowed            | 1 point         |
| 21-27 Points Allowed            | 0 points        |
| 28-34 Points Allowed            | -1 points       |
| 35+ Points Allowed              | -4 points       |

## Usage

```
 turkey-bowl --help
Usage: turkey-bowl [OPTIONS] COMMAND [ARGS]...

  Turkey Bowl fantasy football draft CLI

Options:
  -V, --version     Report current version of turkey-bowl package.
  --help            Show this message and exit.

Commands:
  clean             Delete current draft output directory and all its contents.
  scrape-actual     Scrape api.fantasy.nfl.com for player ACTUAL points
                    and merge with participant drafted teams.
  scrape-projected  Scrape api.fantasy.nfl.com for player PROJECTED points
                    and merge with participant drafted teams.
  setup             Setup output directory and create draft order.
```

A typical workflow can be found below.
- If desiring to update `player_ids.json`,
  be sure to change the first line `"year": 2022` to a year that is not the current year.
- If desiring to run a test,
  consider using the `--dry-run` option for both the `scrape-projected` and `scrape-actual` commands.

```
$ turkey-bowl setup

$ turkey-bowl scrape-projected

$ turkey-bowl scrape-actual
```

## Developer Notes

### Release CLI Documentation
For documentation of the full `release` command line interface (CLI),
please see the [release docs](docs/releases/README.md)
