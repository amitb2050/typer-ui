"""Commands package for mycli showcase.

This package exposes modular Typer sub-apps that can be registered onto the
main app in `src/mycli/cli.py`.
"""

from .users import user_app

__all__ = ["user_app"]
