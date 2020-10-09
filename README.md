# Turkey Bowl
[![Build Status](https://img.shields.io/travis/loganthomas/turkey-bowl/master.svg?logo=travis)](https://travis-ci.com/loganthomas/turkey-bowl)
[![codecov](https://codecov.io/gh/loganthomas/turkey-bowl/branch/master/graph/badge.svg)](https://codecov.io/gh/loganthomas/turkey-bowl)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/3d9b862d5a414e64b3ffe804b9a73eee)](https://www.codacy.com/manual/loganthomas/turkey-bowl/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=loganthomas/turkey-bowl&amp;utm_campaign=Badge_Grade)

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
