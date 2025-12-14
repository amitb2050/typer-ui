import os
import re
import sys
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


def bump_semver_version(current_version, rule):
    """
    Bumps the SemVer version based on the rule.
    Rule: 'major', 'minor', or 'patch'.
    """
    # specific check for the old legacy format to support transition if manual edit was missed
    # YYYY.MM.DD.BUILD -> Reset to 0.1.0 is safest, or 1.0.0
    # But since we already edited pyproject.toml, we expect X.Y.Z

    parts = current_version.split(".")
    if len(parts) != 3:
        # Fallback for non-semver compliant version
        print(
            f"Warning: Current version '{current_version}' is not standard SemVer (X.Y.Z)."
        )
        # If it looks like the old date format (4 parts), let's reset to a clean state
        # or if it's just messed up.
        # Let's decide to treat it as 0.0.0 pre-bump if we can't parse it,
        # OR just fail. Failing is better to alert the user.
        # However, to be nice, if we see 4 parts, we can try to coerce.
        # But for now, let's just error out or assume the user fixed it.
        # User request: "Based on the option, the right side should be reset to 0"

        # If I see 2025.12.12.0, I'll log and force a reset.
        print(
            "Resetting to 0.1.0 as a baseline before applying bump is ambiguous provided the rule."
        )
        # Actually, let's just return a default start.
        return "0.1.0"

    try:
        major, minor, patch = map(int, parts)
    except ValueError:
        print(f"Error: Version parts must be integers in '{current_version}'")
        sys.exit(1)

    if rule == "major":
        major += 1
        minor = 0
        patch = 0
    elif rule == "minor":
        minor += 1
        patch = 0
    elif rule == "patch":
        patch += 1
    else:
        print(f"Error: Unknown bump rule '{rule}'. Must be major, minor, or patch.")
        sys.exit(1)

    return f"{major}.{minor}.{patch}"


def main():
    current_ver = get_current_version()
    print(f"Current version: {current_ver}")

    bump_rule = os.environ.get("BUMP_RULE", "patch").lower()
    print(f"Bump rule: {bump_rule}")

    new_ver = bump_semver_version(current_ver, bump_rule)
    print(f"New version: {new_ver}")

    if os.environ.get("DRY_RUN") == "true":
        print("Dry run: Skipping update to pyproject.toml")
    else:
        update_toml_version(new_ver)

    # Write to GITHUB_OUTPUT environment variable so steps can use it
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"version={new_ver}\n")


if __name__ == "__main__":
    main()
