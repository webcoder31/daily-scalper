"""
Utility modules for the Daily Scalper trading application.

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
    DataLoader: Handles cryptocurrency market data loading with caching
    Visualizer: Creates interactive charts and visualizations
    StrategySaver: Manages strategy results persistence and retrieval
    PeriodTranslator: Translates time period abbreviations for display

Example:
    >>> from utils import DataLoader, Visualizer, StrategySaver
    >>> loader = DataLoader()
    >>> data = loader.load_crypto_data("BTC-USD", "1y")
    >>> # Use data for backtesting...
"""

from typing import List

from .data_loader import DataLoader
from .visualizer import Visualizer
from .strategy_saver import StrategySaver
from .period_translator import PeriodTranslator

__all__: List[str] = [
    'DataLoader',
    'Visualizer', 
    'StrategySaver',
    'PeriodTranslator'
]

__version__ = "1.0.0"
__author__ = "Daily Scalper Team"
__description__ = "Utility modules for cryptocurrency trading strategy backtesting"