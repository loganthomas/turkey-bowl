# Turkey Bowl
[![Build Status](https://img.shields.io/travis/loganthomas/turkey-bowl/master.svg?logo=travis)](https://travis-ci.com/loganthomas/turkey-bowl)
[![codecov](https://codecov.io/gh/loganthomas/turkey-bowl/branch/master/graph/badge.svg)](https://codecov.io/gh/loganthomas/turkey-bowl)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/0f1564fd54f74bc081398ae0b982d4fb)](https://www.codacy.com/gh/loganthomas/turkey-bowl/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=loganthomas/turkey-bowl&amp;utm_campaign=Badge_Grade)
[![Maintainability](https://api.codeclimate.com/v1/badges/08d1578979aeb217b85a/maintainability)](https://codeclimate.com/github/loganthomas/turkey-bowl/maintainability)
![Tests: main](https://github.com/loganthomas/turkey-bowl/actions/workflows/test-suite.yml/badge.svg?branch=main)
![Tests: dev](https://github.com/loganthomas/turkey-bowl/actions/workflows/test-suite.yml/badge.svg)
![Auto Release](https://github.com/loganthomas/turkey-bowl/actions/workflows/auto-release.yml/badge.svg)

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
