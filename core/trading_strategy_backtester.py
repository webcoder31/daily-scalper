"""
Trading Strategy Backtester Application Core Logic.

This module contains the TradingStrategyBacktester class which serves as the main application
controller for running backtests, comparing strategies, and managing results.
It provides a comprehensive interface for cryptocurrency trading strategy analysis.
"""

import os
import sys
import warnings
from typing import Dict, Any, List, Optional, Union

# Suppress non-critical warnings for cleaner output
warnings.filterwarnings('ignore', category=FutureWarning)

# Add root directory to Python path for module imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Rich imports for elegant terminal formatting
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

# Application imports
from backtesting.strategy_backtest_engine import StrategyBacktestEngine
from backtesting.performance_analyzer import PerformanceAnalyzer
from market_data.market_data_provider import MarketDataProvider
from visualization.backtest_chart_generator import BacktestChartGenerator
from persistence.strategy_results_persistence import StrategyResultsPersistence
from market_data.period_translator import PeriodTranslator
from strategies.base.strategy_registry import (
    create_strategy,
    get_strategy_parameter_info,
    get_strategy_class
)
from ui.theme import THEME
from ui.components import (
    ui_interactive_menu,
    ui_section_header,
    ui_error_message,
    ui_modern_table,
    ui_block_header
)

# Initialize rich console with consistent width
UI_WIDTH: int = 100
console = Console(width=UI_WIDTH)


class TradingStrategyBacktesterError(Exception):
    """Base exception class for Trading Strategy Backtester application errors."""
    pass


class DataLoadError(TradingStrategyBacktesterError):
    """Exception raised when data loading fails."""
    pass


class StrategyError(TradingStrategyBacktesterError):
    """Exception raised when strategy operations fail."""
    pass


class BacktestError(TradingStrategyBacktesterError):
    """Exception raised when backtesting operations fail."""
    pass


class TradingStrategyBacktester:
    """
    Main application class for the Trading Strategy Backtester cryptocurrency trading strategy analyzer.
    
    This class provides comprehensive functionality for backtesting trading strategies,
    comparing different configurations, and managing profitable strategy results.
    It serves as the primary interface between the user and the underlying
    backtesting engine, data loading, and visualization components.
    """


    def __init__(self) -> None:
        """
        Initialize the Trading Strategy Backtester application.
        
        Sets up all required components including data loader, backtest engine,
        and strategy saver. Displays initialization confirmation to the user.
        
        Raises:
            TradingStrategyBacktesterError: If initialization of core components fails.
        """
        try:
            self.data_loader = MarketDataProvider()
            self.backtest_engine = StrategyBacktestEngine()
            self.strategy_saver = StrategyResultsPersistence()
            
            console.print(ui_block_header(
                "Trading Strategy Backtester", 
                "Application successfully initialized."
            ))
            
        except Exception as e:
            raise TradingStrategyBacktesterError(f"Failed to initialize application: {str(e)}") from e


    def render_backtest_summary(self, results: Dict[str, Any]) -> None:
        """
        Display comprehensive backtest results in formatted tables.
        
        Creates and displays multiple tables showing configuration details,
        performance metrics, trading statistics, and final evaluation.
        
        Args:
            results: Complete backtest results dictionary containing metrics,
                    strategy information, and performance data.
        
        Raises:
            KeyError: If required keys are missing from results dictionary.
        """
        try:
            metrics = results['metrics']
            strategy = results['strategy']
            period = results['backtest_period']
            symbol = results['symbol']
            
            # Create header table with key configuration information
            header_table = ui_modern_table("Tested Configuration")
            header_table.add_column("Setting", width=48)
            header_table.add_column("Value", width=48)

            # Add cryptocurrency pair
            header_table.add_row(
                "Crypto Pair",
                f"[{THEME['success']}]{symbol}[/{THEME['success']}]"
            )

            # Add initial capital
            initial_cash = results['parameters']['initial_cash']
            header_table.add_row(
                "Initial Capital",
                f"[{THEME['success']}]${initial_cash:,.2f}[/{THEME['success']}]"
            )

            # Add backtest period
            period_str = f"{period['start']} → {period['end']} ({period['duration_days']} days)"
            header_table.add_row(
                "Backtest Period",
                f"[{THEME['success']}]{period_str}[/{THEME['success']}]"
            )

            # Add strategy name
            strategy_name = strategy['name'].upper()
            header_table.add_row(
                "Strategy",
                f"[{THEME['highlight']}]{strategy_name}[/{THEME['highlight']}]"
            )

            # Add strategy parameters if available
            if 'parameters' in strategy and strategy['parameters']:
                params = strategy['parameters']
                param_str = "\n".join([f"{k}: {v}" for k, v in params.items()])
                header_table.add_row(
                    "Parameters",
                    f"[{THEME['accent']}]{param_str}[/{THEME['accent']}]"
                )

            console.print(header_table)

            # Performance metrics table
            perf_metric_table = ui_modern_table("Performance Metrics")
            perf_metric_table.add_column("Metric", width=24)
            perf_metric_table.add_column("Value", justify="right", width=24)
            perf_metric_table.add_column("Metric", width=24)
            perf_metric_table.add_column("Value", justify="right", width=24)

            perf_metric_table.add_row(
                "Initial Capital", f"[bold]${results['parameters']['initial_cash']:,.2f}[/bold]",
                "Final Value", f"[bold]${metrics['final_value']:,.2f}[/bold]"
            )
            perf_metric_table.add_row(
                "Total Return", f"[bold]{metrics['total_return']:.2%}[/bold]",
                "Alpha vs Buy & Hold", f"[bold]{metrics['alpha']:.2%}[/bold]"
            )
            perf_metric_table.add_row(
                "Sharpe Ratio", f"[bold]{metrics['sharpe_ratio']:.2f}[/bold]",
                "Maximum Drawdown", f"[bold]{metrics['max_drawdown']:.2%}[/bold]"
            )
            perf_metric_table.add_row(
                "Volatility", f"[bold]{metrics.get('volatility', 0):.2%}[/bold]",
                "VaR 95%", f"[bold]{metrics.get('var_95', 0):.2%}[/bold]"
            )

            console.print(perf_metric_table)

            # Trading statistics table
            trading_metric_table = ui_modern_table("Trading Statistics")
            trading_metric_table.add_column("Statistic", width=24)
            trading_metric_table.add_column("Value", justify="right", width=24)
            trading_metric_table.add_column("Statistic", width=24)
            trading_metric_table.add_column("Value", justify="right", width=24)

            trading_metric_table.add_row(
                "Number of Trades", f"[bold]{metrics['total_trades']}[/bold]",
                "Win Rate", f"[bold]{metrics['win_rate']:.2%}[/bold]"
            )
            trading_metric_table.add_row(
                "Profit Factor", f"[bold]{metrics['profit_factor']:.2f}[/bold]",
                "Average Duration", f"[bold]{metrics['avg_trade_duration']:.1f} days[/bold]"
            )

            console.print(trading_metric_table)

            # Final profitability evaluation
            is_profitable = PerformanceAnalyzer.meets_profitability_criteria(metrics)
            tested_strategy = f"{results['strategy_label']} for {results['symbol']}"
            status_text = f"✅ {tested_strategy} is PROFITABLE" if is_profitable \
                         else f"❌ {tested_strategy} is NOT PROFITABLE"
            status_style = THEME["success"] if is_profitable else THEME["error"]

            print()
            console.print(Text(status_text, style=status_style))
            print()
            
        except KeyError as e:
            raise TradingStrategyBacktesterError(f"Missing required data in results: {str(e)}") from e
        except Exception as e:
            raise TradingStrategyBacktesterError(f"Error displaying results: {str(e)}") from e


    def execute_strategy_backtest(
        self,
        strategy_name: str,
        symbol: str = "BTC-USD",
        period: str = "1y",
        strategy_parameters: Optional[Dict[str, Any]] = None,
        display_charts: bool = True,
        auto_save_profitable_results: bool = True,
        batch_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a comprehensive backtest of a trading strategy.
        
        This method performs a complete backtesting workflow including data loading,
        strategy initialization, backtest execution, metrics calculation, result
        display, visualization, and optional saving of profitable strategies.
        
        Args:
            strategy_name: Name of the strategy class to instantiate and test.
            symbol: Cryptocurrency symbol to analyze (e.g., 'BTC-USD').
            period: Time period for historical data (e.g., '1y', '6mo', '3mo').
            strategy_parameters: Dictionary of parameters to configure the strategy.
                           If None, default parameters will be used.
            display_charts: Whether to display interactive charts and visualizations.
            auto_save_profitable_results: Whether to automatically save profitable strategies.
            batch_mode: Whether running in batch mode (affects display verbosity).
        
        Returns:
            Dictionary containing complete backtest results including:
            - metrics: Performance metrics and statistics
            - strategy: Strategy configuration and parameters
            - portfolio: Portfolio object from vectorbt
            - backtest_period: Period information
            - symbol: Tested cryptocurrency symbol
            - strategy_instance: Strategy object instance
            - strategy_label: Human-readable strategy description
        
        Raises:
            DataLoadError: If data loading fails or no data is available.
            StrategyError: If strategy creation or configuration fails.
            BacktestError: If the backtesting process encounters errors.
        """
        # Initialize strategy parameters
        if strategy_parameters is None:
            strategy_parameters = {}

        try:
            # Get parameter information for display
            param_info = get_strategy_parameter_info(strategy_name)
            
            # Build parameter description for user display
            param_desc = []
            for name, value in strategy_parameters.items():
                if name in param_info:
                    param_desc.append(f"{name}: {value}")

            param_str = ", ".join(param_desc) if param_desc else "Default parameters"

            # Display backtest header
            if not batch_mode:
                console.print(ui_block_header(
                    "Strategy Backtest",
                    f"{strategy_name}\n"
                    f"Crypto pair: {symbol}, "
                    f"Period: {PeriodTranslator.get_period_description(period)}\n"
                    f"{param_str}"
                ))
            else:
                console.print(ui_section_header(f"Running backtest with {param_str}"))

            # Step 1: Load historical data
            console.print("Loading data...", style=THEME["table_border"])
            try:
                data = self.data_loader.fetch_cryptocurrency_data(symbol=symbol, period=period)
                if data.empty:
                    raise DataLoadError(f"No data available for {symbol} in period {period}")
                    
                console.print(
                    f"✅ {len(data)} data points loaded "
                    f"from {data.index[0].strftime('%Y-%m-%d')} "
                    f"to {data.index[-1].strftime('%Y-%m-%d')}\n",
                    style=THEME["success"]
                )
            except Exception as e:
                console.print(ui_error_message(
                    f"Failed to load data: {str(e)}", 
                    "Data Error"
                ))
                raise DataLoadError(f"Data loading failed: {str(e)}") from e

            # Step 2: Create and initialize strategy
            console.print("Initializing strategy...", style=THEME["table_border"])
            try:
                strategy = create_strategy(strategy_name, **strategy_parameters)
                console.print("✅ Strategy ready\n", style=THEME["success"])
                console.print(f"{strategy.get_explanation()}\n", style=THEME["success"])
            except Exception as e:
                raise StrategyError(f"Strategy initialization failed: {str(e)}") from e

            # Step 3: Execute backtest
            console.print("Executing backtest...", style=THEME["table_border"])
            try:
                results = self.backtest_engine.execute_strategy_evaluation(strategy, data)
                console.print("✅ Backtest completed\n", style=THEME["success"])
            except Exception as e:
                raise BacktestError(f"Backtest execution failed: {str(e)}") from e

            # Add additional information to results
            results['strategy_instance'] = strategy
            results['strategy_label'] = strategy.get_short_description(strategy_parameters)
            results['symbol'] = symbol

            # Step 4: Calculate advanced performance metrics
            console.print("Calculating advanced metrics...", style=THEME["table_border"])
            try:
                results['metrics'] = PerformanceAnalyzer.compute_extended_performance_stats(results)
                console.print("✅ Metrics computed\n", style=THEME["success"])
            except Exception as e:
                console.print(f"Warning: Advanced metrics calculation failed: {str(e)}", 
                            style=THEME["warning"])

            # Step 5: Display comprehensive results
            self.render_backtest_summary(results)

            # Step 6: Generate visualizations
            if display_charts:
                try:
                    console.print("Generating charts...", style=THEME["accent"])
                    BacktestChartGenerator.show_all_plots(results)
                except Exception as e:
                    console.print(f"Warning: Visualization failed: {str(e)}", 
                                style=THEME["warning"])

            # Step 7: Save profitable strategies
            if auto_save_profitable_results and PerformanceAnalyzer.meets_profitability_criteria(results['metrics']):
                try:
                    console.print("\nProfitable strategy detected - Saving...", 
                                style=THEME["dim"])
                    save_id = self.strategy_saver.save_strategy_results(results)
                    results['save_id'] = save_id
                    console.print(f"✅ Strategy saved: {save_id}", style=THEME["success"])
                except Exception as e:
                    console.print(f"Warning: Failed to save strategy: {str(e)}", 
                                style=THEME["warning"])
            elif auto_save_profitable_results:
                console.print("⚠️  Unprofitable strategy - Not saved", style=THEME["warning"])

            return results

        except (DataLoadError, StrategyError, BacktestError):
            # Re-raise specific exceptions
            raise
        except Exception as e:
            # Catch any unexpected errors
            raise TradingStrategyBacktesterError(f"Unexpected error during backtesting: {str(e)}") from e


    def analyze_strategy_variants(
        self,
        strategy_name: str,
        symbol: str = "BTC-USD",
        period: str = "1y",
        configurations: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Compare multiple configurations of a trading strategy.
        
        This method runs backtests for different parameter configurations of the
        same strategy and presents a comprehensive comparison including rankings
        and performance analysis.
        
        Args:
            strategy_name: Name of the strategy class to test.
            symbol: Cryptocurrency symbol to analyze.
            period: Time period for historical data.
            configurations: List of parameter dictionaries to test. If None,
                          uses predefined configurations from the strategy class.
        
        Raises:
            StrategyError: If strategy class cannot be found or configurations fail.
            TradingStrategyBacktesterError: If comparison process encounters errors.
        """
        try:
            # Get configurations from strategy class if none provided
            if configurations is None:
                strategy_class = get_strategy_class(strategy_name)
                if strategy_class:
                    configurations = strategy_class.get_predefined_configurations()
                else:
                    raise StrategyError(f"Strategy class '{strategy_name}' not found")
                    
                if not configurations:
                    configurations = [{}]  # Use default configuration

            console.print(ui_block_header(
                "Strategy Comparison",
                f"{strategy_name}\n"
                f"Crypto pair: {symbol}, "
                f"Period: {PeriodTranslator.get_period_description(period)}"
            ))

            results_list: List[Dict[str, Any]] = []

            # Create progress table for real-time results
            progress_table = ui_modern_table("Comparison Results")
            progress_table.add_column("Test", style=THEME["table_header"], width=8)
            progress_table.add_column("Configuration", width=32)
            progress_table.add_column("Return", justify="right", width=12)
            progress_table.add_column("Sharpe", justify="right", width=10)
            progress_table.add_column("Trades", justify="right", width=10)
            progress_table.add_column("Profit Factor", justify="right", width=14)
            progress_table.add_column("Status", justify="center", width=14)

            # Run backtests for each configuration
            for i, strategy_parameters in enumerate(configurations, 1):
                try:
                    # Get strategy description for display
                    strategy_class = get_strategy_class(strategy_name)
                    if strategy_class:
                        strategy_short_desc = strategy_class.get_short_description(strategy_parameters)
                    else:
                        strategy_short_desc = ", ".join([f"{k}={v}" for k, v in strategy_parameters.items()])

                    # Run backtest for this configuration
                    results = self.execute_strategy_backtest(
                        strategy_name,
                        symbol=symbol,
                        period=period,
                        strategy_parameters=strategy_parameters,
                        display_charts=False,
                        auto_save_profitable_results=False,
                        batch_mode=True
                    )
                    
                    if results:  # Only add if backtest was successful
                        results_list.append(results)
                        metrics = results['metrics']
                        status = "✅" if metrics['total_return'] > 0 else "❌"

                        progress_table.add_row(
                            f"{i}/{len(configurations)}",
                            strategy_short_desc,
                            f"{metrics['total_return']:.2%}",
                            f"{metrics['sharpe_ratio']:.2f}",
                            f"{metrics['total_trades']}",
                            f"{metrics['profit_factor']:.2f}",
                            status
                        )
                    else:
                        progress_table.add_row(
                            f"{i}/{len(configurations)}",
                            strategy_short_desc,
                            "❌ Failed",
                            "-",
                            "-",
                            "-",
                            "❌"
                        )

                except Exception as e:
                    console.print(f"Error testing configuration {i}: {str(e)}", 
                                style=THEME["error"])
                    progress_table.add_row(
                        f"{i}/{len(configurations)}",
                        "Configuration Error",
                        "❌ Error",
                        "-",
                        "-",
                        "-",
                        "❌"
                    )

            # Display comparison results
            console.print(ui_section_header(f"Comparison Results for Strategy {strategy_name}"))
            console.print(progress_table)

            # Generate and display strategy rankings
            if results_list:
                self._display_strategy_rankings(strategy_name, results_list)
            else:
                console.print("❌ No valid results obtained for comparison.", 
                            style=THEME["error"])

        except StrategyError:
            raise
        except Exception as e:
            raise TradingStrategyBacktesterError(f"Strategy comparison failed: {str(e)}") from e


    def _display_strategy_rankings(
        self,
        strategy_name: str,
        results_list: List[Dict[str, Any]]
    ) -> None:
        """
        Display ranked comparison results for strategies.
        
        Args:
            strategy_name: Name of the strategy being compared.
            results_list: List of backtest results to rank and display.
        """
        try:
            ranked_strategies = PerformanceAnalyzer.sort_strategies_by_performance(results_list)

            ranking_table = ui_modern_table("Strategy Ranking")
            ranking_table.add_column("Rank", style=THEME["table_header"], width=5)
            ranking_table.add_column("Configuration", width=25)
            ranking_table.add_column("Return", justify="right", width=15)
            ranking_table.add_column("Sharpe", justify="right", width=15)
            ranking_table.add_column("Score", justify="right", width=15)
            ranking_table.add_column("Status", width=20)

            for i, result in enumerate(ranked_strategies, 1):
                strategy = result['strategy']
                metrics = result['metrics']
                params = strategy['parameters']

                is_profitable = PerformanceAnalyzer.meets_profitability_criteria(metrics)
                status = "✅ Profitable" if is_profitable else "❌ Not profitable"

                # Get configuration display string
                strategy_class = get_strategy_class(strategy_name)
                if strategy_class:
                    config_display = strategy_class.get_short_description(params)
                else:
                    config_display = ", ".join([f"{k}={v}" for k, v in params.items()])

                ranking_table.add_row(
                    f"#{i}",
                    config_display,
                    f"{metrics['total_return']:.2%}",
                    f"{metrics['sharpe_ratio']:.2f}",
                    f"{result['ranking_score']:.3f}",
                    status
                )

            console.print(ranking_table)
            
        except Exception as e:
            console.print(f"Error displaying rankings: {str(e)}", style=THEME["error"])


    def display_saved_results(self) -> None:
        """
        Display a comprehensive list of saved profitable strategies.
        
        Retrieves and displays all previously saved profitable strategies
        with their key performance metrics and configuration details.
        
        Raises:
            TradingStrategyBacktesterError: If retrieving saved strategies fails.
        """
        try:
            # Retrieve list of saved strategies
            strategies = self.strategy_saver.list_saved_strategies()

            # Create status message
            status_text = ("No saved strategies available." if not strategies 
                          else f"{len(strategies)} profitable strategies saved.")

            console.print(ui_block_header("Saved Strategies", status_text))
            
            if not strategies:
                return

            # Create table for saved strategies
            saved_table = ui_modern_table("Profitable Strategies", show_line=True)
            saved_table.add_column("ID", justify="left", style=THEME["table_header"], width=5)
            saved_table.add_column("Strategy", justify="left", width=35)
            saved_table.add_column("Crypto", justify="left", width=12)
            saved_table.add_column("Return", justify="right", width=12)
            saved_table.add_column("Sharpe", justify="right", width=12)
            saved_table.add_column("Trades", justify="right", width=12)
            saved_table.add_column("Date", justify="right", width=12)

            # Display up to 10 most recent strategies
            for i, strategy in enumerate(strategies[:10], 1):
                metrics = strategy.get('metrics', {})
                strategy_info = strategy.get('strategy', {})
                
                # Create multi-line strategy cell
                strategy_cell = (
                    Text(strategy.get('strategy_label', ''), style=THEME["highlight"]) + 
                    "\n" + 
                    Text(strategy_info.get('name', 'N/A'), style=THEME["dim"])
                )

                saved_table.add_row(
                    f"#{i}",
                    strategy_cell,
                    strategy.get('symbol', ''),
                    f"{metrics.get('total_return', 0):.2%}",
                    f"{metrics.get('sharpe_ratio', 0):.2f}",
                    f"{metrics.get('total_trades', 0)}",
                    strategy.get('test_date', 'N/A')[:10],  # Date only
                )

            console.print(saved_table)

            # Show count of additional strategies if applicable
            if len(strategies) > 10:
                console.print(
                    f"{len(strategies) - 10} additional strategy(s) available...", 
                    style=THEME["dim"]
                )

        except Exception as e:
            raise TradingStrategyBacktesterError(f"Failed to retrieve saved strategies: {str(e)}") from e