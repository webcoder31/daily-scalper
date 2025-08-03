"""
CLI and Menu Functions for Daily Scalper

Contains all user interaction, menu, and main loop logic.
"""

import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.rule import Rule
from rich.prompt import Prompt, IntPrompt, FloatPrompt, Confirm
from rich import box

from config import (
    DEFAULT_BACKTEST_CONFIG,
    DEFAULT_DATA_CONFIG,
    PROFITABILITY_CRITERIA,
    VISUALIZATION_CONFIG,
    POPULAR_CRYPTO_SYMBOLS
)
from app import DailyScalper
from utils import PeriodTranslator
from utils.ui_components import ui_interactive_menu
from utils.ui_components import ui_section_header
from utils.ui_components import ui_error_message
from utils.ui_components import ui_modern_table
from utils.ui_components import ui_block_header
from strategies.strategy_registry import get_strategy_names
from strategies.strategy_registry import get_strategy_parameter_info
from utils.theme import THEME

UI_WIDTH = 100
console = Console(width=UI_WIDTH)


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


def backtest_strategy_menu(app: DailyScalper):
    """
    Menu for testing a strategy.
    """

    # Strategy selection
    strategy_names = get_strategy_names()
    menu_entries = [
        {"option": str(i), "desc": name}
        for i, name in enumerate(strategy_names, 1)
    ]
    strategy_choice = ui_interactive_menu(
        entries=menu_entries,
        title="Choose a strategy:",
        width=UI_WIDTH,
        default=1
    )
    selected_strategy_name = strategy_names[strategy_choice - 1]

    # Parameter collection - Symbol and Period
    console.print("\nBacktest parameters:", style=THEME["table_title"])
    symbol = get_user_input("Crypto pair", str, DEFAULT_DATA_CONFIG['default_symbol'])
    if symbol is None:
        return

    console.print(
        f"Available periods: {PeriodTranslator.get_available_periods()}",
        style=THEME["dim"]
    )
    period = get_user_input("Period", str, DEFAULT_DATA_CONFIG['default_period'])
    if period is None:
        return

    # Get strategy-specific parameters
    strategy_params = {}
    param_info = get_strategy_parameter_info(selected_strategy_name)

    console.print("\nStrategy parameters:", style=THEME["table_title"])
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
    console.print("\nOptional features:", style=THEME["table_title"])
    show_plots = Confirm.ask("Show charts?", default=False)
    if show_plots is None:
        return

    save_if_profitable = Confirm.ask("Save if profitable?", default=True)
    if save_if_profitable is None:
        return

    # Start the backtest
    console.print(f"\nTesting strategy '{selected_strategy_name}'...", style=THEME["accent"])
    try:
        app.backtest_strategy(
            selected_strategy_name,
            symbol=symbol,
            period=period,
            strategy_params=strategy_params,
            show_plots=show_plots,
            save_if_profitable=save_if_profitable
        )
    except Exception as e:
        console.print(ui_error_message(e, "Test Error"))


def compare_strategies_menu(app: DailyScalper):
    """
    Menu for comparing strategies.
    """

    # Strategy selection
    strategy_names = get_strategy_names()
    menu_entries = [
        {"option": str(i), "desc": name}
        for i, name in enumerate(strategy_names, 1)
    ]
    strategy_choice = ui_interactive_menu(
        entries=menu_entries,
        title="Choose a strategy:",
        width=UI_WIDTH,
        default=1
    )
    selected_strategy_name = strategy_names[strategy_choice - 1]

    # Default parameters
    default_symbol = "BTC-USD"
    default_period = "1y"

    symbol = get_user_input("\nCrypto pair", str, default_symbol)
    if symbol is None:
        return

    console.print(
        f"Available periods: {PeriodTranslator.get_available_periods()}",
        style=THEME["dim"]
    )
    period = get_user_input("Period", str, default_period)
    if period is None:
        return

    # Check if user wants to customize configurations
    custom_configs = Confirm.ask("\nDo you want to customize test configurations?", default=False)
    configurations = None

    if custom_configs:
        configurations = []
        console.print("\nEnter up to 5 configurations (leave blank to finish):", style=THEME["table_title"])

        param_info = get_strategy_parameter_info(selected_strategy_name)
        for i in range(1, 6):
            console.print(f"\nConfiguration #{i}:", style=THEME["table_header"])
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
        app.compare_strategies(
            selected_strategy_name,
            symbol=symbol,
            period=period,
            configurations=configurations
        )
        console.print("✅ Comparison completed!", style=THEME["success"])

    except Exception as e:
        console.print(ui_error_message(e, "Comparison Error"))


def view_saved_results_menu(app: DailyScalper):
    """
    Menu for viewing saved results.
    """

    try:
        app.show_saved_strategies()
    except Exception as e:
        console.print(ui_error_message(e, "Display Error"))


def view_app_settings_menu():
    """
    Menu for viewing application settings.
    """

    console.print(ui_block_header("Application Settings", "Current configuration parameters (config.py)"))

    try:
        # Backtest configuration table
        backtest_table = ui_modern_table("Backtest Parameters")
        backtest_table.add_column("Parameter", width=48)
        backtest_table.add_column("Value", justify="right", style="bold", width=48)

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

        console.print(backtest_table)

        # Data configuration table
        data_table = ui_modern_table("Data Configuration")
        data_table.add_column("Parameter", width=48)
        data_table.add_column("Value", justify="right", style="bold", width=48)

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

        console.print(data_table)

        # Profitability criteria table
        profit_table = ui_modern_table("Profitability Criteria")
        profit_table.add_column("Criterion", width=48)
        profit_table.add_column("Value", justify="right", style="bold", width=48)

        profit_table.add_row("Minimum Return", f"{PROFITABILITY_CRITERIA['min_return']:.1%}")
        profit_table.add_row("Minimum Sharpe Ratio", f"{PROFITABILITY_CRITERIA['min_sharpe']:.1f}")
        profit_table.add_row("Maximum Drawdown", f"{PROFITABILITY_CRITERIA['max_drawdown']:.1%}")
        profit_table.add_row("Minimum Trades", f"{PROFITABILITY_CRITERIA['min_trades']}")

        console.print(profit_table)

        # # Popular symbols
        # symbols_text = ", ".join(POPULAR_CRYPTO_SYMBOLS[:10])
        # if len(POPULAR_CRYPTO_SYMBOLS) > 10:
        #     symbols_text += f"\n... and {len(POPULAR_CRYPTO_SYMBOLS) - 10} others"

        # console.print(
        #     f"\nPopular crypto symbols ({len(POPULAR_CRYPTO_SYMBOLS)} available):"
        # )
        # console.print(symbols_text)

        # Modification instructions
        console.print("\nTo modify the configuration:\n", style=THEME["accent"] + " underline")
        console.print("1. Edit the 'config.py' file")
        console.print("2. Restart the application")
        console.print("3. The new parameters will be applied")

    except Exception as e:
        console.print(f"❌ Error reading configuration: {e}", style=THEME["error"])


def main():
    """
    Main function with interactive menu.
    """

    app = DailyScalper()

    while True:
        try:
            menu_entries = [
                {"option": "1", "desc": "Test a single strategy configuration"},
                {"option": "2", "desc": "Compare strategy configurations"},
                {"option": "3", "desc": "View saved strategies"},
                {"option": "4", "desc": "View settings"},
                {"option": "5", "desc": "Exit"},
            ]
            choice = ui_interactive_menu(
                entries=menu_entries,
                title="Select an option:",
                width=UI_WIDTH,
                default=1
            )

            if choice == 1:
                backtest_strategy_menu(app)
            elif choice == 2:
                compare_strategies_menu(app)
            elif choice == 3:
                view_saved_results_menu(app)
            elif choice == 4:
                view_app_settings_menu()
            elif choice == 5:
                break
            else:
                console.print(ui_error_message("Invalid option!"))

        except KeyboardInterrupt:
            console.print("\nUser requested app interruption (CTRL+C)", style=THEME["warning"])
            break
        except Exception as e:
            console.print(f"❌ Unexpected error: {e}", style=THEME["error"])

        Prompt.ask("\nPress Enter to continue")
        print()

    console.print("\nGoodbye.\n", style=THEME["highlight"])

    return 0