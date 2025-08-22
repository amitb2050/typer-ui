"""Typer showcase CLI demonstrating common features and patterns.

Run with: python -m src.run --help  (or via the run.py entrypoint)
"""

from __future__ import annotations

import asyncio
import re
from enum import Enum
from pathlib import Path
from typing import List, Optional

import typer
from typer import BadParameter
from typer.colors import GREEN, RED, YELLOW

from .commands import user_app

app = typer.Typer(help="Typer showcase app. Explore commands and options.")


# --- Global (callback) option example ---
def version_callback(value: bool):
    if value:
        typer.echo("mycli version 1.0.0")
        raise typer.Exit()


def common_options():
    """Return a callback that adds a global --version flag via callback injection.

    This function shows how one might implement a global option with a callback.
    """


# We'll simulate a global option by creating a Typer app wrapper
main_app = typer.Typer()


@main_app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        callback=lambda v: version_callback(v),
        help="Show version and exit",
    ),
):
    """Main entrypoint for the mycli showcase - supports a global --version flag."""
    # callback handles printing/version exit
    return


# --- Basic commands and positional/optional args ---
@main_app.command(name="greet")
def greet(
    name: str = typer.Argument(..., help="Name to greet"),
    formal: bool = typer.Option(False, "--formal", help="Use a formal greeting"),
):
    """Greet somebody by name.

    Demonstrates positional arguments and boolean flags.
    """
    if formal:
        typer.secho(f"Good day, {name}.", fg=YELLOW)
    else:
        typer.secho(f"Hey {name}!", fg=GREEN)


# --- Options with defaults, prompts, type validation, and environment variables ---
@main_app.command()
def config(
    host: str = typer.Option("localhost", help="Server hostname"),
    port: int = typer.Option(8080, help="Server port", min=1, max=65535),
    debug: bool = typer.Option(
        False, envvar="MYCLI_DEBUG", help="Enable debug mode (env: MYCLI_DEBUG)"
    ),
    api_key: Optional[str] = typer.Option(
        None,
        prompt=True,
        hide_input=True,
        help="API key (will prompt if not provided)",
    ),
):
    """Show configuration values and validate them.

    Demonstrates default values, prompts, env var support, and min/max constraints.
    """
    typer.echo(f"Host: {host}")
    typer.echo(f"Port: {port}")
    typer.echo(f"Debug: {debug}")
    typer.echo(f"API key length: {len(api_key) if api_key else 0}")


# --- Enums and complex option types ---
class Color(Enum):
    red = "red"
    green = "green"
    blue = "blue"


@main_app.command()
def paint(
    color: Color = typer.Option(Color.red, help="Choose a paint color"),
    files: List[Path] = typer.Option([], exists=False, help="Files to paint"),
):
    """Demonstrate Enum and Path/list options.

    Passing multiple --files options collects into a list.
    """
    typer.echo(f"Color: {color.value}")
    typer.echo(f"Files: {', '.join(str(p) for p in files) if files else '<none>'}")


# --- Callbacks, custom validation, and explicit Argument/Option usage ---
def validate_email(ctx: typer.Context, value: str):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
        raise BadParameter("Not a valid email address")
    return value


@main_app.command()
def subscribe(
    email: str = typer.Argument(
        ..., callback=validate_email, help="Email to subscribe"
    ),
    weekly: bool = typer.Option(True, help="Receive weekly newsletter"),
):
    """Subscribe an email address (validates format).

    Shows explicit use of `typer.Argument` and `typer.Option` and validation callbacks.
    """
    typer.echo(f"Subscribing {email} (weekly={weekly})")


# --- Custom error handling and exit codes ---
class MyCliError(Exception):
    """Custom exception used to demonstrate non-zero exit codes."""


@main_app.command()
def fail(reason: Optional[str] = typer.Option(None, help="Reason to fail")):
    """Example command that demonstrates custom error raising and exit codes."""
    if not reason:
        raise MyCliError("No reason provided")
    typer.echo(f"Failing because: {reason}")


# --- Rich text output and confirmation prompts ---
@main_app.command()
def remove(
    path: Path = typer.Argument(..., exists=True, help="Path to remove"),
    recursive: bool = typer.Option(
        False, "-r", "--recursive", help="Remove recursively"
    ),
):
    """Simulate removing a file/directory with confirmation.

    Demonstrates colored output, confirmations, and prompts.
    """
    if not typer.confirm(f"Are you sure you want to remove {path}?"):
        typer.secho("Aborted.", fg=YELLOW)
        raise typer.Exit(code=1)
    typer.secho(f"Removed {path}", fg=RED)


# --- Nested commands with sub-applications (modular example) ---
# Import `user_app` from a separate module (shows how to split commands across files)


main_app.add_typer(user_app, name="user", help="Manage users")


# --- Async command example ---
@main_app.command()
def wait(seconds: int = typer.Option(1, help="Seconds to wait", min=0, max=10)):
    """Run an asynchronous wait (demonstrates asyncio usage inside a command)."""

    async def _sleep():
        typer.echo(f"Waiting {seconds} second(s) asynchronously...")
        await asyncio.sleep(seconds)
        typer.secho("Done waiting", fg=GREEN)

    asyncio.run(_sleep())


# --- Parameter constraints and regex example ---
@main_app.command()
def ratio(
    value: float = typer.Option(
        ..., help="A ratio between 0.0 and 1.0", min=0.0, max=1.0
    ),
):
    """Accepts a float constrained between 0 and 1."""
    typer.echo(f"Ratio: {value}")


# Attach the app object that users should import and run
app = main_app
