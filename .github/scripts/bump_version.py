import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Path to the configuration file
TOML_PATH = Path("pyproject.toml")


def get_current_version():
    """Reads the current version from pyproject.toml."""
    if not TOML_PATH.exists():
        print(f"Error: {TOML_PATH} not found.")
        sys.exit(1)

    content = TOML_PATH.read_text()
    match = re.search(r'version = "(.+?)"', content)
    if match:
        return match.group(1)

    # Fallback or error if not found
    print("Error: Could not find version in pyproject.toml")
    sys.exit(1)


def update_toml_version(new_version):
    """Updates the version in pyproject.toml."""
    content = TOML_PATH.read_text()
    # Replace the version line
    # Uses regex to ensure we only replace the specific project version line
    new_content = re.sub(
        r'version = ".+?"', f'version = "{new_version}"', content, count=1
    )
    TOML_PATH.write_text(new_content)
    print(f"Updated pyproject.toml to version {new_version}")


def calculate_new_version(current_version):
    """
    Calculates the new version based on the current date (CalVer).
    Format: YYYY.MM.DD.INCREMENT
    """
    now = datetime.now()
    # Using %Y.%-m.%-d covers standard CalVer (e.g. 2025.12.9)
    # But usually 0-padding is safer for sorting: 2025.12.09
    date_str = now.strftime("%Y.%m.%d")

    # Check if the current version belongs to today
    if current_version.startswith(date_str):
        try:
            # Split to get the increment part
            # Expected format: YYYY.MM.DD.INC
            parts = current_version.split(".")
            increment = int(parts[-1]) + 1
            return f"{date_str}.{increment}"
        except (ValueError, IndexError):
            # If parsing fails (e.g. transitioning from 0.1.0 to date-based)
            # We start fresh for today
            return f"{date_str}.0"

    # If date is different (new day) or format is completely different
    return f"{date_str}.0"


def main():
    current_ver = get_current_version()
    print(f"Current version: {current_ver}")

    new_ver = calculate_new_version(current_ver)
    print(f"New version: {new_ver}")

    update_toml_version(new_ver)

    # Write to GITHUB_OUTPUT environment variable so steps can use it
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"version={new_ver}\n")


if __name__ == "__main__":
    main()
