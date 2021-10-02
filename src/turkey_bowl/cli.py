# Standard libraries
import shutil

# Third-party libraries
import pandas as pd
import typer

# Local libraries
from turkey_bowl import utils
from turkey_bowl.draft import Draft

# Main CLI entry point
app = typer.Typer()

# Set option for nice DataFrame display
pd.options.display.width = None


@app.command()
def clean():
    """Delete current draft output directory and all its conetnts."""
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
    print(f"\n{'-'*5} {year} Turkey Bowl {'-'*5}")

    draft = Draft(year)
    draft.setup()


if __name__ == "__main__":
    app()
