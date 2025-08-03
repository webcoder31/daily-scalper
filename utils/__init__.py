"""
Utility modules for the Trading Strategy Backtester trading application.

This package provides essential utility modules for data loading, visualization,
strategy persistence, UI components, and other supporting functionality for the
cryptocurrency trading strategy backtesting system.

Modules:
    data_loader: Market data loading and caching functionality
    visualizer: Interactive chart generation and visualization
    strategy_saver: Strategy results persistence and management
    period_translator: Time period abbreviation translation utilities
    theme: UI theme configuration and styling
    ui_components: Rich terminal UI components and interactive elements

Classes:
    MarketDataProvider: Handles cryptocurrency market data loading with caching
    BacktestChartGenerator: Creates interactive charts and visualizations
    StrategyResultsPersistence: Manages strategy results persistence and retrieval
    PeriodTranslator: Translates time period abbreviations for display

Example:
    >>> from utils import MarketDataProvider, BacktestChartGenerator, StrategyResultsPersistence
    >>> loader = MarketDataProvider()
    >>> data = loader.fetch_cryptocurrency_data("BTC-USD", "1y")
    >>> # Use data for backtesting...
"""

from typing import List

from market_data.market_data_provider import MarketDataProvider
from visualization.backtest_chart_generator import BacktestChartGenerator
from persistence.strategy_results_persistence import StrategyResultsPersistence
from market_data.period_translator import PeriodTranslator

__all__: List[str] = [
    'MarketDataProvider',
    'BacktestChartGenerator',
    'StrategyResultsPersistence',
    'PeriodTranslator'
]

__version__ = "1.0.0"