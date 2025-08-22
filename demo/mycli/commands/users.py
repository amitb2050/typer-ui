"""User related commands as a separate module to demonstrate nested modules.

This module defines a `user_app` Typer application that can be mounted onto the
main app in `src/mycli/cli.py` using `add_typer`.
"""

from __future__ import annotations

import typer

user_app = typer.Typer(help="User related commands")


@user_app.command()
def add(
    username: str = typer.Argument(..., help="Username"),
    admin: bool = typer.Option(False, help="Make user an admin"),
):
    """Add a user."""
    typer.echo(f"Adding user {username} (admin={admin})")


@user_app.command(name="remove")
def remove_user(username: str = typer.Argument(..., help="Username to remove")):
    """Remove a user."""
    typer.echo(f"Removing user {username}")
