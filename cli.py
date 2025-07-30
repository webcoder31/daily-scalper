"""
CLI and Menu Functions for Daily Scalper

Contains all user interaction, menu, and main loop logic.
"""

import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, IntPrompt, FloatPrompt, Confirm
from rich import box

from app import DailyScalper
from utils import PeriodTranslator
from strategies.strategy_registry import get_strategy_names
from strategies.strategy_registry import get_strategy_parameter_info

console = Console(width=120)

def get_user_input(prompt: str, input_type: type = str, default=None):
    """
    Utility function to get user input with validation using Rich.
    """
    try:
        if input_type == str:
            return Prompt.ask(prompt, default=default)
        elif input_type == int:
            return IntPrompt.ask(prompt, default=default)
        elif input_type == float:
            return FloatPrompt.ask(prompt, default=default)
        else:
            return Prompt.ask(prompt, default=default)
    except KeyboardInterrupt:
        console.print("\n⏹️ Operation cancelled", style="yellow")
        return None

def show_main_menu():
    """Display the main menu."""
    console.print("\nMAIN MENU", style="bold bright_green")

    menu_table = Table(
        show_header=False,
        box=box.ROUNDED,
        style="bright_green",
        border_style="bright_green",
        width=120
    )
    menu_table.add_column("Option", style="bold bright_green", width=5)
    menu_table.add_column("Description", style="bright_green", width=115)

    menu_table.add_row("1", "Test a single strategy configuration")
    menu_table.add_row("2", "Compare different strategy configurations")
    menu_table.add_row("3", "View saved profitable strategies")
    menu_table.add_row("4", "View application settings")
    menu_table.add_row("5", "Exit application")

    console.print(menu_table)

def backtest_strategy_menu(app: DailyScalper):
    """Menu for testing a strategy."""
    console.print("\nSTRATEGY BACKTEST PARAMETERS\n", style="bright_green bold underline")

    # Get available strategies
    strategy_names = get_strategy_names()

    # Default parameters
    default_symbol = "BTC-USD"
    default_period = "1y"

    # Create strategy selection options
    strategy_table = Table(
        show_header=False,
        box=box.ROUNDED,
        style="bright_green",
        border_style="bright_green",
        width=120
    )
    strategy_table.add_column("ID", style="bold bright_green", width=5)
    strategy_table.add_column("Strategy", style="bright_green", width=115)

    for i, strategy_name in enumerate(strategy_names, 1):
        strategy_table.add_row(f"{i}", strategy_name)

    console.print("Available strategies:")
    console.print(strategy_table)

    # Strategy selection
    strategy_choice = get_user_input("Select strategy (number)", int, 1)
    if strategy_choice is None or strategy_choice < 1 or strategy_choice > len(strategy_names):
        console.print("Invalid strategy selection.", style="red")
        return

    # Get selected strategy name (short description)
    selected_strategy_name = strategy_names[strategy_choice - 1]
    console.print(f"Selected strategy: {selected_strategy_name}", style="bold bright_blue")

    # Parameter collection - Symbol and Period
    symbol = get_user_input("Crypto pair", str, default_symbol)
    if symbol is None:
        return

    console.print(
        f"Available periods: {PeriodTranslator.get_available_periods()}",
        style="dim"
    )
    period = get_user_input("Period", str, default_period)
    if period is None:
        return

    # Get strategy-specific parameters
    strategy_params = {}
    param_info = get_strategy_parameter_info(selected_strategy_name)

    console.print("\nStrategy parameters:", style="bold bright_blue")
    for param_name, param_config in param_info.items():
        param_type = param_config.get('type', str)
        default_value = param_config.get('default')
        description = param_config.get('description', param_name)

        # Format the prompt with description and range if available
        range_info = ""
        if 'range' in param_config:
            min_val, max_val = param_config['range']
            range_info = f" (range: {min_val}-{max_val})"

        prompt = f"{description}{range_info}"

        # Get user input with appropriate type
        value = get_user_input(prompt, param_type, default_value)
        if value is None:  # User cancelled
            return

        strategy_params[param_name] = value

    # Chart and save options
    show_plots = Confirm.ask("Show charts?", default=False)
    if show_plots is None:
        return

    save_if_profitable = Confirm.ask("Save if profitable?", default=True)
    if save_if_profitable is None:
        return

    try:
        console.print("\nStarting test...", style="bold blue")
        results = app.backtest_strategy(
            strategy_name=selected_strategy_name,
            symbol=symbol,
            period=period,
            strategy_params=strategy_params,
            show_plots=show_plots,
            save_if_profitable=save_if_profitable
        )

        console.print("✅ Test completed successfully!", style="bold green")

    except Exception as e:
        console.print(f"❌ Error during test: {e}", style="red")

    Prompt.ask("\nPress Enter to continue")

def compare_strategies_menu(app: DailyScalper):
    """Menu for comparing strategies."""
    console.print("\nSTRATEGY COMPARISON PARAMETERS\n", style="bright_green bold underline")

    # Get available strategies
    strategy_names = get_strategy_names()

    # Create strategy selection options
    strategy_table = Table(
        show_header=False,
        box=box.ROUNDED,
        style="bright_green",
        border_style="bright_green",
        width=120
    )
    strategy_table.add_column("ID", style="bold bright_green", width=5)
    strategy_table.add_column("Strategy", style="bright_green", width=115)

    for i, strategy_name in enumerate(strategy_names, 1):
        strategy_table.add_row(f"{i}", strategy_name)

    console.print("Available strategies:")
    console.print(strategy_table)

    # Strategy selection
    strategy_choice = get_user_input("Select strategy to compare (number)", int, 1)
    if strategy_choice is None or strategy_choice < 1 or strategy_choice > len(strategy_names):
        console.print("Invalid strategy selection.", style="red")
        return

    # Get selected strategy name (short description)
    selected_strategy_name = strategy_names[strategy_choice - 1]
    console.print(f"Selected strategy: {selected_strategy_name}", style="bold bright_blue")

    # Default parameters
    default_symbol = "BTC-USD"
    default_period = "1y"

    symbol = get_user_input("Crypto pair", str, default_symbol)
    if symbol is None:
        return

    console.print(
        f"Available periods: {PeriodTranslator.get_available_periods()}",
        style="dim"
    )
    period = get_user_input("Period", str, default_period)
    if period is None:
        return

    # Check if user wants to customize configurations
    custom_configs = Confirm.ask("Do you want to customize test configurations?", default=False)
    configurations = None

    if custom_configs:
        configurations = []
        console.print("\nEnter up to 5 configurations (leave blank to finish):", style="bold bright_blue")

        param_info = get_strategy_parameter_info(selected_strategy_name)
        for i in range(1, 6):
            console.print(f"\nConfiguration #{i}:", style="bold")
            config = {}

            for param_name, param_config in param_info.items():
                param_type = param_config.get('type', str)
                default_value = param_config.get('default')
                description = param_config.get('description', param_name)

                value = get_user_input(f"{description}", param_type, default_value)
                if value is None:
                    break
                config[param_name] = value

            if not config:
                break

            configurations.append(config)
            if i < 5 and not Confirm.ask("Add another configuration?", default=True):
                break

    try:
        console.print("Starting comparison...", style="bold blue")
        app.compare_strategies(
            strategy_name=selected_strategy_name,
            symbol=symbol,
            period=period,
            configurations=configurations
        )
        console.print("✅ Comparison completed!", style="bold green")

    except Exception as e:
        console.print(f"❌ Error during comparison: {e}", style="red")

    Prompt.ask("\nPress Enter to continue")

def view_saved_results_menu(app: DailyScalper):
    """Menu for viewing saved results."""
    try:
        app.show_saved_strategies()
    except Exception as e:
        console.print(f"❌ Error during display: {e}", style="red")
    Prompt.ask("\nPress Enter to continue")

def view_configuration_menu():
    """Configuration menu."""
    console.print()
    console.print(Panel(
        Text(f"Current configuration defined in config.py", justify="center"),
        title=f"CONFIGURATION",
        padding=(1, 1),
        style="bold bright_magenta"
    ))
    console.print()

    try:
        from config import (
            DEFAULT_BACKTEST_CONFIG,
            DEFAULT_DATA_CONFIG,
            PROFITABILITY_CRITERIA,
            VISUALIZATION_CONFIG,
            POPULAR_CRYPTO_SYMBOLS
        )

        # Backtest configuration table
        backtest_table = Table(
            box=box.ROUNDED,
            style="blue",
            border_style="blue",
            width=120
        )
        backtest_table.add_column("Backtest Parameter", style="bold bright_blue", width=50)
        backtest_table.add_column("Value", justify="right", style="bright_blue", width=50)

        backtest_table.add_row(
            "Initial Capital", 
            f"{DEFAULT_BACKTEST_CONFIG['initial_cash']:,.2f} USD"
        )
        backtest_table.add_row(
            "Commission", 
            f"{DEFAULT_BACKTEST_CONFIG['commission']:.3f} ({DEFAULT_BACKTEST_CONFIG['commission']*100:.1f}%)"
        )
        backtest_table.add_row(
            "Slippage", 
            f"{DEFAULT_BACKTEST_CONFIG['slippage']:.4f} ({DEFAULT_BACKTEST_CONFIG['slippage']*100:.2f}%)"
        )

        console.print("\nBacktest Parameters")
        console.print(backtest_table)

        # Data configuration table
        data_table = Table(box=box.ROUNDED, style="blue", border_style="blue", width=120)
        data_table.add_column("Data Parameter", style="bold bright_blue", width=50)
        data_table.add_column("Value", justify="right", style="bright_blue", width=50)

        data_table.add_row(
            "Default Symbol", 
            DEFAULT_DATA_CONFIG['default_symbol']
        )
        data_table.add_row(
            "Default Period",
            PeriodTranslator.get_period_description(DEFAULT_DATA_CONFIG['default_period'])
        )
        data_table.add_row(
            "Cache Enabled", 
            'Yes' if DEFAULT_DATA_CONFIG['cache_enabled'] else 'No'
        )
        data_table.add_row(
            "Cache Duration", 
            f"{DEFAULT_DATA_CONFIG['cache_max_age_hours']} hours"
        )

        console.print("\nData Configuration")
        console.print(data_table)

        # Profitability criteria table
        profit_table = Table(box=box.ROUNDED, style="blue", border_style="blue", width=120)
        profit_table.add_column("Profitability Criterion", style="bold bright_blue", width=50)
        profit_table.add_column("Value", justify="right", style="bright_blue", width=50)

        profit_table.add_row("Minimum Return", f"{PROFITABILITY_CRITERIA['min_return']:.1%}")
        profit_table.add_row("Minimum Sharpe Ratio", f"{PROFITABILITY_CRITERIA['min_sharpe']:.1f}")
        profit_table.add_row("Maximum Drawdown", f"{PROFITABILITY_CRITERIA['max_drawdown']:.1%}")
        profit_table.add_row("Minimum Trades", f"{PROFITABILITY_CRITERIA['min_trades']}")

        console.print("\nProfitability Criteria")
        console.print(profit_table)

        # Popular symbols
        symbols_text = ", ".join(POPULAR_CRYPTO_SYMBOLS[:10])
        if len(POPULAR_CRYPTO_SYMBOLS) > 10:
            symbols_text += f"\n... and {len(POPULAR_CRYPTO_SYMBOLS) - 10} others"

        console.print(
            f"\nPopular crypto symbols ({len(POPULAR_CRYPTO_SYMBOLS)} available):"
        )
        console.print(symbols_text, style="blue")

        # Modification instructions
        console.print("\nTo modify the configuration:", style="blue")
        console.print("1. Edit the 'config.py' file")
        console.print("2. Restart the application")
        console.print("3. The new parameters will be applied")

    except Exception as e:
        console.print(f"❌ Error reading configuration: {e}", style="red")

    Prompt.ask("\nPress Enter to continue")

def main():
    """Main function with interactive menu."""
    app = DailyScalper()

    while True:
        try:
            show_main_menu()

            choice = get_user_input("Choose an option (1-5)", str)

            if choice is None:  # Ctrl+C
                break
            elif choice == "1":
                backtest_strategy_menu(app)
            elif choice == "2":
                compare_strategies_menu(app)
            elif choice == "3":
                view_saved_results_menu(app)
            elif choice == "4":
                view_configuration_menu()
            elif choice == "5":
                console.print("👋 Goodbye!", style="bold green")
                break
            else:
                console.print("❌ Invalid option. Please choose between 1 and 5.", style="red")
                Prompt.ask("Press Enter to continue")

        except KeyboardInterrupt:
            console.print("\n\nUser requested stop", style="yellow")
            break
        except Exception as e:
            console.print(f"❌ Unexpected error: {e}", style="red")
            Prompt.ask("Press Enter to continue")

    return 0