"""
Trading strategies module.
"""

from .base_strategy import BaseStrategy
"""
Strategies package - Contains all trading strategies for the Daily Scalper app.
"""

# Import base classes
from .base_strategy import BaseStrategy
from .strategy_registry import register_strategy, get_strategy_names, create_strategy, get_strategy_parameter_info

# Import strategy implementations (these will register with the decorator)
from .sma_strategy import SMAStrategy
from .rsi_strategy import RSIStrategy
from .bb_strategy import BBStrategy
from .emarsi_strategy import EMARSIStrategy

# Export the classes
__all__ = [
    'BaseStrategy',
    'register_strategy',
    'get_strategy_names',
    'create_strategy',
    'get_strategy_parameter_info',
    'SMAStrategy',
    'RSIStrategy',
    'BBStrategy',
    'EMARSIStrategy'
]