# Publishing Guide (Automated CalVer)

This guide explains how to release `typer-ui` using the automated Date-Based Versioning (CalVer) workflow.

## Overview

The workflow now handles versioning automatically. You do **not** need to manually edit `pyproject.toml` or create tags.

**Version Format**: `YYYY.MM.DD.INCREMENT`
Example: `2025.12.09.0`, then `2025.12.09.1`, etc.

## Prerequisites

Ensure you have the `PYPI_API_TOKEN` secret set in GitHub Settings (see previous instructions).

## How to Release

1.  **Go to GitHub Actions**:
    Navigate to the "Actions" tab in your repository.

2.  **Select "Publish to PyPI"**:
    Click on the workflow named "Publish to PyPI" on the left sidebar.

3.  **Run Workflow**:
    *   Click the **Run workflow** button (usually top right of the list).
    *   (Optional) Leave `dry_run` as `false` to actually publish. Set to `true` if you just want to test the bump and build process.
    *   Click **Run workflow**.

## What happens next?

The automation will:
1.  **Run Tests**: Ensure code quality.
2.  **Calculate Version**: Check the current date. If today is `2025-12-09` and the last release was `2025.12.09.0`, the new version becomes `2025.12.09.1`.
3.  **Update File**: Updates `pyproject.toml` with the new version.
4.  **Commit & Push**: Commits the change to `main` and creates a git tag (e.g., `v2025.12.09.1`).
5.  **Publish**: Builds the package and uploads it to PyPI.

## CHANGELOG

Since versioning is automated, you should manually update `CHANGELOG.md` with your feature notes *before* running the workflow. You can just list them under an "Upcoming" or "Next" section, and the automated commit will just bump the version file.
