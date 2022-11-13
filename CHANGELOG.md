# Release Notes

## Release v2022.1 -- 2022-11-13

## Release v2022.1 -- 2022-11-13

Fixes
-----
* Fix getter and setter for scraper nfl week. (#89)

* Fix incorrect aggregation warning by implementing double NaN check. (#96)


Deprecations
------------
* Removed travis CI as platform in favor of GitHub actions for running test suite. (#86)


Documentation Changes
---------------------
* Upload 2021 results. (#87)


Enhancements
------------
* Add ability to report version at command line via `turkey-bowl -V` or `turkey-bowl --version`. (#100)

* Add standard scoring docs and unittests. (#101)

* New directory configuration strucutre for keeping track of where things are daved. (#89)

* Cleanup CLI in preparation for 2022 run. (#94)


Infrastructure Improvements
---------------------------
* New command line interface (CLI) utility for automating news fragment creation and CHANGELOG building created. (#82)

* New GitHub actions created for auto-release and running test suite. (#86)

* Update CLI reporting to use logging (stream and file support). (#92)

