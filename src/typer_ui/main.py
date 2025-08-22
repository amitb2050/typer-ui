"""Main entry point for the Typer UI application."""

import asyncio
from typing import Optional

import typer
from nicegui import ui

from . import ui_components as ui_comp
from .command_executor import CommandExecutor
from .introspector import TyperIntrospector


class TyperUI:
    """Main TyperUI application class"""

    def __init__(self, app: typer.Typer, module_path: Optional[str] = None):
        self.app = app
        self.module_path = module_path or self._detect_module_path()
        self.introspector = TyperIntrospector(app)
        self.command_executor = CommandExecutor(self._log_output)
        self.commands = self.introspector.commands
        self.current_command = None
        # store the selected command path (e.g. 'user/add') so execution can
        # include group names even when CommandNode.name is just the subcommand
        self.current_command_path = None
        self._current_form_values = {}
        self.log_area = None
        self.stop_button = None
        self.form_container = None

    def _detect_module_path(self) -> str:
        """Detect the module path from the app's __module__ attribute"""
        return self.app.__module__.replace(".", "/")

    def _log_output(self, message: str) -> None:
        """Log output to the UI log area"""
        if self.log_area:
            self.log_area.push(message)

    async def _execute_command(self, commands_name: str, parameters: dict):
        """Execute a command with the given parameters"""
        if self.command_executor.is_running:
            self._log_output(
                "Command is already running. Please wait or stop it first."
            )
            return

        # pair parameter values with their ParameterInfo metadata when available
        param_map = {}
        if self.current_command:
            # build a mapping name -> (ParameterInfo, value)
            for p in self.current_command.parameters:
                val = parameters.get(p.name)
                param_map[p.name] = (p, val)
            # also include any extra keys from parameters not in introspector
            for k, v in parameters.items():
                if k not in param_map:
                    param_map[k] = v

        else:
            param_map = parameters

        command_args = self.command_executor.build_command_args(
            module_path=self.module_path,
            command_name=commands_name,
            parameters=param_map,
        )

        self._log_output(f"Executing command: {' '.join(command_args)}")
        self._log_output("--" * 20)

        if self.stop_button:
            self.stop_button.props("disable=false")

        try:
            (
                return_code,
                stdout,
                stderr,
            ) = await self.command_executor.execute_command(command_args)
            self._log_output("--" * 20)
            self._log_output(f"Command finished with return code: {return_code}")
            if stdout:
                self._log_output(f"STDOUT:\n{stdout}")
            if stderr:
                self._log_output(f"STDERR:\n{stderr}")
        finally:
            if self.stop_button:
                self.stop_button.props("disable=true")

    def _on_command_change(self, command_name: str):
        """Handle command/menu selection change.

        `command_name` may be a path like "group/command" or a simple command name.
        Update current command and refresh the form. Also try to update the
        browser URL so navigation works when users select a command.
        """
        # update current command from introspector and remember the path used
        # to select it (this path may be 'group/command' or a simple name)
        self.current_command = self.introspector.get_command_by_name(command_name)
        self.current_command_path = command_name

        # Try to log selection to UI log; if the client's connection has been
        # deleted (multi-client or quick disconnect) fall back to stdout so
        # the server doesn't crash.
        try:
            self._log_output(f"Selected command: {command_name}")
        except RuntimeError:
            # client was likely deleted/disconnected; fallback
            print(f"Selected command: {command_name}")

        # Refresh the command form. Wrap in try/except for the same reason
        # — creating UI elements requires a live client context.
        try:
            self._refresh_command_form()
        except RuntimeError:
            # ignore refresh failure when client is gone; the client will
            # naturally re-request page state when reconnecting.
            print(f"Could not refresh form for: {command_name} (client missing)")

    def _refresh_command_form(self):
        """Refresh the command form with the current command's parameters"""
        if hasattr(self, "form_container"):
            self.form_container.clear()

        if self.current_command:
            with self.form_container:
                # ensure execution uses the selected command path so groups are included
                def _on_execute(cmd_name, params):
                    # prefer the recorded path; fall back to the form's command name
                    exec_name = self.current_command_path or cmd_name
                    return asyncio.create_task(self._execute_command(exec_name, params))

                self._current_form_values = ui_comp.create_command_form(
                    self.current_command,
                    _on_execute,
                )

    def _stop_execution(self):
        """Stop the currently running command"""
        self.command_executor.stop_execution()

    def _clear_logs(self):
        """Clear the log area"""
        if self.log_area:
            self.log_area.clear()

    def create_ui(self):
        """Create the NiceGUI UI components"""
        ui.page_title("Typer UI")
        with ui.column().classes("w-full max-w-4xl mx-auto p-4"):
            ui.label("Typer UI").classes("text-2xl font-bold mb-4")

            ui.label(f"Module: {self.module_path}").classes(
                "text-sm text-gray-600 mb-4"
            )

            with ui.row().classes("w-full gap-4"):
                with ui.column().classes("flex-1"):
                    ui.label("Commands:").classes("text-lg font-semibold mb-2")

                    if self.commands:
                        # Render a nested menu for the command tree. We expect
                        # `self.commands` to be a list of CommandNode objects.
                        ui_comp.create_command_menu(
                            self.commands, self._on_command_change
                        )
                        self.form_container = ui.column().classes("mt-4")
                    else:
                        ui.label("No commands found in the Typer app.").classes(
                            "text-red-500"
                        )

            with ui.column().classes("flex-1"):
                ui.label("Execution Logs:").classes("text-lg font-semibold mb-2")

                self.stop_button, clear_button = ui_comp.create_execution_controls(
                    self._stop_execution
                )
                self.stop_button.props("disable=true")
                clear_button.on("click", self._clear_logs)

                # log display
                ui.label("Command Output:").classes("text-md font-semibold mt-4 mb-2")
                self.log_area = ui_comp.create_log_display()

    def run(self, host: str = "localhost", port: int = 8080, **kwargs) -> None:
        """Run the NiceGUI app"""

        @ui.page("/")
        def main_page():
            self.create_ui()

        ui.run(host=host, port=port, **kwargs)


def create_typer_ui(app: typer.Typer, module_path: Optional[str] = None):
    """Create and run the Typer UI application

    Args:
        app (typer.Typer): Typer application instance
        module_path (Optional[str], optional): Path to the module containing the Typer app. Defaults to None.
    """
    return TyperUI(app, module_path)
