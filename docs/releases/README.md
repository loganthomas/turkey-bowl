The `upcoming` directory contains news fragments that will be added to the
CHANGELOG for the NEXT release.

Changes that are not of interest to the end-user can skip adding news fragment.

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

Documentation of `release` CLI
------------------------------
```
Usage: python -m scripts.release [OPTIONS] COMMAND [ARGS]...

Options:
  --help                Show this message and exit.

Commands:
  build-changelog       Build CHANGELOG file from all news fragments since last release.
  create-news-fragment  Create a single news fragment for the upcoming release.
```

#### `python -m scripts.release build-changelog [OPTIONS] RELEASE_VERSION`

Builds a CHANGELOG.md file from all news fragments since last release.

```
Usage: python -m scripts.release build-changelog [OPTIONS] RELEASE_VERSION

  Build CHANGELOG file from all news fragments since last release.

Arguments:
  RELEASE_VERSION  [required]

Options:
  --clean    Delete news fragments once CHANGELOG is build.  [default: False]
  --dry-run  Treat as a dry run and only print changes without committing them.
             [default: False]

  --help     Show this message and exit.
```

#### `python -m scripts.release create-news-fragment [OPTIONS]`

Create a single news fragment for the upcoming release.

```
Usage: python -m scripts.release create-news-fragment [OPTIONS]

  Create a single news fragment for the upcoming release.

Options:
  --help  Show this message and exit.
```
