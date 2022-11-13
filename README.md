# Turkey Bowl
[![Tests: main](https://img.shields.io/github/workflow/status/loganthomas/turkey-bowl/test-suite/main?label=tests%3A%20main&logo=GitHub)](https://github.com/loganthomas/turkey-bowl/actions/workflows/test-suite.yml)
[![Tests: dev](https://img.shields.io/github/workflow/status/loganthomas/turkey-bowl/test-suite/dev?label=tests%3A%20dev&logo=GitHub)](https://github.com/loganthomas/turkey-bowl/actions/workflows/test-suite.yml)
[![codecov](https://codecov.io/gh/loganthomas/turkey-bowl/branch/master/graph/badge.svg)](https://codecov.io/gh/loganthomas/turkey-bowl)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/0f1564fd54f74bc081398ae0b982d4fb)](https://www.codacy.com/gh/loganthomas/turkey-bowl/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=loganthomas/turkey-bowl&amp;utm_campaign=Badge_Grade)
[![Maintainability](https://api.codeclimate.com/v1/badges/08d1578979aeb217b85a/maintainability)](https://codeclimate.com/github/loganthomas/turkey-bowl/maintainability)
[![Auto Release](https://img.shields.io/github/workflow/status/loganthomas/turkey-bowl/auto-release?label=auto-release&logo=GitHub)](https://github.com/loganthomas/turkey-bowl/actions/workflows/auto-release.yml)


This repo contains Turkey Bowl fantasy football draft and scoring code.

Every year during Thanksgiving, my family has a fantasy football draft.
We only include the teams that are playing on Thanksgiving and limit the positions of
the draft in order to keep it simple. This has become a holiday tradition and been
a nice distraction from the amount of calories I consume at the dinner table.

A few things to note:
- The code is written in `Python (3.7.5)` and uses `requests` for web scrapping
- The player scores are grabbed from NFL.com (using their API)
- Player stats are manipulated using `pandas`
- There are a few different ways to run the code
  (assuming the draft has take place, and the `{year}_draft_sheet.xlsx` has been filled out):
  - `python thanks_fball.py` in command line will run the code without any interactive shell
  - Launch `ipython` and use `%run thanks_fball.py` will run the code and allow you to use
    some of the defined functions (a little more interactivity)
  - Launch `ipython` and use `%run thanks_fball.py` or import it and copy the `main()`
    function to run each line. This isn't the best option (to be fixed), but will give you
    a lot of meta data to work with.

# Fantasy Scoring Details
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

# Developer Notes

## Release CLI Documentation
For documentation of the full `release` command line interface (CLI),
please see the [release docs](docs/releases/README.md)

Add a news fragment
-------------------
Create a new file with a name like `<pull-request>.<type>.md`, where
`<pull-request>` is a pull request number, and `<type>` is one of:

- `bug`: fixes something broken
- `dep`: deprecates something from maintenance or deletes it entirely
- `doc`: documents something
- `enh`: adds a new feature
- `maint`: improves infrastructure maintenance

Then write a short sentence in the file that describes the changes for the
end users. Be sure to include the pull request number at the end of the sentence,
e.g. in `123.maint.md`:

```
New command line interface (CLI) utility for creating news fragments created. (#123)
```

Alternatively, you can use either of the following commands, and answer the questions:

```
# From the project's scripts directory
$ python -m release create-news-fragment

# From the project's root directory
$ python -m scripts.release create-news-fragment
````

Updating & Building the CHANGELOG
---------------------------------
Updating and building the `CHANGELOG.md` from the news fragments can be
accomplished by executing either of the below commands:

```
# From the project's scripts directory
$ python -m release build-changelog RELEASE_VERSION

# From the project's root directory
$ python -m scripts.release build-changelog RELEASE_VERSION
```
