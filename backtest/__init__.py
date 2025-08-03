"""
Backtesting Module for Daily Scalper Trading System.

This module provides comprehensive backtesting capabilities for cryptocurrency trading strategies
using vectorbt for high-performance vectorized calculations. The module includes:

- BacktestEngine: Core backtesting engine for strategy evaluation
- PerformanceMetrics: Advanced performance analysis and metrics calculation

The backtesting system supports:
- Vectorized backtesting with vectorbt integration
- Comprehensive performance metrics calculation
- Advanced risk analysis and portfolio evaluation
- Strategy comparison and ranking capabilities
- Professional reporting and analysis tools

Example:
    Basic usage of the backtesting module:
    
    ```python
    from backtest import BacktestEngine, PerformanceMetrics
    from strategies import SMACrossoverStrategy
    
    # Initialize backtesting engine
    engine = BacktestEngine(initial_cash=10000.0, commission=0.001)
    
    # Create strategy instance
    strategy = SMACrossoverStrategy(short_window=10, long_window=30)
    
    # Run backtest
    results = engine.run_backtest(strategy, data)
    
    # Calculate advanced metrics
    advanced_metrics = PerformanceMetrics.calculate_advanced_metrics(results)
    
    # Generate performance report
    report = PerformanceMetrics.generate_performance_report(results)
    ```

Dependencies:
    - vectorbt: For high-performance backtesting calculations
    - pandas: For data manipulation and analysis
    - numpy: For numerical computations
    - typing: For type annotations and hints

Author: Daily Scalper Development Team
Version: 2.0.0
License: MIT
"""

from typing import List

from .backtest_engine import BacktestEngine
from .performance_metrics import PerformanceMetrics

# Public API exports
__all__: List[str] = [
    'BacktestEngine',
    'PerformanceMetrics'
]

# Module metadata
__version__ = '2.0.0'
__author__ = 'Daily Scalper Development Team'
__license__ = 'MIT'
__description__ = 'Professional backtesting module for cryptocurrency trading strategies'

# Module-level constants
DEFAULT_INITIAL_CASH = 10000.0
DEFAULT_COMMISSION = 0.001  # 0.1%
DEFAULT_SLIPPAGE = 0.0001   # 0.01%

# Profitability criteria constants
DEFAULT_MIN_RETURN = 0.1    # 10% minimum return
DEFAULT_MIN_SHARPE = 1.0    # Minimum Sharpe ratio
DEFAULT_MAX_DRAWDOWN = 0.2  # Maximum 20% drawdown