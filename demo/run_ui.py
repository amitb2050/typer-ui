import sys

import typer

from mycli import app
from mycli.cli import MyCliError
from typer_ui import TyperUI


def main():
    try:
        app()
    except MyCliError as exc:
        typer.secho(f"Error: {exc}", fg=typer.colors.RED)
        sys.exit(2)
    except Exception:
        # Re-raise other exceptions for visibility
        raise


if __name__ in {"__main__", "__mp_main__"}:
    typer_ui = TyperUI(app, module_path="run.py")
    typer_ui.run()
