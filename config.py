"""
Global configuration for the Trading Strategy Backtester application.

This module contains all configuration constants and settings used throughout
the application, including backtest parameters, data retrieval settings,
profitability criteria, and charting options.
"""

from typing import Dict, List, Union, Any


# Type aliases for better readability
ConfigDict = Dict[str, Union[str, int, float, bool]]
CriteriaDict = Dict[str, Union[int, float]]


DEFAULT_BACKTEST_CONFIG: ConfigDict = {
    'initial_cash': 10000.0,
    'commission': 0.001,  # 0.1%
    'slippage': 0.0001,   # 0.01%
}
"""
Default configuration parameters for backtesting operations.

Contains:
    initial_cash: Starting capital for backtests in USD
    commission: Trading commission as a decimal (0.001 = 0.1%)
    slippage: Price slippage as a decimal (0.0001 = 0.01%)
"""


DEFAULT_DATA_CONFIG: ConfigDict = {
    'default_symbol': 'BTC-USD',
    'default_period': '1y',
    'cache_enabled': True,
    'cache_max_age_hours': 24,
}
"""
Default configuration for data retrieval and caching.

Contains:
    default_symbol: Default cryptocurrency symbol to analyze
    default_period: Default time period for data retrieval
    cache_enabled: Whether to enable data caching
    cache_max_age_hours: Maximum age of cached data in hours
"""


PROFITABILITY_CRITERIA: CriteriaDict = {
    'min_return': 0.1,      # 10% minimum
    'min_sharpe': 1.0,      # Sharpe ratio minimum
    'max_drawdown': 0.2,    # 20% maximum
    'min_trades': 5,        # Minimum number of trades
}
"""
Criteria for determining if a trading strategy is considered profitable.

Contains:
    min_return: Minimum required return as a decimal (0.1 = 10%)
    min_sharpe: Minimum acceptable Sharpe ratio
    max_drawdown: Maximum acceptable drawdown as a decimal (0.2 = 20%)
    min_trades: Minimum number of trades required for reliability
"""


CHARTING_CONFIG: ConfigDict = {
    'default_height': 800,
    'show_volume': True,
    'show_signals': True,
    'show_indicators': True,
}
"""
Configuration settings for chart creation.

Contains:
    default_height: Default height of charts in pixels
    show_volume: Whether to display volume data
    show_signals: Whether to display buy/sell signals
    show_indicators: Whether to display technical indicators
"""


POPULAR_CRYPTO_SYMBOLS: List[str] = [
    "BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "ADA-USD",
    "SOL-USD", "DOGE-USD", "DOT-USD", "AVAX-USD", "SHIB-USD",
    "MATIC-USD", "LTC-USD", "UNI-USD", "LINK-USD", "ATOM-USD"
]
"""
List of popular cryptocurrency symbols available for analysis.

These symbols are commonly used and supported by Yahoo Finance API.
All symbols follow the format: CRYPTO-USD (e.g., BTC-USD, ETH-USD).
"""


def get_backtest_config() -> ConfigDict:
    """
    Get the default backtest configuration.
    
    Returns:
        Dictionary containing backtest configuration parameters.
    """
    return DEFAULT_BACKTEST_CONFIG.copy()


def get_data_config() -> ConfigDict:
    """
    Get the default data configuration.
    
    Returns:
        Dictionary containing data retrieval configuration parameters.
    """
    return DEFAULT_DATA_CONFIG.copy()


def get_profitability_criteria() -> CriteriaDict:
    """
    Get the profitability criteria for strategy evaluation.
    
    Returns:
        Dictionary containing profitability criteria parameters.
    """
    return PROFITABILITY_CRITERIA.copy()


def get_charting_config() -> ConfigDict:
    """
    Get the charting configuration.
    
    Returns:
        Dictionary containing charting configuration parameters.
    """
    return CHARTING_CONFIG.copy()


def get_popular_symbols() -> List[str]:
    """
    Get the list of popular cryptocurrency symbols.
    
    Returns:
        List of cryptocurrency symbols in CRYPTO-USD format.
    """
    return POPULAR_CRYPTO_SYMBOLS.copy()


def validate_symbol(symbol: str) -> bool:
    """
    Validate if a cryptocurrency symbol is in the correct format.
    
    Args:
        symbol: The cryptocurrency symbol to validate.
    
    Returns:
        True if the symbol format is valid, False otherwise.
    """
    if not isinstance(symbol, str):
        return False
    
    # Check if symbol follows CRYPTO-USD format
    parts = symbol.split('-')
    return len(parts) == 2 and parts[1] == 'USD' and len(parts[0]) > 0


def is_popular_symbol(symbol: str) -> bool:
    """
    Check if a symbol is in the list of popular cryptocurrencies.
    
    Args:
        symbol: The cryptocurrency symbol to check.
    
    Returns:
        True if the symbol is popular, False otherwise.
    """
    return symbol in POPULAR_CRYPTO_SYMBOLS