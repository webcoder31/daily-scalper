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
from utils.theme import THEME
from utils.ui_components import ui_interactive_menu
from utils.ui_components import ui_section_header
from utils.ui_components import ui_error_message
from utils.ui_components import ui_modern_table
from utils.ui_components import ui_block_header

# Initialize rich console
UI_WIDTH = 100
console = Console(width=UI_WIDTH)


class DailyScalper:
    """
    Main class for the Daily Scalper application.
    """


    def __init__(self):
        """
        Initialize the application.
        """

        self.data_loader = DataLoader()
        self.backtest_engine = BacktestEngine()
        self.strategy_saver = StrategySaver()

        console.print(ui_block_header("Daily Scalper", "Application successfully initialized."))


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
        header_table = ui_modern_table("Tested Configuration")
        header_table.add_column("Setting", width=48)
        header_table.add_column("Value", width=48)

        # Add coin pair
        symbol = results['symbol']
        header_table.add_row(
            "Crytpo Pair",
            f"[{THEME['success']}]{symbol}[/{THEME['success']}]"
        )

        # Add initial capital
        initial_cash = results['parameters']['initial_cash']
        header_table.add_row(
            "Initial Capital",
            f"[{THEME['success']}]${initial_cash:,.2f}[/{THEME['success']}]"
        )

        # Add period
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
        if 'parameters' in strategy:
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

        # Final evaluation
        is_profitable = PerformanceMetrics.is_strategy_profitable(metrics)
        tested_strategy = f"{results['strategy_label']} for {results['symbol']}"
        status_text = f"✅ {tested_strategy} is PROFITABLE" if is_profitable \
                      else f"❌ {tested_strategy} is NOT PROFITABLE"
        status_style = THEME["success"] if is_profitable else THEME["error"]

        print()
        console.print(Text(status_text, style=status_style))
        print()


    def backtest_strategy(
            self,
            strategy_name: str,
            symbol: str = "BTC-USD",
            period: str = "1y",
            strategy_params: Dict[str, Any] = None,
            show_plots: bool = True,
            save_if_profitable: bool = True,
            batch_mode: bool = False
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

        if not batch_mode:
            console.print(ui_block_header("Strategy Backtest",
                f"{strategy_name}\n"
                f"Crypto pair: {symbol}, "
                f"Period: {PeriodTranslator.get_period_description(period)}\n"
                f"{param_str}"))
        else:
            console.print(ui_section_header(f"Running backtest with {param_str}"))

        # 1. Loading data
        console.print("Loading data...", style=THEME["table_border"])
        data = self.data_loader.load_crypto_data(symbol=symbol, period=period)
        if data.empty:
            console.print(ui_error_message("No data found for the specified period.", "Data Error"))
            return {}
        console.print(
            f"✅ {len(data)} data points loaded " \
                f"from {data.index[0].strftime('%Y-%m-%d')} " \
                f"to {data.index[-1].strftime('%Y-%m-%d')}\n", 
            style=THEME["success"])
        

        # 2. Creating strategy
        console.print("Initializing strategy...", style=THEME["table_border"])
        strategy = create_strategy(strategy_name, **strategy_params)
        console.print(f"✅ Strategy ready\n", style=THEME["success"])
        console.print(f"{strategy.get_explanation()}\n", style=THEME["success"])

        # 3. Executing backtest
        console.print("Executing backtest...", style=THEME["table_border"])
        results = self.backtest_engine.run_backtest(strategy, data)
        console.print("✅ Backtest completed\n", style=THEME["success"])

        # Add strategy instance to results for visualization
        results['strategy_instance'] = strategy
        results['strategy_label'] = strategy.get_short_description(strategy_params)

        # Add symbol to results
        results['symbol'] = symbol

        # 4. Calculate advanced metrics
        console.print("Calculating advanced metrics...", style=THEME["table_border"])
        results['metrics'] = PerformanceMetrics.calculate_advanced_metrics(results)
        console.print("✅ Metrics computed\n", style=THEME["success"])

        # 5. Display results
        self._display_results(results)

        # 6. Visualization
        if show_plots:
            console.print("Generating charts...", style=THEME["accent"])
            Visualizer.show_all_plots(results)

        # 7. Save if profitable
        if save_if_profitable and PerformanceMetrics.is_strategy_profitable(results['metrics']):
            console.print("\nProfitable strategy detected - Saving...", style=THEME["dim"])
            save_id = self.strategy_saver.save_strategy_results(results)
            results['save_id'] = save_id
            console.print(f"✅ Strategy saved: {save_id}", style=THEME["success"])
        elif save_if_profitable:
            console.print("⚠️  Unprofitable strategy - Not saved", style=THEME["warning"])

        return results


    def compare_strategies(
            self,
            strategy_name: str,
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

        console.print(ui_block_header("Strategy Comparison",
            f"{strategy_name}\n"
            f"Crypto pair: {symbol}, "
            f"Period: {PeriodTranslator.get_period_description(period)}"))

        results_list = []

        # Table for results
        progress_table = ui_modern_table("Comparison Results")
        progress_table.add_column("Test", style=THEME["table_header"], width=8)
        progress_table.add_column("Configuration", width=32)
        progress_table.add_column("Return", justify="right", width=12)
        progress_table.add_column("Sharpe", justify="right", width=10)
        progress_table.add_column("Trades", justify="right", width=10)
        progress_table.add_column("Profit Factor", justify="right", width=14)
        progress_table.add_column("Status", justify="center", width=14)

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
                    strategy_name,
                    symbol=symbol,
                    period=period,
                    strategy_params=strategy_params,
                    show_plots=False,
                    save_if_profitable=False,
                    batch_mode=True
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

        # Section title
        console.print(ui_section_header(f"Comparison Results for Strategy {strategy_name}"))

        console.print(progress_table)

        # Strategy ranking
        if results_list:
            ranked_strategies = PerformanceMetrics.rank_strategies(results_list)

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
            console.print("❌ No valid results obtained for comparison.", style=THEME["error"])


    def show_saved_strategies(self) -> None:
        """
        Display saved profitable strategies.
        """

        # Get list of saved strategies
        strategies = self.strategy_saver.list_saved_strategies()

        # Create status text
        status_text = "No saved strategy for now." if not strategies else f"{len(strategies)} profitable strategies saved."

        console.print(ui_block_header("Saved Strategies", status_text))
        if not strategies:
            return

        # Table of saved best strategies
        saved_table = ui_modern_table("Profitable Strategies", show_line=True)
        saved_table.add_column("ID", justify="left", style=THEME["table_header"], width=5)
        saved_table.add_column("Strategy", justify="left", width=35)
        saved_table.add_column("Crypto", justify="left", width=12)
        saved_table.add_column("Return", justify="right", width=12)
        saved_table.add_column("Sharpe", justify="right", width=12)
        saved_table.add_column("Trades", justify="right", width=12)
        saved_table.add_column("Date", justify="right", width=12)

        for i, strategy in enumerate(strategies[:10], 1):
            metrics = strategy.get('metrics', {})
            strategy_info = strategy.get('strategy', {})
            strategy_cell = Text(strategy.get('strategy_label', ''), style=THEME["highlight"]) + "\n" + Text(strategy_info.get('name', 'N/A'), style=THEME["dim"])

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

        if len(strategies) > 10:
            console.print(f"{len(strategies) - 10} additional strategy(s) available...", style=THEME["dim"])