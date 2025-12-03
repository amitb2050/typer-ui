<!-- Copilot instructions for the typer-ui repository -->
# Copilot / AI agent instructions — typer-ui

Purpose: Give an AI coding agent the minimal, actionable knowledge needed to be productive in this repository.

1) Big picture (what this repo is and why)
- This is a small Python package (src layout) that provides a UI/runtime for Typer CLI apps. Key responsibilities:
  - Introspect a Typer app and extract command + parameter metadata (`src/typer_ui/introspector.py`)
  - Build and run CLI commands as subprocesses and stream output (`src/typer_ui/command_executor.py`) 
  - Render a web UI using NiceGUI with command forms and execution logs (`src/typer_ui/ui_components.py`)
  - Package metadata & dependencies in `pyproject.toml` (Python >=3.7, depends on `typer`, `pydantic`, and `nicegui`)

2) Key files to read first
- `src/typer_ui/main.py` — primary orchestrator that connects all components:
  - `TyperUI` class manages app state and component interaction
  - Uses `TyperIntrospector` to discover commands and `CommandExecutor` to run them
  - Creates UI layout/components and handles command execution flow

- `src/typer_ui/introspector.py` — command discovery and metadata extraction:
  - `TyperIntrospector` expects a `typer.Typer` app and reads `app.registered_commands`
  - `CommandNode` models command tree structure (groups and subcommands) with `pydantic.BaseModel`
  - `ParameterInfo` captures parameter details using `inspect.signature` and type hints
  - Default command name uses "main" when `cmd_info.name` is falsy

- `src/typer_ui/command_executor.py` — command execution and output streaming:
  - Uses `asyncio.create_subprocess_exec` for process management
  - `build_command_args()` handles CLI arg formatting (underscores -> dashes)
  - Streaming output through callback (defaults to print)
  - Supports graceful termination via `stop_execution()`

3) Developer workflows & commands
- Local installation:
```
python -m pip install .      # regular install
python -m pip install -e .   # editable/development install
```

- Run example UI:
```
cd demo/
python run_ui.py
```

- Test files: Currently no tests (only `tests/__init__.py`). When adding tests:
  - Use pytest and run from repo root with `pytest -q`
  - Model test structure after demo app in `demo/mycli/`
  - Cover command introspection, arg building, and UI rendering

4) Project-specific conventions
- Component architecture:
  - Introspection → Execution → UI rendering pipeline
  - Each component has focused responsibility
  - State flows from introspector through executor to UI

- Event handling:
  - UI uses callback-based patterns (form submission, log streaming)
  - Async execution with proper subprocess cleanup
  - Command state tracking (is_running, output buffering)

- UI patterns:
  - Form generation based on command parameters
  - Real-time command output streaming
  - Mobile-responsive header/menu structure

5) Integration points & edge cases
- Command parameter handling:
  - Boolean flags emit only when True
  - Proper escaping and quoting of values 
  - Handles required vs optional parameters
  - Supports complex types through type hints

- Process lifecycle:
  - Proper STDOUT/STDERR stream handling
  - Clean process termination support
  - Concurrent output processing

- UI state management:
  - Handles disconnected clients gracefully
  - Preserves command selections across refreshes
  - Command group path resolution

6) Examples from codebase
- Command parameter extraction:
```python
# From introspector.py
param_info = ParameterInfo(
    name=param_name,
    param_type=ParamType.OPTION,
    python_type=type_hints.get(param_name, str),
    default=default_value,
    required=required,
    help=help_text
)
```

- Command execution flow:
```python
# From main.py
command_args = self.command_executor.build_command_args(
    module_path=self.module_path,
    command_name=commands_name, 
    parameters=param_map
)
return_code, stdout, stderr = await self.command_executor.execute_command(command_args)
```

7) What an agent should not assume
- No testing infrastructure yet - don't assume pytest/coverage tools
- No linting configuration - prefer standard tools if adding
- `src/typer_ui/main.py` implements the core UI app, not a CLI entrypoint
- UI components are not tightly coupled - validate all dataflows

8) Common edit patterns
- Add command metadata:
  1. Update `ParameterInfo` model 
  2. Extend `_extract_parameters_from_callable()`
  3. Update UI form generation
  4. Add tests for serialization

- Change command execution:
  1. Modify `build_command_args()`
  2. Update parameter handling
  3. Test with various parameter types
  4. Verify UI interaction

9) Where to look for context
- Study `demo/mycli/` for command patterns
- Check `introspector.py` for parameter handling
- Review `ui_components.py` for UI patterns
- Follow execution flow in `main.py`

For questions or unclear areas, inspect the implementation in key files rather than making assumptions.
