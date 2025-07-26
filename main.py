#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily Scalper - Crypto trading strategy testing application
Main script for running backtests and analyzing performance.
"""

import sys
import os
from typing import Dict, Any, Optional, List
import warnings

# Suppress non-critical warnings
warnings.filterwarnings('ignore', category=FutureWarning)

# Add root directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Rich imports for elegant terminal formatting
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, IntPrompt, FloatPrompt, Confirm
from rich import box

from strategies import SMACrossoverStrategy
from backtest import BacktestEngine, PerformanceMetrics
from utils import DataLoader, Visualizer, StrategySaver, PeriodTranslator

# Initialize rich console
console = Console(width=120)


class DailyScalper:
    """
    Main class for the Daily Scalper application.
    """
    
    def __init__(self):
        """Initialize the application."""
        self.data_loader = DataLoader()
        self.backtest_engine = BacktestEngine()
        self.strategy_saver = StrategySaver()
        
        console.print()
        console.print(Panel(
            Text("Application successfully initialized!", justify="center"),
            title="DAILY SCALPER - TRADING STRATEGY TESTER",
            padding=(1, 1), 
            style="bold bright_green"
        ))
    
    def _display_results(self, results: Dict[str, Any]) -> None:
        """
        Display backtest results.
        
        Args:
            results: Backtest results
        """
        metrics = results['metrics']
        strategy = results['strategy']
        period = results['backtest_period']
                
        # Create a header table with key information
        header_table = Table(
            box=box.DOUBLE_EDGE, 
            style="bright_magenta", 
            border_style="blue", 
            title="[bold bright_magenta]BACKTEST CONFIGURATION[/bold bright_magenta]",
            width=120
        )
        header_table.add_column("PARAMETER", style="bold bright_magenta", width=41)
        header_table.add_column("VALUE", style="bold bright_white", width=79)
        
        # Add coin pair
        coin_pair = results.get('symbol', strategy.get('symbol', 'N/A'))
        header_table.add_row(
            "SYMBOL",
            f"[bold bright_green]{coin_pair.upper()}[/bold bright_green]"
        )

        # Add initial capital
        initial_cash = results['parameters']['initial_cash']
        header_table.add_row(
            "INITIAL CAPITAL",
            f"[bold bright_green]${initial_cash:,.2f}[/bold bright_green]"
        )

        # Add period
        period_str = f"{period['start']} → {period['end']} ({period['duration_days']} DAYS)"
        header_table.add_row(
            "PERIOD",
            f"[bold bright_green]{period_str}[/bold bright_green]"
        )
        
        # Add strategy name
        strategy_name = strategy['name'].upper()
        header_table.add_row(
            "STRATEGY",
            f"[bold bright_yellow]{strategy_name}[/bold bright_yellow]"
        )
        
        # Add strategy parameters if available
        if 'parameters' in strategy:
            params = strategy['parameters']
            param_str = " | ".join([f"{k.upper()}: {v}" for k, v in params.items()])
            header_table.add_row(
                "PARAMETERS",
                f"[bold bright_yellow]{param_str}[/bold bright_yellow]"
            )
        
        console.print(header_table)
        console.print()
        
        # Performance metrics table
        perf_metric_table = Table(
            box=box.ROUNDED, 
            style="blue", 
            border_style="blue", 
            title="[bold bright_magenta]BACKTEST RESULTS[/bold bright_magenta]",
            width=120
        )
        perf_metric_table.add_column("Performance Metric", style="bold bright_blue", width=40)
        perf_metric_table.add_column("Value", justify="right", style="bright_blue", width=20)
        perf_metric_table.add_column("Performance Metric", style="bold bright_blue", width=40)
        perf_metric_table.add_column("Value", justify="right", style="bright_blue", width=20)
        
        perf_metric_table.add_row(
            "Initial Capital", f"${results['parameters']['initial_cash']:,.2f}",
            "Final Value", f"${metrics['final_value']:,.2f}"
        )
        perf_metric_table.add_row(
            "Total Return", f"{metrics['total_return']:.2%}",
            "Alpha vs Buy & Hold", f"{metrics['alpha']:.2%}"
        )
        perf_metric_table.add_row(
            "Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}",
            "Maximum Drawdown", f"{metrics['max_drawdown']:.2%}"
        )
        perf_metric_table.add_row(
            "Volatility", f"{metrics.get('volatility', 0):.2%}",
            "VaR 95%", f"{metrics.get('var_95', 0):.2%}"
        )
        
        console.print(perf_metric_table)
        
        # Trading statistics table
        trading_metric_table = Table(box=box.ROUNDED, style="blue", border_style="blue", width=120)
        trading_metric_table.add_column("Trading Statistics", style="bold bright_blue", width=40)
        trading_metric_table.add_column("Value", justify="right", style="bright_blue", width=20)
        trading_metric_table.add_column("Trading Statistics", style="bold bright_blue", width=40)
        trading_metric_table.add_column("Value", justify="right", style="bright_blue", width=20)
        
        trading_metric_table.add_row(
            "Number of Trades", f"{metrics['total_trades']}",
            "Win Rate", f"{metrics['win_rate']:.2%}"
        )
        trading_metric_table.add_row(
            "Profit Factor", f"{metrics['profit_factor']:.2f}",
            "Average Duration", f"{metrics['avg_trade_duration']:.1f} days"
        )
        
        console.print(trading_metric_table)
        
        # Final evaluation
        is_profitable = PerformanceMetrics.is_strategy_profitable(metrics)
        status_text =  "✅ PROFITABLE STRATEGY" if is_profitable else "❌ UNPROFITABLE STRATEGY"
        status_style = "bold green" if is_profitable else "bold red"

        console.print()
        console.print(Panel(
            Text(status_text, justify="center"), 
            title=f"FINAL EVALUATION",
            padding=(1, 1), 
            style=status_style
        ))
        console.print()

    def backtest_strategy(
            self, 
            symbol: str = "BTC-USD",
            period: str = "1y",
            short_window: int = 20,
            long_window: int = 50,
            show_plots: bool = True,
            save_if_profitable: bool = True
        ) -> Dict[str, Any]:
        """
        Execute a backtest of an SMA Crossover strategy.
        
        Args:
            symbol: Crypto symbol to analyze
            period: Data period
            short_window: Short SMA period
            long_window: Long SMA period
            show_plots: Show charts
            save_if_profitable: Save if profitable
            
        Returns:
            Backtest results
        """

        console.print()
        console.print(Panel(
            Text(f"SMA Crossover {short_window}/{long_window}\nPaire : {symbol}, Période: {PeriodTranslator.get_period_description(period)}", justify="center"), 
            title=f"STRATEGY BACKTEST",
            padding=(1, 1), 
            style="bold bright_magenta"
        ))
        console.print()
        
        try:
            # 1. Loading data
            console.print("Loading data...", style="blue")
            data = self.data_loader.load_crypto_data(symbol=symbol, period=period)
            console.print(f"✅ {len(data)} data points loaded\n", style="green")
            
            # 2. Creating strategy
            console.print("Initializing strategy...", style="blue")
            strategy = SMACrossoverStrategy(
                short_window=short_window,
                long_window=long_window
            )
            console.print(f"✅ {strategy.get_description()}\n", style="green")
            
            # 3. Executing backtest
            console.print("Executing backtest...", style="blue")
            results = self.backtest_engine.run_backtest(strategy, data)
            
            # Add strategy instance for visualization
            results['strategy_instance'] = strategy
            
            # Add symbol for display
            results['symbol'] = symbol
            
            # 4. Calculate advanced metrics
            console.print("Calculating advanced metrics...", style="blue")
            results['metrics'] = PerformanceMetrics.calculate_advanced_metrics(results)
            console.print("✅ Backtest completed!\n", style="green")
            
            # 5. Display results
            self._display_results(results)
            
            # 6. Visualization
            if show_plots:
                console.print("Generating charts...", style="blue")
                Visualizer.show_all_plots(results)
            
            # 7. Save if profitable
            if save_if_profitable and PerformanceMetrics.is_strategy_profitable(results['metrics']):
                console.print("Profitable strategy detected - Saving...", style="green")
                save_id = self.strategy_saver.save_strategy_results(results)
                results['save_id'] = save_id
                console.print(f"✅ Strategy saved: {save_id}", style="green")
            elif save_if_profitable:
                console.print("❌ Unprofitable strategy - Not saved", style="yellow")
            
            return results
            
        except Exception as e:
            console.print(f"❌ Error during execution: {e}", style="red")
            raise
    
    def compare_strategies(
            self, 
            symbol: str = "BTC-USD",
            period: str = "1y"
        ) -> None:
        """
        Compare different configurations of the SMA strategy.
        
        Args:
            symbol: Symbol to analyze
            period: Data period
        """

        console.print()
        console.print(Panel(
            Text(f"SMA Crossover\nPaire : {symbol}, Période: {PeriodTranslator.get_period_description(period)}", justify="center"), 
            title=f"STRATEGY COMPARISON",
            padding=(1, 1), 
            style="bold bright_magenta"
        ))
        console.print()
        
        # Different configurations to test
        configurations = [
            (10, 30),
            (20, 50),
            (30, 70),
            (50, 100),
            (20, 100)
        ]
        
        results_list = []
        
        # Table for results
        progress_table = Table(box=box.ROUNDED, style="blue", border_style="blue", width=120)
        progress_table.add_column("Test", style="bold bright_blue", width=8)
        progress_table.add_column("Configuration", style="bold bright_blue", width=20)
        progress_table.add_column("Rendement", justify="right", style="bright_blue", width=15)
        progress_table.add_column("Sharpe", justify="right", style="bright_blue", width=12)
        progress_table.add_column("Trades", justify="right", style="bright_blue", width=12)
        progress_table.add_column("Profit Factor", justify="right", style="bright_blue", width=15)
        progress_table.add_column("Statut", justify="center", style="bright_blue", width=12)
        
        for i, (short, long) in enumerate(configurations, 1):
            try:
                results = self.backtest_strategy(
                    symbol=symbol,
                    period=period,
                    short_window=short,
                    long_window=long,
                    show_plots=False,
                    save_if_profitable=False
                )
                results_list.append(results)
                
                metrics = results['metrics']
                status = "✅" if metrics['total_return'] > 0 else "❌"
                
                progress_table.add_row(
                    f"{i}/5",
                    f"SMA {short}/{long}",
                    f"{metrics['total_return']:.2%}",
                    f"{metrics['sharpe_ratio']:.2f}",
                    f"{metrics['total_trades']}",
                    f"{metrics['profit_factor']:.2f}",
                    status
                )
                
            except Exception as e:
                progress_table.add_row(
                    f"{i}/5",
                    f"SMA {short}/{long}",
                    "❌ Erreur",
                    "-",
                    "-",
                    "-",
                    "❌"
                )
        
        console.print("\nTEST RESULTS", style="bold bright_blue")
        console.print(progress_table)
        
        # Strategy ranking
        if results_list:
            
            ranked_strategies = PerformanceMetrics.rank_strategies(results_list)
            
            ranking_table = Table(box=box.ROUNDED, style="blue", border_style="blue", width=120)
            ranking_table.add_column("Rang", style="bold bright_blue", width=10)
            ranking_table.add_column("Configuration", style="bold bright_blue", width=20)
            ranking_table.add_column("Rendement", justify="right", style="bright_blue", width=15)
            ranking_table.add_column("Sharpe", justify="right", style="bright_blue", width=12)
            ranking_table.add_column("Score", justify="right", style="bright_blue", width=12)
            ranking_table.add_column("Statut", style="bright_blue", width=20)
                        
            for i, result in enumerate(ranked_strategies, 1):
                strategy = result['strategy']
                metrics = result['metrics']
                params = strategy['parameters']
                
                is_profitable = PerformanceMetrics.is_strategy_profitable(metrics)
                status = "✅ Profitable" if is_profitable else "❌ Not profitable"
                
                ranking_table.add_row(
                    f"#{i}",
                    f"SMA {params['short_window']}/{params['long_window']}",
                    f"{metrics['total_return']:.2%}",
                    f"{metrics['sharpe_ratio']:.2f}",
                    f"{result['score']:.3f}",
                    status
                )
            
            console.print("\nSTRATEGY RANKING", style="bold bright_blue")
            console.print(ranking_table)
        else:
            console.print("❌ No valid results obtained for comparison.", style="red")
            
    def show_saved_strategies(self) -> None:
        """Display saved strategies with simple formatting."""

        status_text = "No saved strategies" if not self.strategy_saver.has_saved_strategies() else f"{len(strategies)} saved strategy(s)"

        console.print()
        console.print(Panel(
            Text(f"SMA Crossover\nPaire : {symbol}, Période: {PeriodTranslator.get_period_description(period)}", justify="center"), 
            title=f"SAVED STRATEGIES",
            padding=(1, 1), 
            style="bold bright_magenta"
        ))
        console.print()
        
        if not strategies:
            console.print("\nNo saved strategies.", style="blue")
            console.print("Run profitable backtests to create some.")
            return
        
        console.print(f"List of best strategies:", style="bold")
        
        # Table of saved strategies
        saved_table = Table(box=box.ROUNDED, style="blue", border_style="blue", width=120)
        saved_table.add_column("ID", style="bold bright_blue", width=8)
        saved_table.add_column("Stratégie", style="bold bright_blue", width=18)
        saved_table.add_column("Rendement", justify="right", style="bright_blue", width=15)
        saved_table.add_column("Sharpe", justify="right", style="bright_blue", width=12)
        saved_table.add_column("Trades", justify="right", style="bright_blue", width=12)
        saved_table.add_column("Date", style="bright_blue", width=15)
        saved_table.add_column("Statut", style="bright_blue", width=15)
        
        for i, strategy in enumerate(strategies[:10], 1):
            metrics = strategy.get('metrics', {})
            strategy_info = strategy.get('strategy', {})
            
            is_profitable = metrics.get('total_return', 0) > 0
            status = "✅ Profitable" if is_profitable else "❌ Not profitable"
            
            saved_table.add_row(
                f"#{i}",
                strategy_info.get('name', 'N/A'),
                f"{metrics.get('total_return', 0):.2%}",
                f"{metrics.get('sharpe_ratio', 0):.2f}",
                f"{metrics.get('total_trades', 0)}",
                strategy.get('timestamp', 'N/A')[:10],  # Date only
                status
            )
        
        console.print(saved_table)
        
        if len(strategies) > 10:
            console.print(f"{len(strategies) - 10} additional strategy(s) available...", style="dim")
        
        console.print("=" * 120, style="dim")


def get_user_input(prompt: str, input_type: type = str, default: Any = None) -> Any:
    """
    Utility function to get user input with validation using Rich.
    
    Args:
        prompt: Message to display
        input_type: Expected type (str, int, float)
        default: Default value
        
    Returns:
        Value entered by user
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


def show_main_menu() -> None:
    """Display the main menu."""
    console.print("\nMENU PRINCIPAL", style="bold bright_green")

    menu_table = Table(show_header=False, box=box.ROUNDED, style="bright_green", border_style="bright_green", width=120)
    menu_table.add_column("Option", style="bold bright_green", width=5)
    menu_table.add_column("Description", style="bright_green", width=115)
    
    menu_table.add_row("1", "Test a strategy")
    menu_table.add_row("2", "Compare strategies")
    menu_table.add_row("3", "View saved results")
    menu_table.add_row("4", "Configuration")
    menu_table.add_row("5", "Exit")
    
    console.print(menu_table)


def backtest_strategy_menu(app: DailyScalper) -> None:
    """Menu for testing a strategy."""
    console.print("\nSTRATEGY BACKTEST PARAMETERS\n", style="bright_green bold  underline")
    
    # Default parameters
    default_symbol = "BTC-USD"
    default_period = "1y"
    default_short = 20
    default_long = 50
    
    # Parameter collection
    symbol = get_user_input("Symbole crypto", str, default_symbol)
    if symbol is None:
        return
    
    console.print(f"Available periods: {PeriodTranslator.get_available_periods()}", style="dim")
    period = get_user_input("Period", str, default_period)
    if period is None:
        return
    
    short_window = get_user_input("Short SMA", int, default_short)
    if short_window is None:
        return
    
    long_window = get_user_input("Long SMA", int, default_long)
    if long_window is None:
        return
    
    show_plots = Confirm.ask("Show charts?", default=False)
    if show_plots is None:
        return
    
    save_if_profitable = Confirm.ask("Save if profitable?", default=True)
    if save_if_profitable is None:
        return
    
    try:
        console.print("\nStarting test...", style="bold blue")
        results = app.backtest_strategy(
            symbol=symbol,
            period=period,
            short_window=short_window,
            long_window=long_window,
            show_plots=show_plots,
            save_if_profitable=save_if_profitable
        )
        
        console.print("✅ Test completed successfully!", style="bold green")
        
    except Exception as e:
        console.print(f"❌ Error during test: {e}", style="red")
    
    Prompt.ask("\nPress Enter to continue")


def compare_strategies_menu(app: DailyScalper) -> None:
    """Menu for comparing strategies."""
    console.print("\nSTRATEGY COMPARISON PARAMETERS\n", style="bright_green bold underline")
    
    # Default parameters
    default_symbol = "BTC-USD"
    default_period = "1y"
    
    symbol = get_user_input("Symbole crypto", str, default_symbol)
    if symbol is None:
        return
    
    console.print(f"Available periods: {PeriodTranslator.get_available_periods()}", style="dim")
    period = get_user_input("Period", str, default_period)
    if period is None:
        return
    
    try:
        console.print("Starting comparison...", style="bold blue")
        app.compare_strategies(symbol=symbol, period=period)
        console.print("✅ Comparison completed!", style="bold green")
        
    except Exception as e:
        console.print(f"❌ Error during comparison: {e}", style="red")
    
    Prompt.ask("\nPress Enter to continue")


def view_saved_results_menu(app: DailyScalper) -> None:
    """Menu for viewing saved results."""
    try:
        app.show_saved_strategies()
        
    except Exception as e:
        console.print(f"❌ Error during display: {e}", style="red")
    
    Prompt.ask("\nPress Enter to continue")


def view_configuration_menu() -> None:
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
        # Import configuration parameters
        from config import (
            DEFAULT_BACKTEST_CONFIG, 
            DEFAULT_DATA_CONFIG, 
            PROFITABILITY_CRITERIA, 
            VISUALIZATION_CONFIG,
            POPULAR_CRYPTO_SYMBOLS
        )
        
        # Backtest configuration table
        backtest_table = Table(box=box.ROUNDED, style="blue", border_style="blue", width=120)
        backtest_table.add_column("Backtest Parameter", style="bold bright_blue", width=50)
        backtest_table.add_column("Value", justify="right", style="bright_blue", width=50)
        
        backtest_table.add_row("Initial Capital", f"{DEFAULT_BACKTEST_CONFIG['initial_cash']:,.2f} USD")
        backtest_table.add_row("Commission", f"{DEFAULT_BACKTEST_CONFIG['commission']:.3f} ({DEFAULT_BACKTEST_CONFIG['commission']*100:.1f}%)")
        backtest_table.add_row("Slippage", f"{DEFAULT_BACKTEST_CONFIG['slippage']:.4f} ({DEFAULT_BACKTEST_CONFIG['slippage']*100:.2f}%)")
        
        console.print("\nBacktest Parameters")
        console.print(backtest_table)
        
        # Data configuration table
        data_table = Table(box=box.ROUNDED, style="blue", border_style="blue", width=120)
        data_table.add_column("Data Parameter", style="bold bright_blue", width=50)
        data_table.add_column("Value", justify="right", style="bright_blue", width=50)
        
        data_table.add_row("Default Symbol", DEFAULT_DATA_CONFIG['default_symbol'])
        data_table.add_row("Default Period", PeriodTranslator.get_period_description(DEFAULT_DATA_CONFIG['default_period']))
        data_table.add_row("Cache Enabled", 'Yes' if DEFAULT_DATA_CONFIG['cache_enabled'] else 'No')
        data_table.add_row("Cache Duration", f"{DEFAULT_DATA_CONFIG['cache_max_age_hours']} hours")
        
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
        
        console.print(f"\nPopular crypto symbols ({len(POPULAR_CRYPTO_SYMBOLS)} available):")
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

    # Initialize application
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


if __name__ == "__main__":
    sys.exit(main())