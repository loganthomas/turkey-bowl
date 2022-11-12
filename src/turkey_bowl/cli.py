import logging
import shutil
from pathlib import Path
from typing import Optional

import pandas as pd
import typer

from turkey_bowl import __version__, aggregate, utils
from turkey_bowl.draft import Draft
from turkey_bowl.leader_board import LeaderBoard
from turkey_bowl.scrape import Scraper

# Main CLI entry point
app = typer.Typer(help="Turkey Bowl fantasy football draft CLI")

# Set option for nice DataFrame display
pd.options.display.width = None

HEADER = "\n\n{message:-^72}\n"
YEAR = utils.get_current_year()


logger = logging.getLogger(__name__)


@app.command()
def clean():
    """Delete current draft output directory and all its contents."""
    draft = Draft(YEAR)

    if Path(draft.dir_config.output_dir).exists():
        delete = typer.confirm(
            f"Are you sure you want to delete {draft.dir_config.output_dir}?",
            abort=True,
        )
        if delete:
            typer.echo("Deleting...")
            shutil.rmtree(draft.dir_config.output_dir.resolve())
    else:
        typer.echo(f"{draft.dir_config.output_dir} does not exits.")


@app.command()
def setup():
    """Setup output directory and create draft order."""
    utils.setup_logger()
    logger.info(
        HEADER.format(message=f" {YEAR} Turkey Bowl ") + f"turkey-bowl version: {__version__}\n"
    )
    draft = Draft(YEAR)
    draft.setup()


@app.command()
def scrape_projected(
    dry_run: bool = typer.Option(False, "--dry-run", help="Perform a dry run."),
):
    """
    Scrape api.fantasy.nfl.com for player PROJECTED points and
    merge with participant drafted teams.
    """
    utils.setup_logger()
    logger.info(HEADER.format(message=" Scraping Player Projected Points "))
    draft = Draft(YEAR)
    scraper = Scraper(YEAR)

    if dry_run:
        week = int(input("Enter dry-run week: "))
        scraper.nfl_thanksgiving_calendar_week = week
    else:
        week = scraper.nfl_thanksgiving_calendar_week

    projected_player_pts_path = Path(
        f"{draft.dir_config.output_dir}/{YEAR}_{week}_projected_player_pts.csv"
    )

    if not aggregate.projected_player_pts_pulled(YEAR, week, savepath=projected_player_pts_path):
        projected_player_pts = scraper.get_projected_player_pts()
        scraper.update_player_ids(projected_player_pts)
        aggregate.create_player_pts_df(
            year=YEAR,
            week=week,
            player_pts=projected_player_pts,
            savepath=projected_player_pts_path,
        )


@app.command()
def scrape_actual(
    dry_run: bool = typer.Option(False, "--dry-run", help="Perform a dry run."),
):
    """
    Scrape api.fantasy.nfl.com for player ACTUAL points and
    merge with participant drafted teams.
    """
    utils.setup_logger()
    logger.info(HEADER.format(message=" Scraping Player Actual Points "))
    draft = Draft(YEAR)
    participant_teams = draft.load()

    if not draft.check_players_have_been_drafted(participant_teams):
        logger.info(
            f"\nNot all players have been drafted yet! Please complete the draft for {YEAR}."
        )
        raise typer.Abort()

    scraper = Scraper(YEAR)

    if dry_run:
        week = int(input("Enter dry-run week: "))
        scraper.nfl_thanksgiving_calendar_week = week
    else:
        week = scraper.nfl_thanksgiving_calendar_week

    projected_player_pts_path = Path(
        f"{draft.dir_config.output_dir}/{YEAR}_{week}_projected_player_pts.csv"
    )
    projected_player_pts_df = pd.read_csv(projected_player_pts_path, index_col=0)
    actual_player_pts = scraper.get_actual_player_pts()

    if actual_player_pts:
        actual_player_pts_df = aggregate.create_player_pts_df(
            year=YEAR, week=week, player_pts=actual_player_pts, savepath=None
        )
    else:
        actual_player_pts_df = projected_player_pts_df[["Player", "Team"]].copy()
        actual_player_pts_df["ACTUAL_pts"] = 0.0

    # Merge points to teams
    participant_teams = aggregate.merge_points(
        participant_teams, projected_player_pts_df, verbose=False
    )

    participant_teams = aggregate.merge_points(
        participant_teams, actual_player_pts_df, verbose=True
    )

    # Sort robust columns so actual is next to projected
    participant_teams = aggregate.sort_robust_cols(participant_teams)

    # Write robust scores to excel for reviewing if desired
    aggregate.write_robust_participant_team_scores(
        participant_teams=participant_teams,
        savepath=Path(
            f"{draft.dir_config.output_dir}/{YEAR}_{week}_robust_participant_player_pts.xlsx"
        ),
    )

    board = LeaderBoard(YEAR, participant_teams)
    board.display()
    board.save(Path(f"{draft.dir_config.output_dir}/{YEAR}_leader_board.xlsx"))


def version_callback(value: bool):
    """
    Report current version of turkey-bowl package.
    """
    if value:
        typer.echo(f"{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-V",
        callback=version_callback,
        is_eager=True,
        help="Report current version of turkey-bowl package.",
    )
):
    return


if __name__ == "__main__":
    app()
