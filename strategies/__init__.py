"""
Trading Strategies Module for Trading Strategy Backtester.

This module provides a comprehensive collection of trading strategies for cryptocurrency
backtesting and analysis. It includes a robust architecture with:

- Abstract base class for all trading strategies
- Strategy registry system for dynamic strategy management
- Multiple implemented strategies (SMA, RSI, Bollinger Bands, EMA+RSI)
- Type-safe parameter validation and error handling
- Professional documentation and code standards

The module follows the Strategy Pattern design, allowing easy extension with new
trading strategies while maintaining consistent interfaces and behavior.

Available Strategies:
    - SMAStrategy: Simple Moving Average crossover strategy
    - RSIStrategy: Relative Strength Index threshold strategy  
    - BBStrategy: Bollinger Bands mean reversion strategy
    - EMARSIStrategy: Combined EMA crossover with RSI filter strategy

Usage:
    from strategies import create_strategy, get_strategy_names
    
    # Get available strategies
    strategy_names = get_strategy_names()
    
    # Create a strategy instance
    strategy = create_strategy("Simple Moving Average", short_window=10, long_window=30)
    
    # Generate trading signals
    buy_signals, sell_signals = strategy.generate_signals(data)
"""

from typing import List

# Import base classes
from .base.abstract_strategy import AbstractStrategy
from .base.strategy_registry import (
    register_strategy,
    get_strategy_names,
    create_strategy,
    get_strategy_parameter_info,
    get_strategy_class,
    get_strategy_class_by_classname,
    get_strategy_classes
)

# Import strategy implementations (these will auto-register with the decorator)
from .implementations.sma_strategy import SMAStrategy
from .implementations.rsi_strategy import RSIStrategy
from .implementations.bb_strategy import BBStrategy
from .implementations.ema_rsi_strategy import EMARSIStrategy

# Public API exports
__all__: List[str] = [
    # Base classes
    'AbstractStrategy',
    
    # Registry functions
    'register_strategy',
    'get_strategy_names',
    'create_strategy',
    'get_strategy_parameter_info',
    'get_strategy_class',
    'get_strategy_class_by_classname',
    'get_strategy_classes',
    
    # Strategy implementations
    'SMAStrategy',
    'RSIStrategy',
    'BBStrategy',
    'EMARSIStrategy'
]

# Module metadata
__version__ = "1.0.0"