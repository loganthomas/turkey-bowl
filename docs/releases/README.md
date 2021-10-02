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

Alternatively, use the following command, run from the project's `scripts` directory
and answer the questions:

```
python -m release create-news-fragment
````

Updating and building the `CHANGELOG.md` from the news fragments can be
accomplished by executing the below command from the project's `scripts` directory:

```
python -m release build-changelog RELEASE_VERSION
```
