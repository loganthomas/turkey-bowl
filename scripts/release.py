# Standard libraries
import glob
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path

# Third-party libraries
import typer

# Local libraries
from turkey_bowl.utils import setup_logger

logger = logging.getLogger("release")  # can be __name__ here as well


class FragmentOptions(str, Enum):
    """Defines possible enumeration types for new fragments."""

    bug = "bug"
    dep = "dep"
    doc = "doc"
    end = "enh"
    maint = "maint"


class Release:
    """
    Tools and methods for managing the release process.

    This is just for managing a new release in GitHub.
    It is not intended to be used for packaging nor deployment of th
    library itself.

    Attributes
    ----------
    changelog_mapping : dict
        A dictionary of available news fragment mappings.
        Currently, one of FragmentOptions:
        `bug`, `dep`, `doc`, `enh`, or `maint`.
    changelog_path : pathlib.Path
        The path to the CHANGELOG file that will be updated for the
        upcoming release.
    dry_run : bool
        Whether or not to treat the release as a dry-run or real.
    news_fragment_path : pathlib.Path
        The path to the directory that stores news fragments for the
        upcoming release.
    root: pathlib.Path
        The root directory of the project.

    Methods
    -------
    build_change_log(release_version, clean=False, dry_run=False)
        Build CHANGELOG file from all news fragments since last release.
    create_news_fragment()
        Create a single news fragment for the upcoming release.
    """

    def __init__(self, dry_run=False):
        self.root = Path(__file__).parent.parent
        self.changelog_path = self.root.joinpath("CHANGELOG.md").resolve()
        self.dry_run = dry_run
        self.news_fragment_path = self.root.joinpath("docs/releases/upcoming/").resolve()

    @property
    def changelog_mapping(self):
        """A mapping from FragmentOptions to CHANGELOG titles."""
        return {
            "type_to_description": {
                "bug": "Fixes",
                "dep": "Deprecations",
                "doc": "Documentation Changes",
                "enh": "Enhancements",
                "maint": "Infrastructure Improvements",
            }
        }

    def build_changelog(self, release_version, clean=False, dry_run=False):
        """Build CHANGELOG file from all news fragments since last release.

        Parameters
        ----------
        release_version : str
            The new release version that will be included at the top of the
            CHANGELOG.
        clean : bool, default=False
            Whether or not to delete news fragments once moved to CHANGELOG.
        dry_run : bool, default=False
            Whether or not to treat the update as a dry run and only print
            changes rather than making them.
        """
        logger.info(f"Building '{self.changelog_path}' for {release_version}...")

        HEADER = "# Release Notes"
        date_str = datetime.today().strftime("%Y-%m-%d")
        contents = [HEADER, "", f"## Release {release_version} -- {date_str}"]

        handled_file_paths = []

        for fragment_type, description in self.changelog_mapping["type_to_description"].items():
            pattern = Path(self.news_fragment_path).joinpath(f"*.{fragment_type}.md").resolve()
            pattern = str(pattern)
            file_paths = sorted(glob.glob(pattern))

            if file_paths:
                contents.append("")
                contents.append(description)
                contents.append("-" * len(description))

            for filename in file_paths:
                with open(filename, "r", encoding="utf-8") as fp:
                    contents.append("* " + fp.read())
                handled_file_paths.append(filename)

        # Prepend content to the changelog file.
        with open(self.changelog_path, "r", encoding="utf-8") as fp:
            original_changelog = fp.readlines()[1:]

        # Only print to console and exit
        if dry_run:
            logger.info("Executing a dry run. Updates will appear as below:")
            print("", *contents, sep="\n")
            raise typer.Exit()

        with open(self.changelog_path, "w", encoding="utf-8") as fp:
            if contents:
                print(*contents, sep="\n", file=fp)
            fp.write("".join(original_changelog))

        logger.info(f"Changelog is updated. Please review it at {self.changelog_path}")

        # Optionally clean up collected news fragments.
        if clean:
            for file_path in handled_file_paths:
                Path.unlink(Path(file_path))

            # Report any leftover for developers to inspect.
            leftovers = sorted(glob.glob(str(Path(self.news_fragment_path).joinpath("*"))))
            if leftovers:
                logger.info("These files are not collected:")
                logger.info("\n  ".join([""] + leftovers))

        logger.info("Done")

    def create_news_fragment(self):
        """Create a news fragment for a PR."""
        choices = [option.value for option in FragmentOptions]
        pr_number = typer.prompt("Please enter the PR number", type=int)
        fragment_type = typer.prompt(f"Choose a fragment type {choices}", type=FragmentOptions)

        filepath = Path(self.news_fragment_path).joinpath(f"{pr_number}.{fragment_type}.md")

        if filepath.exists():
            logger.warning("FAILED: File {} already exists.".format(filepath))
            raise typer.Abort()

        content = typer.prompt(
            "Describe the changes to the END USERS.\n"
            "Example: New command line interface (CLI) utility for creating news fragments created.\n",
            type=str,
        )
        if not Path(self.news_fragment_path).exists():
            Path.mkdir(self.news_fragment_path, parents=True)
        with open(filepath, "w", encoding="utf-8") as fp:
            fp.write(content + f" (#{pr_number})")
            fp.write("\n")  # ensure file ends in newline

        logger.info(f"Please commit the file created at: {filepath}")


if __name__ == "__main__":
    setup_logger(logging.INFO)

    app = typer.Typer()

    @app.command()
    def build_changelog(
        release_version: str,
        clean: bool = typer.Option(
            False, "--clean", help="Delete news fragments once CHANGELOG is build."
        ),
        dry_run: bool = typer.Option(
            False,
            "--dry-run",
            help="Treat as a dry run and only print changes without committing them.",
        ),
    ):
        """Build CHANGELOG file from all news fragments since last release."""
        release = Release()
        release.build_changelog(release_version, clean, dry_run)

    @app.command()
    def create_news_fragment():
        """Create a single news fragment for the upcoming release."""
        release = Release()
        release.create_news_fragment()

    app()
