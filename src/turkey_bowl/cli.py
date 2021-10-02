# Third-party libraries
import typer

app = typer.Typer()


@app.command()
def setup():
    typer.echo("hello")


if __name__ == "__main__":
    app()
