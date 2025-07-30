"""
Daily Scalper Application Core Logic

Contains the DailyScalper class for running backtests, comparing strategies, and managing results.
"""

import sys
import os
from typing import Dict, Any, List
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
from rich import box

from backtest import BacktestEngine, PerformanceMetrics
from utils import DataLoader, Visualizer, StrategySaver, PeriodTranslator
from strategies.strategy_registry import create_strategy
from strategies.strategy_registry import get_strategy_parameter_info
from strategies.strategy_registry import get_strategy_class

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
            title="[bold bright_magenta]TESTED CONFIGURATION[/bold bright_magenta]",
            width=120
        )
        header_table.add_column("PARAMETER", style="bold bright_blue", width=60)
        header_table.add_column("VALUE", style="bold bright_white", width=60)

        # Add coin pair
        symbol = results['symbol']
        header_table.add_row(
            "CRYPTO PAIR",
            f"[bold bright_green]{symbol}[/bold bright_green]"
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
            "BACKTEST PERIOD",
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
            title="[bold bright_magenta]RESULTS[/bold bright_magenta]",
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
        tested_strategy = f"{results['strategy_label']} for {results['symbol']}"
        status_text = f"✅ {tested_strategy} is PROFITABLE" if is_profitable \
                      else f"❌ {tested_strategy} is UNPROFITABLE"
        status_style = "bold green" if is_profitable else "bold red"

        console.print()
        console.print(Panel(
            Text(status_text, justify="center"),
            title=f"STRATEGY EVALUATION",
            padding=(1, 1),
            style=status_style
        ))
        console.print()

    def backtest_strategy(
            self,
            strategy_name: str = "SMACrossoverStrategy",
            symbol: str = "BTC-USD",
            period: str = "1y",
            strategy_params: Dict[str, Any] = None,
            show_plots: bool = True,
            save_if_profitable: bool = True
        ) -> Dict[str, Any]:
        """
        Execute a backtest of a trading strategy.

        Args:
            strategy_name: Name of the strategy class to use
            symbol: Crypto symbol to analyze
            period: Data period
            strategy_params: Parameters for the strategy
            show_plots: Show charts
            save_if_profitable: Save if profitable

        Returns:
            Backtest results
        """
        # Use default parameters if none provided
        if strategy_params is None:
            strategy_params = {}

        # Get parameter info for the strategy
        param_info = get_strategy_parameter_info(strategy_name)

        # Build parameter description for display
        param_desc = []
        for name, value in strategy_params.items():
            if name in param_info:
                param_desc.append(f"{name}: {value}")

        param_str = ", ".join(param_desc) if param_desc else "Default parameters"

        console.print()
        console.print(Panel(
            Text(
                f"{strategy_name.upper()}\n\n"
                f"Crypto pair: {symbol}, "
                f"Backtest period: {PeriodTranslator.get_period_description(period)}\n"
                f"{param_str}",
                justify="center"
            ),
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
            strategy = create_strategy(strategy_name, **strategy_params)
            console.print(f"✅ {strategy.get_explanation()}\n", style="green")

            # 3. Executing backtest
            console.print("Executing backtest...", style="blue")
            results = self.backtest_engine.run_backtest(strategy, data)

            # Add strategy instance for visualization
            results['strategy_instance'] = strategy
            results['strategy_label'] = strategy.get_short_description(strategy_params)

            # Add symbol to results
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
            strategy_name: str = "SMACrossoverStrategy",
            symbol: str = "BTC-USD",
            period: str = "1y",
            configurations: List[Dict[str, Any]] = None
        ) -> None:
        """
        Compare different configurations of a strategy.

        Args:
            strategy_name: Name of the strategy class to use
            symbol: Symbol to analyze
            period: Data period
            configurations: List of parameter configurations to test
        """
        # If no configurations provided, get predefined ones from the strategy class
        if configurations is None:
            # Get the strategy class from registry
            strategy_class = get_strategy_class(strategy_name)
            if strategy_class:
                # Use the strategy's predefined configurations
                configurations = strategy_class.get_predefined_configurations()
            else:
                # Fallback to empty configuration if strategy not found
                configurations = [{}]

        console.print()
        console.print(Panel(
            Text(
                f"{strategy_name}\n"
                f"Crypto pair: {symbol}, "
                f"Period: {PeriodTranslator.get_period_description(period)}",
                justify="center"
            ),
            title=f"STRATEGY COMPARISON",
            padding=(1, 1),
            style="bold bright_magenta"
        ))
        console.print()

        results_list = []

        # Table for results
        progress_table = Table(
            box=box.ROUNDED,
            show_lines=True,
            style="blue",
            border_style="blue",
            title="[bold bright_magenta]COMPARISON RESULTS[/bold bright_magenta]",
            width=120
        )
        progress_table.add_column("Test", style="bold bright_blue", width=8)
        progress_table.add_column("Configuration", style="bold bright_blue", width=30)
        progress_table.add_column("Return", justify="right", style="bright_blue", width=11)
        progress_table.add_column("Sharpe", justify="right", style="bright_blue", width=9)
        progress_table.add_column("Trades", justify="right", style="bright_blue", width=9)
        progress_table.add_column("Profit Factor", justify="right", style="bright_blue", width=15)
        progress_table.add_column("Status", justify="center", style="bright_blue", width=12)

        for i, strategy_params in enumerate(configurations, 1):
            try:
                # Get the strategy class for short description
                strategy_class = get_strategy_class(strategy_name)
                if strategy_class:
                    # Use the strategy's short description method
                    strategy_short_desc = strategy_class.get_short_description(strategy_params)
                else:
                    # Fallback to generic formatting
                    strategy_short_desc = ", ".join([f"{k}={v}" for k, v in strategy_params.items()])

                results = self.backtest_strategy(
                    strategy_name=strategy_name,
                    symbol=symbol,
                    period=period,
                    strategy_params=strategy_params,
                    show_plots=False,
                    save_if_profitable=False
                )
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

            except Exception as e:
                progress_table.add_row(
                    f"{i}/{len(configurations)}",
                    strategy_short_desc,
                    "❌ Erreur",
                    "-",
                    "-",
                    "-",
                    "❌"
                )

        console.print(progress_table)

        # Strategy ranking
        if results_list:
            ranked_strategies = PerformanceMetrics.rank_strategies(results_list)

            ranking_table = Table(
                box=box.ROUNDED,
                style="blue",
                border_style="blue",
                title="[bold bright_magenta]STRATEGY RANKING[/bold bright_magenta]",
                width=120
            )
            ranking_table.add_column("Rang", style="bold bright_blue", width=10)
            ranking_table.add_column("Configuration", style="bold bright_blue", width=20)
            ranking_table.add_column("Return", justify="right", style="bright_blue", width=15)
            ranking_table.add_column("Sharpe", justify="right", style="bright_blue", width=12)
            ranking_table.add_column("Score", justify="right", style="bright_blue", width=12)
            ranking_table.add_column("Status", style="bright_blue", width=20)

            for i, result in enumerate(ranked_strategies, 1):
                strategy = result['strategy']
                metrics = result['metrics']
                params = strategy['parameters']

                is_profitable = PerformanceMetrics.is_strategy_profitable(metrics)
                status = "✅ Profitable" if is_profitable else "❌ Not profitable"

                # Get the strategy class
                strategy_class = get_strategy_class(strategy_name)
                if strategy_class:
                    # Use the strategy's short description
                    config_display = strategy_class.get_short_description(params)
                else:
                    # Fallback to generic display
                    config_display = ", ".join([f"{k}={v}" for k, v in params.items()])

                ranking_table.add_row(
                    f"#{i}",
                    config_display,
                    f"{metrics['total_return']:.2%}",
                    f"{metrics['sharpe_ratio']:.2f}",
                    f"{result['score']:.3f}",
                    status
                )

            console.print(ranking_table)
        else:
            console.print("❌ No valid results obtained for comparison.", style="red")

    def show_saved_strategies(self) -> None:
        """Display saved profitable strategies."""

        # Get list of saved strategies
        strategies = self.strategy_saver.list_saved_strategies()

        # Create status text
        status_text = "No saved strategies" if not strategies else f"{len(strategies)} saved strategy(s)"

        console.print()
        console.print(Panel(
            Text(status_text, justify="center"),
            title=f"SAVED PROFITABLE STRATEGIES",
            padding=(1, 1),
            style="bold bright_magenta"
        ))
        console.print()

        if not strategies:
            return

        # Table of saved best strategies
        saved_table = Table(
            box=box.ROUNDED,
            show_lines=True,
            style="bold bright_blue",
            border_style="blue",
            title="[bold bright_magenta]LAST 10 PROFITABLE STRATEGIES[/bold bright_magenta]",
            width=120
        )
        saved_table.add_column("ID", justify="center", style="bold bright_blue", width=5)
        saved_table.add_column("Strategy", justify="left", style="bold bright_blue", width=40)
        saved_table.add_column("Crypto", justify="left", style="bold bright_blue", width=15)
        saved_table.add_column("Return", justify="right", style="bright_blue", width=15)
        saved_table.add_column("Sharpe", justify="right", style="bright_blue", width=15)
        saved_table.add_column("Trades", justify="right", style="bright_blue", width=15)
        saved_table.add_column("Date", justify="center", style="bright_blue", width=15)

        for i, strategy in enumerate(strategies[:10], 1):
            metrics = strategy.get('metrics', {})
            strategy_info = strategy.get('strategy', {})

            saved_table.add_row(
                f"#{i}",
                f"{strategy_info.get('name', 'N/A')}\n{strategy.get('strategy_label', '')}",
                strategy.get('symbol', ''),
                f"{metrics.get('total_return', 0):.2%}",
                f"{metrics.get('sharpe_ratio', 0):.2f}",
                f"{metrics.get('total_trades', 0)}",
                strategy.get('test_date', 'N/A')[:10],  # Date only
            )

        console.print(saved_table)

        if len(strategies) > 10:
            console.print(f"{len(strategies) - 10} additional strategy(s) available...", style="dim")