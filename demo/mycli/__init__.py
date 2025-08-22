"""mycli package exposing the Typer app for the showcase.

Import the app as `mycli.app` so `src/run.py` can run it.
"""

from .cli import app

__all__ = ["app"]
