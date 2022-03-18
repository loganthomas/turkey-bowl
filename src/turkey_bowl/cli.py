import shutil
from pathlib import Path

import pandas as pd
import typer

from turkey_bowl import aggregate, utils
from turkey_bowl.draft import Draft
from turkey_bowl.leader_board import LeaderBoard
from turkey_bowl.scrape import Scraper

# Main CLI entry point
app = typer.Typer()

# Set option for nice DataFrame display
pd.options.display.width = None

HEADER = "\n{message:-^72}"


@app.command()
def clean():
    """Delete current draft output directory and all its contents."""
    year = utils.get_current_year()
    draft = Draft(year)
    delete = typer.confirm(
        f"Are you sure you want to delete {draft.output_dir}?", abort=True
    )
    if delete:
        typer.echo("Deleting...")
        shutil.rmtree(draft.output_dir.resolve())


@app.command()
def setup():
    """Setup output directory and create draft order."""
    year = utils.get_current_year()
    typer.echo(HEADER.format(message=f" {year} Turkey Bowl "))
    draft = Draft(year)
    draft.setup()


@app.command()
def scrape_projected(
    dry_run: bool = typer.Option(False, "--dry-run", help="Perform a dry run."),
):
    """
    Scrape api.fantasy.nfl.com for player PROJECTED points and
    merge with participant drafted teams.
    """
    year = utils.get_current_year()
    typer.echo(HEADER.format(message=" Scraping Player Projected Points "))
    draft = Draft(year)
    scraper = Scraper(year)

    if dry_run:
        week = input("Enter dry-run week: ")
        # TODO: use getter and setter to update scraper here
    else:
        week = scraper.nfl_thanksgiving_calendar_week

    projected_player_pts_path = Path(
        f"{draft.output_dir}/{year}_{week}_projected_player_pts.csv"
    )

    if not aggregate.check_projected_player_pts_pulled(
        year, week, savepath=projected_player_pts_path
    ):
        projected_player_pts = scraper.get_projected_player_pts()
        scraper.update_player_ids(projected_player_pts)
        aggregate.create_player_pts_df(
            year=year,
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
    year = utils.get_current_year()
    typer.echo(HEADER.format(message=" Scraping Player Actual Points "))
    draft = Draft(year)
    participant_teams = draft.load()

    if not draft.check_players_have_been_drafted(participant_teams):
        typer.echo(
            f"\nNot all players have been drafted yet! Please complete the draft for {year}."
        )
        raise typer.Abort()

    scraper = Scraper(year)

    if dry_run:
        week = input("Enter dry-run week: ")
        # TODO: use getter and setter to update this
    else:
        week = scraper.nfl_thanksgiving_calendar_week

    projected_player_pts_path = Path(
        f"{draft.output_dir}/{year}_{week}_projected_player_pts.csv"
    )
    projected_player_pts_df = pd.read_csv(projected_player_pts_path, index_col=0)
    actual_player_pts = scraper.get_actual_player_pts()

    if actual_player_pts:
        actual_player_pts_df = aggregate.create_player_pts_df(
            year=year, week=week, player_pts=actual_player_pts, savepath=None
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
            f"{draft.output_dir}/{year}_{week}_robust_participant_player_pts.xlsx"
        ),
    )

    board = LeaderBoard(year, participant_teams)
    board.display()
    board.save(f"{draft.output_dir}/{year}_leader_board.xlsx")


if __name__ == "__main__":
    app()
