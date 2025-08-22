"""NiceGUI components for Typer UI"""

from nicegui import ui

from typer_ui.introspector import CommandNode, ParameterInfo


def create_parameter_input(param_info: ParameterInfo, value_container: dict):
    """Create a NiceGUI input component based on parameter info

    Args:
        param_info (dict): Parameter information dictionary
        value_container (dict): Dictionary to store the input value

    Returns:
        ui.element: Created NiceGUI input component
    """
    param_name = param_info.name
    param_type = param_info.param_type
    default = param_info.default
    required = param_info.required
    help_text = param_info.help
    python_type = param_info.python_type

    # Typer may mark required options/arguments with Ellipsis (`...`).
    # Normalize Ellipsis to None so UI code treats it as "no default".
    if default is ...:
        default = None

    # initialize stored value; for arguments without default keep empty string so UI can fill
    if param_name not in value_container:
        value_container[param_name] = default if default is not None else ""

    label_text = f"{param_name}"
    if required:
        label_text += " *"
    if help_text:
        label_text += f" - ({help_text})"
    # indicate whether this parameter is an argument or an option
    try:
        label_text += f" [{param_type.value}]"
    except Exception:
        pass

    # Choose widget based on discovered python_type
    if python_type is bool or (
        isinstance(python_type, type) and issubclass(python_type, bool)
    ):
        # NiceGUI checkbox expects the label as the first positional arg
        return ui.checkbox(
            label_text,
            value=bool(default),
            on_change=lambda e: value_container.update({param_name: e.value}),
        )

    if python_type is int or (
        isinstance(python_type, type) and issubclass(python_type, int)
    ):
        return ui.number(
            label=label_text,
            value=int(default) if default is not None else 0,
            on_change=lambda e: value_container.update({param_name: e.value}),
        )

    if python_type is float or (
        isinstance(python_type, type) and issubclass(python_type, float)
    ):
        return ui.number(
            label=label_text,
            value=float(default) if default is not None else 0.0,
            on_change=lambda e: value_container.update({param_name: e.value}),
            step=0.1,
        )

    # default to text input
    return ui.input(
        label=label_text,
        value=str(default) if default is not None else "",
        on_change=lambda e: value_container.update({param_name: e.value}),
    )


def create_command_form(command_info: CommandNode, on_execute_callback):
    """Create a NiceGUI form for a command based on its parameters

    Args:
        command_info (dict): Command information dictionary
        on_execute_callback (Callable): Callback function to call on form submission

    Returns:
        ui.element: Created NiceGUI form component
    """
    value_container = {}
    with ui.card().classes("w-full max-w-md"):
        ui.label(f"Command: {command_info.name}").classes("text-lg font-bold")
        if command_info.help:
            ui.markdown(command_info.help).classes("text-gray-600 mb-4")

        for param_info in command_info.parameters:
            create_parameter_input(param_info, value_container)

        ui.button(
            "Execute",
            on_click=lambda: on_execute_callback(command_info.name, value_container),
        ).classes("mt-4")

    return value_container


def create_log_display():
    """Create a NiceGUI component for displaying command execution logs

    Returns:
        ui.element: Created NiceGUI log display component
    """
    return ui.log(max_lines=1000).classes("w-full h-64")


def create_command_menu(commands: list[CommandNode], on_command_change_callback):
    """Create a nested menu (buttons) for top-level commands and groups.

    Renders top-level commands as buttons and groups as expandable sections. When a
    command is selected the callback is called with a path-like name
    ("group/command" or "command").
    """

    # Render a single menu trigger (hamburger) that contains top-level commands
    # and groups. Groups are menu_items with auto_close=False and a nested menu
    # using the same pattern as the NiceGUI example provided by the user.

    with ui.button(icon="menu"):
        with ui.menu():
            for node in commands:
                if node.is_group:
                    # parent item that stays open when opening the nested menu
                    with ui.menu_item(node.name, auto_close=False):
                        with ui.item_section().props("side"):
                            ui.icon("keyboard_arrow_right")
                        # nested submenu anchored to the right/top
                        with ui.menu().props(
                            'anchor="top end" self="top start" auto-close'
                        ):
                            for child in node.children:
                                path = f"{node.name}/{child.name}".strip("/")
                                # bind path into default arg to avoid late binding
                                ui.menu_item(
                                    child.name,
                                    on_click=lambda e,
                                    p=path: on_command_change_callback(p),
                                    auto_close=False,
                                )
                else:
                    # top-level command - single item
                    ui.menu_item(
                        node.name,
                        on_click=lambda e, p=node.name: on_command_change_callback(p),
                        auto_close=False,
                    )

    return None


def create_execution_controls(on_stop_callback):
    """Create NiceGUI buttons for controlling command execution

    Args:
        on_stop_callback (Callable): Callback function to call on stop button click

    Returns:
        ui.element: Created NiceGUI button components
    """
    with ui.row().classes("mt-4"):
        stop_button = ui.button(
            "Stop Execution", on_click=on_stop_callback, color="negative"
        ).classes("mr-2")
        clean_button = ui.button(
            "Clear Logs", on_click=lambda: ui.get_log().clear(), color="secondary"
        )

    return stop_button, clean_button
