"""Entrypoint for the Typer showcase CLI.

Run this file to launch the CLI: python src/run.py --help
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the `src` directory is on sys.path so `mycli` can be imported when
# running this script from the repository root as `python src/run.py`.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import sys

import typer

from mycli import app
from mycli.cli import MyCliError


def main():
    try:
        app()
    except MyCliError as exc:
        typer.secho(f"Error: {exc}", fg=typer.colors.RED)
        sys.exit(2)
    except Exception:
        # Re-raise other exceptions for visibility
        raise

app.registered_commands
if __name__ == "__main__":
    main()
