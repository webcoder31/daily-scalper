"""
Rich terminal UI components and interactive elements for the Daily Scalper application.

This module provides comprehensive UI components built on the Rich library for
creating interactive terminal interfaces. It includes menu systems, tables,
panels, error displays, and other UI elements with consistent theming and
robust error handling.

Functions:
    ui_interactive_menu: Interactive menu with arrow key navigation
    ui_modern_table: Styled table component with theme integration
    ui_block_header: Block header with panel styling
    ui_section_header: Section separator with horizontal rule
    ui_error_message: Error message display with exception handling
    ui_success_message: Success message display component
    ui_warning_message: Warning message display component
    ui_info_message: Info message display component

Classes:
    UIComponentError: Custom exception for UI component errors
    MenuNavigationError: Custom exception for menu navigation errors

Example:
    >>> from utils.ui_components import ui_interactive_menu, ui_modern_table
    >>> entries = [{"option": "1", "desc": "Test Option"}]
    >>> selection = ui_interactive_menu(entries, title="Test Menu")
    >>> table = ui_modern_table("Test Table")
"""

import traceback
import os
from typing import Union, List, Dict, Any, Optional, Tuple
from pathlib import Path
import logging
from rich.table import Table
from rich.console import Console, Group
from rich.live import Live
from rich import box
from rich.rule import Rule
from rich.text import Text
from rich.panel import Panel
import readchar
from utils.theme import THEME

# Configure logging
from utils.logging_config import get_logger
logger = get_logger(__name__)


class UIComponentError(Exception):
    """Exception raised when UI component operations fail."""
    

    def __init__(self, message: str, component: Optional[str] = None, cause: Optional[Exception] = None) -> None:
        """
        Initialize UIComponentError.
        
        Args:
            message: Error message describing the issue.
            component: The UI component that caused the error (optional).
            cause: The underlying exception that caused this error (optional).
        """
        self.component = component
        self.cause = cause
        super().__init__(message)


class MenuNavigationError(Exception):
    """Exception raised when menu navigation fails."""
    
    
    def __init__(self, message: str, menu_state: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None) -> None:
        """
        Initialize MenuNavigationError.
        
        Args:
            message: Error message describing the navigation issue.
            menu_state: Current menu state information (optional).
            cause: The underlying exception that caused this error (optional).
        """
        self.menu_state = menu_state or {}
        self.cause = cause
        super().__init__(message)


def ui_interactive_menu(
    entries: List[Dict[str, str]],
    title: Optional[str] = None,
    title_style: str = THEME["title"],
    width: int = 100,
    option_style: str = THEME["primary"],
    desc_style: str = THEME["secondary"],
    selected_style: str = THEME["selected"],
    border_style: str = THEME["table_border"],
    default: int = 1,
    prompt_text: Optional[str] = None,
    print_selected: bool = True,
    allow_empty_selection: bool = False
) -> int:
    """
    Display an interactive menu with arrow key navigation using Rich Live.
    
    This function creates a fully interactive menu system with keyboard navigation,
    visual feedback, and comprehensive error handling. It supports customizable
    styling through the theme system and provides robust input validation.
    
    Args:
        entries: List of menu entries. Each dict must have 'option' and 'desc' keys.
        title: Title displayed above the menu (optional).
        title_style: Rich style string for the title.
        width: Table width in characters.
        option_style: Rich style string for the option column.
        desc_style: Rich style string for the description column.
        selected_style: Rich style string for the selected row.
        border_style: Rich style string for table borders.
        default: Default selected option (1-based index).
        prompt_text: Additional prompt text displayed below title (optional).
        print_selected: Whether to print the selected entry after selection.
        allow_empty_selection: Whether to allow selection of empty entries.
        
    Returns:
        Selected option index (1-based).
        
    Raises:
        UIComponentError: If menu setup or display fails.
        MenuNavigationError: If navigation encounters errors.
        ValueError: If invalid parameters are provided.
        
    Example:
        >>> entries = [
        ...     {"option": "1", "desc": "Load data"},
        ...     {"option": "2", "desc": "Run backtest"},
        ...     {"option": "3", "desc": "Exit"}
        ... ]
        >>> selection = ui_interactive_menu(entries, title="Main Menu")
        >>> print(f"Selected option: {selection}")
    """
    # Comprehensive parameter validation
    _validate_menu_parameters(entries, default, width, allow_empty_selection)
    
    try:
        console = Console(width=width)
        selected = default - 1  # Convert to 0-based index
        
        def render_menu() -> Table:
            """Render the menu table with current selection state."""
            try:
                table = Table(
                    show_header=False,
                    box=box.SIMPLE,
                    style=THEME["table_style"],
                    border_style=border_style,
                    width=width
                )
                
                # Configure columns with proper width distribution
                option_width = max(3, min(10, width // 10))  # Adaptive option column width
                desc_width = width - option_width - 4  # Account for borders and padding
                
                table.add_column("Option", style=option_style, width=option_width)
                table.add_column("Description", style=desc_style, width=desc_width)
                
                # Add rows with selection highlighting
                for idx, entry in enumerate(entries):
                    if idx == selected:
                        table.add_row(
                            f"[{selected_style}]{entry['option']}[/{selected_style}]",
                            f"[{selected_style}]{entry['desc']}[/{selected_style}]"
                        )
                    else:
                        table.add_row(entry["option"], entry["desc"])
                
                return table
                
            except Exception as e:
                raise UIComponentError(
                    f"Failed to render menu table: {str(e)}",
                    component="menu_table",
                    cause=e
                ) from e
        
        # Display title and prompt if provided
        if title:
            console.print(f"\n{title}", style=title_style)
        
        if prompt_text:
            console.print(f"[dim]{prompt_text}[/dim]")
        
        # Interactive navigation loop
        try:
            with Live(render_menu(), console=console, refresh_per_second=10, screen=False) as live:
                while True:
                    try:
                        key = readchar.readkey()
                        
                        # Handle navigation keys
                        if key in (readchar.key.UP, "k", "K"):
                            selected = (selected - 1) % len(entries)
                            live.update(render_menu())
                            logger.debug(f"Menu navigation: UP to index {selected}")
                            
                        elif key in (readchar.key.DOWN, "j", "J"):
                            selected = (selected + 1) % len(entries)
                            live.update(render_menu())
                            logger.debug(f"Menu navigation: DOWN to index {selected}")
                            
                        elif key in (readchar.key.ENTER, "\r", "\n", " "):
                            # Validate selection before accepting
                            if not allow_empty_selection and not entries[selected]["desc"].strip():
                                console.print("[dim]Cannot select empty option[/dim]")
                                continue
                            break
                            
                        elif key in (readchar.key.ESC, "q", "Q"):
                            # Allow graceful exit with ESC or 'q'
                            logger.info("Menu navigation cancelled by user")
                            raise KeyboardInterrupt("Menu navigation cancelled")
                            
                        # Handle direct number selection
                        elif key.isdigit():
                            digit_selection = int(key) - 1
                            if 0 <= digit_selection < len(entries):
                                selected = digit_selection
                                live.update(render_menu())
                                logger.debug(f"Menu navigation: Direct selection {selected}")
                        
                    except KeyboardInterrupt:
                        console.print("\n[dim]Menu cancelled[/dim]")
                        raise
                    except Exception as e:
                        raise MenuNavigationError(
                            f"Navigation error: {str(e)}",
                            menu_state={"selected": selected, "total_entries": len(entries)},
                            cause=e
                        ) from e
        
        except KeyboardInterrupt:
            raise
        except Exception as e:
            raise UIComponentError(
                f"Menu display failed: {str(e)}",
                component="interactive_menu",
                cause=e
            ) from e
        
        # Display selection confirmation
        selected_entry = entries[selected]
        if print_selected:
            console.print(f"Selected option: [{selected_style}]{selected_entry['desc']}[/{selected_style}]")
        
        logger.info(f"Menu selection completed: option {selected + 1} - {selected_entry['desc']}")
        return selected + 1  # Return 1-based index
        
    except (UIComponentError, MenuNavigationError, KeyboardInterrupt):
        raise
    except Exception as e:
        raise UIComponentError(
            f"Unexpected error in interactive menu: {str(e)}",
            component="interactive_menu",
            cause=e
        ) from e


def _validate_menu_parameters(
    entries: List[Dict[str, str]],
    default: int,
    width: int,
    allow_empty_selection: bool
) -> None:
    """
    Validate parameters for the interactive menu.
    
    Args:
        entries: Menu entries to validate.
        default: Default selection to validate.
        width: Menu width to validate.
        allow_empty_selection: Whether empty selections are allowed.
        
    Raises:
        ValueError: If any parameter is invalid.
    """
    # Validate entries structure
    if not isinstance(entries, list):
        raise ValueError("entries must be a list of dictionaries")
    
    if not entries:
        raise ValueError("entries list cannot be empty")
    
    # Validate each entry
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValueError(f"Entry at index {i} must be a dictionary")
        
        required_keys = ["option", "desc"]
        for key in required_keys:
            if key not in entry:
                raise ValueError(f"Entry at index {i} missing required key: '{key}'")
            if not isinstance(entry[key], str):
                raise ValueError(f"Entry at index {i} key '{key}' must be a string")
        
        # Check for empty descriptions if not allowed
        if not allow_empty_selection and not entry["desc"].strip():
            raise ValueError(f"Entry at index {i} has empty description and allow_empty_selection=False")
    
    # Validate default selection
    if not isinstance(default, int):
        raise ValueError("default must be an integer")
    
    if not (1 <= default <= len(entries)):
        raise ValueError(f"default must be between 1 and {len(entries)}")
    
    # Validate width
    if not isinstance(width, int) or width < 20:
        raise ValueError("width must be an integer >= 20")


def ui_modern_table(
    title: str,
    show_line: bool = False,
    title_style: Optional[str] = None,
    expand: bool = True,
    box_style: Optional[box.Box] = None
) -> Table:
    """
    Create a modern styled table with consistent theme integration.
    
    Args:
        title: The title for the table.
        show_line: Whether to show horizontal lines between rows.
        title_style: Custom title style (uses theme default if None).
        expand: Whether the table should expand to fill available width.
        box_style: Custom box style (uses SIMPLE if None).
        
    Returns:
        Configured Rich Table object with theme styling applied.
        
    Raises:
        UIComponentError: If table creation fails.
        ValueError: If invalid parameters are provided.
        
    Example:
        >>> table = ui_modern_table("Performance Metrics", show_line=True)
        >>> table.add_column("Metric", style="bold")
        >>> table.add_column("Value", justify="right")
        >>> table.add_row("Return", "15.2%")
    """
    try:
        if not isinstance(title, str):
            raise ValueError("title must be a string")
        
        if not title.strip():
            raise ValueError("title cannot be empty")
        
        # Use theme defaults with optional overrides
        final_title_style = title_style or THEME["table_title"]
        final_box_style = box_style or box.SIMPLE
        
        table = Table(
            title=title,
            title_style=final_title_style,
            title_justify="left",
            box=final_box_style,
            pad_edge=False,
            expand=expand,
            style=THEME["table_style"],
            header_style=THEME["table_header"],
            border_style=THEME["table_border"],
            show_lines=show_line,
        )
        
        logger.debug(f"Created modern table: '{title}' with show_line={show_line}")
        return table
        
    except Exception as e:
        raise UIComponentError(
            f"Failed to create modern table: {str(e)}",
            component="modern_table",
            cause=e
        ) from e


def ui_block_header(
    title: str,
    content: str,
    padding: Tuple[int, int] = (1, 1),
    box_style: Optional[box.Box] = None
) -> Group:
    """
    Create a block header with panel styling and spacing.
    
    Args:
        title: The title for the panel.
        content: The content to display in the panel.
        padding: Tuple of (vertical, horizontal) padding.
        box_style: Custom box style (uses ROUNDED if None).
        
    Returns:
        Rich Group object with blank lines and the styled panel.
        
    Raises:
        UIComponentError: If block header creation fails.
        ValueError: If invalid parameters are provided.
        
    Example:
        >>> header = ui_block_header("Strategy Results", "Backtest completed successfully")
        >>> console.print(header)
    """
    try:
        if not isinstance(title, str) or not title.strip():
            raise ValueError("title must be a non-empty string")
        
        if not isinstance(content, str):
            raise ValueError("content must be a string")
        
        if not isinstance(padding, tuple) or len(padding) != 2:
            raise ValueError("padding must be a tuple of (vertical, horizontal)")
        
        final_box_style = box_style or box.ROUNDED
        
        panel = Panel(
            Text(content, justify="center"),
            title=title,
            padding=padding,
            border_style=THEME["panel_border"],
            box=final_box_style
        )
        
        logger.debug(f"Created block header: '{title}'")
        return Group(Text(""), panel, Text(""))
        
    except Exception as e:
        raise UIComponentError(
            f"Failed to create block header: {str(e)}",
            component="block_header",
            cause=e
        ) from e


def ui_section_header(
    label: str,
    style: Optional[str] = None,
    characters: str = "─",
    align: str = "center"
) -> Group:
    """
    Create a styled horizontal rule with label for section separation.
    
    Args:
        label: The label to display in the center of the rule.
        style: Custom style for the rule (uses theme default if None).
        characters: Characters to use for the rule line.
        align: Text alignment ("left", "center", "right").
        
    Returns:
        Rich Group object with spacing and the styled rule.
        
    Raises:
        UIComponentError: If section header creation fails.
        ValueError: If invalid parameters are provided.
        
    Example:
        >>> header = ui_section_header("PERFORMANCE ANALYSIS")
        >>> console.print(header)
    """
    try:
        if not isinstance(label, str) or not label.strip():
            raise ValueError("label must be a non-empty string")
        
        if align not in ["left", "center", "right"]:
            raise ValueError("align must be 'left', 'center', or 'right'")
        
        final_style = style or THEME["dim"]
        
        rule = Rule(
            Text(label.upper(), style=final_style),
            style=final_style,
            characters=characters,
            align=align
        )
        
        logger.debug(f"Created section header: '{label}'")
        return Group(Text(""), Text(""), rule, Text(""))
        
    except Exception as e:
        raise UIComponentError(
            f"Failed to create section header: {str(e)}",
            component="section_header",
            cause=e
        ) from e


def ui_error_message(
    message: Union[str, Exception],
    title: str = "Error",
    show_traceback: bool = True,
    max_traceback_lines: int = 10
) -> Group:
    """
    Create a styled error message panel with optional traceback information.
    
    Args:
        message: Error message string or Exception object to display.
        title: Title for the error panel.
        show_traceback: Whether to include traceback information for exceptions.
        max_traceback_lines: Maximum number of traceback lines to show.
        
    Returns:
        Rich Group object with spacing and the error panel.
        
    Raises:
        UIComponentError: If error message creation fails.
        
    Example:
        >>> try:
        ...     raise ValueError("Something went wrong")
        ... except Exception as e:
        ...     error_panel = ui_error_message(e, show_traceback=True)
        ...     console.print(error_panel)
    """
    try:
        icon = "❌"
        formatted_message = _format_error_message(message, show_traceback, max_traceback_lines)
        
        panel = Panel(
            formatted_message,
            title=f"{icon} {title}",
            title_align="left",
            border_style=THEME["error"],
            style=THEME["error"],
            padding=(1, 2)
        )
        
        logger.debug(f"Created error message panel: '{title}'")
        return Group(Text(""), panel)
        
    except Exception as e:
        # Fallback error message if formatting fails
        fallback_panel = Panel(
            f"Error displaying error message: {str(e)}\nOriginal message: {str(message)}",
            title="❌ Error Display Error",
            title_align="left",
            border_style=THEME["error"],
            style=THEME["error"],
            padding=(1, 2)
        )
        return Group(Text(""), fallback_panel)


def _format_error_message(
    message: Union[str, Exception],
    show_traceback: bool,
    max_traceback_lines: int
) -> str:
    """
    Format an error message with optional traceback information.
    
    Args:
        message: Error message or exception to format.
        show_traceback: Whether to include traceback.
        max_traceback_lines: Maximum traceback lines to include.
        
    Returns:
        Formatted error message string.
    """
    if isinstance(message, Exception):
        exc_type = type(message).__name__
        exc_message = str(message)
        
        if show_traceback and message.__traceback__:
            try:
                # Get traceback information
                tb_lines = traceback.format_tb(message.__traceback__)
                
                # Limit traceback lines
                if len(tb_lines) > max_traceback_lines:
                    tb_lines = tb_lines[-max_traceback_lines:]
                    tb_lines.insert(0, "... (traceback truncated) ...\n")
                
                # Get relative paths for better readability
                formatted_tb = []
                for line in tb_lines:
                    try:
                        # Try to make paths relative to project root
                        project_root = Path(__file__).parent.parent
                        line = line.replace(str(project_root), ".")
                    except Exception:
                        pass  # Use original line if path conversion fails
                    formatted_tb.append(line)
                
                traceback_text = "".join(formatted_tb).rstrip()
                formatted_message = f"{exc_type}: {exc_message}\n\nTraceback:\n{traceback_text}"
            except Exception:
                # Fallback if traceback formatting fails
                formatted_message = f"{exc_type}: {exc_message}\n\n(Traceback formatting failed)"
        else:
            formatted_message = f"{exc_type}: {exc_message}"
    else:
        formatted_message = str(message)
    
    return formatted_message


def ui_success_message(message: str, title: str = "Success") -> Group:
    """
    Create a styled success message panel.
    
    Args:
        message: Success message to display.
        title: Title for the success panel.
        
    Returns:
        Rich Group object with spacing and the success panel.
        
    Example:
        >>> success_panel = ui_success_message("Strategy saved successfully!")
        >>> console.print(success_panel)
    """
    try:
        icon = "✅"
        
        panel = Panel(
            message,
            title=f"{icon} {title}",
            title_align="left",
            border_style=THEME["success"],
            style=THEME["success"],
            padding=(1, 2)
        )
        
        logger.debug(f"Created success message panel: '{title}'")
        return Group(Text(""), panel)
        
    except Exception as e:
        raise UIComponentError(
            f"Failed to create success message: {str(e)}",
            component="success_message",
            cause=e
        ) from e


def ui_warning_message(message: str, title: str = "Warning") -> Group:
    """
    Create a styled warning message panel.
    
    Args:
        message: Warning message to display.
        title: Title for the warning panel.
        
    Returns:
        Rich Group object with spacing and the warning panel.
        
    Example:
        >>> warning_panel = ui_warning_message("Cache is getting full")
        >>> console.print(warning_panel)
    """
    try:
        icon = "⚠️"
        
        panel = Panel(
            message,
            title=f"{icon} {title}",
            title_align="left",
            border_style=THEME["warning"],
            style=THEME["warning"],
            padding=(1, 2)
        )
        
        logger.debug(f"Created warning message panel: '{title}'")
        return Group(Text(""), panel)
        
    except Exception as e:
        raise UIComponentError(
            f"Failed to create warning message: {str(e)}",
            component="warning_message",
            cause=e
        ) from e


def ui_info_message(message: str, title: str = "Information") -> Group:
    """
    Create a styled information message panel.
    
    Args:
        message: Information message to display.
        title: Title for the info panel.
        
    Returns:
        Rich Group object with spacing and the info panel.
        
    Example:
        >>> info_panel = ui_info_message("Loading data from cache...")
        >>> console.print(info_panel)
    """
    try:
        icon = "ℹ️"
        
        panel = Panel(
            message,
            title=f"{icon} {title}",
            title_align="left",
            border_style=THEME["info"],
            style=THEME["info"],
            padding=(1, 2)
        )
        
        logger.debug(f"Created info message panel: '{title}'")
        return Group(Text(""), panel)
        
    except Exception as e:
        raise UIComponentError(
            f"Failed to create info message: {str(e)}",
            component="info_message",
            cause=e
        ) from e