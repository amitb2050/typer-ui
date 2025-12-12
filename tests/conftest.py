import os
import sys

import pytest
import typer
from typer.testing import CliRunner

pytest.register_assert_rewrite("typer_ui.main")

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_typer_app():
    app = typer.Typer()

    @app.command()
    def hello(name: str):
        """Say hello"""
        print(f"Hello {name}")

    @app.command()
    def goodbye(name: str, formal: bool = False):
        """Say goodbye"""
        if formal:
            print(f"Goodbye, Mr. {name}")
        else:
            print(f"Bye {name}")

    sub_app = typer.Typer(name="math", help="Math operations")
    app.add_typer(sub_app, name="math")

    @sub_app.command()
    def add(a: int, b: int):
        """Add two numbers"""
        print(a + b)

    return app
