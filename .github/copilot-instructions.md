<!-- Copilot instructions for the typer-ui repository -->
# Copilot / AI agent instructions — typer-ui

Purpose: give an AI coding agent the minimal, actionable knowledge needed to be productive in this repository.

1) Big picture (what this repo is and why)
- This is a small Python package (src layout) that provides a tiny UI/runtime for Typer CLI apps. Key responsibilities:
  - Introspect a Typer app and extract command + parameter metadata (`src/typer_ui/introspector.py`).
  - Build and run CLI commands as subprocesses and stream output (`src/typer_ui/command_executor.py`).
  - Package metadata & dependencies live in `pyproject.toml` (Python >= 3.7, depends on `typer` and `pydantic`).

2) Key files to read first
- `src/typer_ui/introspector.py` — primary domain logic for discovering Typer commands. Important facts:
  - `TyperIntrospector` expects a `typer.Typer` app and reads `app.registered_commands`.
  - `CommandInfo` extracts param information using `inspect.signature` and type hints; it models parameter shape with `pydantic.BaseModel` (`ParameterInfo`).
  - Default command name uses "main" when `cmd_info.name` is falsy.

- `src/typer_ui/command_executor.py` — runs commands via `asyncio.create_subprocess_exec`.
  - `build_command_args(module_path, command_name, parameters)` produces argv like: `[sys.executable, module_path, <command_name?>, --flag, --opt value]`.
  - Parameter naming: underscores in Python names are converted to CLI dashes (e.g. `db_url` -> `--db-url`).
  - Boolean parameters are emitted as bare flags only when True.
  - Output is streamed with a callback (defaults to `print`) and the class exposes `stop_execution()` to terminate a running process.

- `pyproject.toml` — project metadata and declared runtime dependencies (`typer`, `pydantic`). Use this for dependency/version hints.

3) Concrete developer workflows & commands
- Install the package locally:

  python -m pip install .

  For editable installs while hacking on code:

  python -m pip install -e .

- There are currently no test files in `tests/` (only `__init__.py`). If you add tests, use `pytest` and run `pytest -q` from the repo root.

- Linting / formatting: no toolchain is pinned in the repo. Follow `pyproject.toml` Python range and prefer standard tools (ruff, black) if you add them; don’t auto-insert without updating `pyproject.toml`.

4) Project-specific conventions & patterns
- Introspection-first design: the code assumes the Typer app exposes `registered_commands`. When adding support for other Typer registration approaches, mirror how `TyperIntrospector._extract_commands()` finds and wraps command callbacks.

- Parameter modeling: `ParameterInfo` uses `pydantic.BaseModel` for simple validation/serialization — keep this pattern when you add new metadata fields.

- CLI construction: `CommandExecutor.build_command_args()` controls how CLI args are emitted. If you change CLI formatting, update callers and tests for exact arg sequences.

5) Integration points & edges an AI should watch for
- Subprocess behavior: uses `asyncio` subprocess APIs and reads `stdout`/`stderr` concurrently. Any changes must retain streaming semantics and the `output_callback` hook.

- Type hints & runtime introspection: `get_type_hints(...)` is used; avoid changing function signatures in a way that breaks introspection without updating `introspector.py`.

6) Examples (concrete patterns you can use)
- Build args example (pseudo-Python):

  executor.build_command_args('path/to/app.py', 'serve', {'host': '0.0.0.0', 'debug': True})
  -> [sys.executable, 'path/to/app.py', 'serve', '--host', '0.0.0.0', '--debug']

- Introspector lookup example: load a `typer.Typer` app object and run:

  intros = TyperIntrospector(app)
  commands = [c.name for c in intros.commands]

7) What an agent should not assume
- There are no tests or CI configs in the repo; don't assume pytest/ruff are configured. If you add tooling, update `pyproject.toml` or add a README section.

- `src/typer_ui/main.py` is a placeholder — don't assume it implements an application entrypoint.

8) Quick checklist for common edit types
- Add a new command metadata field: update `ParameterInfo` (pydantic model), extend `_extract_parameters()` and add unit tests that assert serialized shape.
- Change CLI arg formatting: update `build_command_args()` and any callers; add a test that asserts exact argv lists.

9) Where to look for follow-ups
- When behavior is unclear, inspect `introspector.py` and `command_executor.py` first. They encode the repo's domain logic and conventions.

If anything here is unclear or you want me to add examples for a specific change type (new param attributes, tests, or CI instructions), tell me which area to expand.
