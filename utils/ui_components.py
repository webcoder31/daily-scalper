import traceback
import os
from typing import Union
from rich.table import Table
from rich.console import Console, Group
from rich.live import Live
from rich import box
from rich.rule import Rule
from rich.text import Text
from rich.panel import Panel
import readchar
from utils.theme import THEME


# --- UI Component for Interactive Menu Prompt ---

def ui_interactive_menu(
    entries: list[dict],
    title: str = None,
    title_style: str = THEME["title"],
    width: int = 100,
    option_style: str = THEME["primary"],
    desc_style: str = THEME["secondary"],
    selected_style: str = THEME["selected"],
    border_style: str = THEME["table_border"],
    default: int = 1,
    prompt_text: str = None,
    print_selected: bool = True
) -> int:
    """
    Display an interactive menu with arrow key navigation using Rich Live and readchar.
    Uses the global THEME from utils/theme for all color and style settings.

    Args:
        entries (list[dict]): List of menu entries. Each dict must have 'option' (str) and 'desc' (str) keys.
        title (str, optional): Title displayed above the menu.
        title_style (str, optional): Style for the title (default: THEME["title"]).
        width (int, optional): Table width (default: 100).
        option_style (str, optional): Style for the option column (default: THEME["primary"]).
        desc_style (str, optional): Style for the description column (default: THEME["secondary"]).
        selected_style (str, optional): Style for the selected row (default: THEME["selected"]).
        border_style (str, optional): Table border style (default: THEME["table_border"]).
        default (int, optional): Default selected option (1-based, default: 1).
        prompt_text (str, optional): Prompt for user input (default: None; no prompt displayed).
        print_selected (bool, optional): Whether to print the selected entry after selection (default: True).

    Returns:
        int: The selected option index (1-based).

    Raises:
        ValueError: If entries is empty, or if any entry is missing required keys.
        TypeError: If entries is not a list of dicts, or if default is not a valid integer.
    """
    # --- Parameter validation ---
    if not isinstance(entries, list) or not all(isinstance(e, dict) for e in entries):
        raise TypeError("entries must be a list of dictionaries.")
    if not entries:
        raise ValueError("entries list cannot be empty.")
    for i, entry in enumerate(entries):
        if "option" not in entry or "desc" not in entry:
            raise ValueError(f"Entry at index {i} missing 'option' or 'desc' key.")
        if not isinstance(entry["option"], str) or not isinstance(entry["desc"], str):
            raise TypeError(f"Entry at index {i} must have 'option' and 'desc' as strings.")
    if not isinstance(default, int) or not (1 <= default <= len(entries)):
        raise ValueError(f"default must be an integer between 1 and {len(entries)}.")

    console = Console(width=width)
    selected = default - 1

    def render_menu():
        table = Table(
            show_header=False,
            box=box.SIMPLE,
            style=THEME["table_style"],
            border_style=border_style,
            width=width
        )
        table.add_column("Option", style=option_style, width=3)
        table.add_column("Description", style=desc_style, width=width-3)
        for idx, entry in enumerate(entries):
            if idx == selected:
                table.add_row(
                    f"[{selected_style}]{entry['option']}[/{selected_style}]",
                    f"[{selected_style}]{entry['desc']}[/{selected_style}]"
                )
            else:
                table.add_row(entry["option"], entry["desc"])
        return table

    if title:
        console.print(f"\n{title}", style=title_style)
    if prompt_text is not None:
        console.print(f"[dim]{prompt_text}[/dim]")

    with Live(render_menu(), console=console, refresh_per_second=10, screen=False) as live:
        while True:
            key = readchar.readkey()
            if key in (readchar.key.UP, "k"):
                selected = (selected - 1) % len(entries)
                live.update(render_menu())
            elif key in (readchar.key.DOWN, "j"):
                selected = (selected + 1) % len(entries)
                live.update(render_menu())
            elif key in (readchar.key.ENTER, "\r", "\n"):
                break

    selected_desc = entries[selected]["desc"]
    if print_selected:
        console.print(f"Selected option: [{selected_style}]{selected_desc}[/{selected_style}]")
    return selected + 1


# --- Simple Table UI Component ---

def ui_modern_table(title: str, show_line: bool = False) -> Table:
    """
    Create a simple table with consistent theme styling.

    Args:
        title (str): The title for the table.
        show_line (bool): Whether to show horizontal lines in the table (default: False).

    Returns:
        Table: A Rich Table object with theme styling applied.
    """
    return Table(
        title=title,
        title_style=THEME["table_title"],
        title_justify="left",
        box=box.SIMPLE,
        pad_edge=False,
        expand=True,
        style=THEME["table_style"],
        header_style=THEME["table_header"],
        border_style=THEME["table_border"],
        show_lines=show_line,
    )


# --- Block Header UI Component ---

def ui_block_header(title: str, content: str) -> Group:
    """
    Create a block header with a panel, including blank lines before and after.

    Args:
        title (str): The title for the panel.
        content (str): The content to display in the panel.

    Returns:
        Group: A Rich Group object with blank lines and the panel.
    """
    panel = Panel(
        Text(content, justify="center"),
        title=title,
        padding=(1, 1),
        border_style=THEME["panel_border"],
        box=box.ROUNDED
    )
    return Group(Text(""), panel, Text(""))


# --- Section Header UI Component ---

def ui_section_header(label: str, style: str = THEME["dim"]) -> Group:
    """
    Render a styled horizontal rule with a label for section separation,
    with 2 blank lines before and 1 after, using Rich's Group.

    Args:
        label (str): The label to display in the center of the rule.

    Returns:
        Group: A Rich Group object with blank lines and the rule.
    """
    return Group(
        Text(""),
        Text(""),
        Rule(
            Text(label.upper(), style=style),
            style=style,
            characters="─",
            align="center"
        ),
        Text("")
    )


# --- Error Message UI Component ---

def ui_error_message(message: Union[str, Exception], title: str = "Error") -> Group:
    """
    Render a red panel for displaying error messages,
    with an icon in the title and a blank line before.

    Args:
        message (Union[str, Exception]): The error message to display or an Exception object.
        title (str): Optional title for the panel (default: "Error").

    Returns:
        Group: A Rich Group object with a blank line and the error panel.
    """
    icon = "❌"
    
    if isinstance(message, Exception):
        # Extract exception information
        exc_type = type(message).__name__
        exc_message = str(message)
        
        # Get traceback information
        tb = traceback.extract_tb(message.__traceback__)
        if tb:
            # Get the last frame (where the exception occurred)
            last_frame = tb[-1]
            
            # Get relative path from project root
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            try:
                relative_path = os.path.relpath(last_frame.filename, project_root)
            except ValueError:
                # If relpath fails (different drives on Windows), use basename
                relative_path = os.path.basename(last_frame.filename)
            
            location = f"{relative_path}:{last_frame.lineno} in {last_frame.name}"
            
            # Format the error message
            formatted_message = f"{exc_type}: {exc_message}\n\nLocation: {location}"
        else:
            formatted_message = f"{exc_type}: {exc_message}"
    else:
        formatted_message = message
    
    panel = Panel(
        formatted_message,
        title=f"{icon} {title}",
        title_align="left",
        border_style=THEME["error"],
        style=THEME["error"],
        padding=(1, 2)
    )
    return Group(Text(""), panel)