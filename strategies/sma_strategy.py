"""
Simple Moving Average Crossover strategy (SMA Crossover).
"""

from typing import Dict, Any, Tuple, List
import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy
from .strategy_registry import register_strategy


@register_strategy
class SMAStrategy(BaseStrategy):
    """
    Strategy based on the crossing of two simple moving averages.
    
    Buy signal: when the short SMA crosses above the long SMA
    Sell signal: when the short SMA crosses below the long SMA
    """
    
    @classmethod
    def get_parameter_definitions(cls) -> Dict[str, Dict[str, Any]]:
        """
        Define parameters for this strategy with constraints.
        
        Returns:
            Dictionary of parameter definitions
        """
        return {
            'short_window': {
                'type': int,
                'default': 20,
                'range': (5, 100),
                'description': 'Period for short moving average'
            },
            'long_window': {
                'type': int,
                'default': 50,
                'range': (10, 200),
                'description': 'Period for long moving average'
            }
        }
    
    def __init__(self, short_window: int = 20, long_window: int = 50, **kwargs):
        """
        Initialize the SMA Crossover strategy.
        
        Args:
            short_window: Period for the short moving average
            long_window: Period for the long moving average
            **kwargs: Additional parameters
        """
        parameters = {
            'short_window': short_window,
            'long_window': long_window,
            **kwargs
        }
        super().__init__(self.get_label(), parameters)
        
        # Parameter validation
        if short_window >= long_window:
            raise ValueError("The short period must be less than the long period")
        if short_window < 1 or long_window < 1:
            raise ValueError("Periods must be positive")
    
    def generate_signals(self, data: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """
        Generate buy and sell signals based on SMA crossovers.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Tuple containing entry and exit signals
        """
        if not self.validate_data(data):
            raise ValueError("Invalid data: OHLCV columns required")
        
        short_window = self.parameters['short_window']
        long_window = self.parameters['long_window']
        
        # Calculate moving averages
        sma_short = data['Close'].rolling(window=short_window).mean()
        sma_long = data['Close'].rolling(window=long_window).mean()
        
        # Crossover signals
        # Buy signal: Short SMA crosses above long SMA
        buy_signals = (sma_short > sma_long) & (sma_short.shift(1) <= sma_long.shift(1))
        
        # Sell signal: Short SMA crosses below long SMA
        sell_signals = (sma_short < sma_long) & (sma_short.shift(1) >= sma_long.shift(1))
        
        # Store indicators for visualization
        self.indicators = {
            'sma_short': sma_short,
            'sma_long': sma_long
        }
        
        return buy_signals, sell_signals
    
    def get_explanation(self) -> str:
        """
        Return an explanation of the strategy.
        
        Returns:
            Textual explanation of the strategy
        """
        short_window = self.parameters['short_window']
        long_window = self.parameters['long_window']
        
        return (
            f"{self.get_label()} Crossover with short period={short_window} and long period={long_window}.\n"
            f"Buy when {self.get_short_label()}{short_window} > {self.get_short_label()}{long_window}, " 
            f"sell when {self.get_short_label()}{short_window} < {self.get_short_label()}{long_window}."
        )
    
    @classmethod
    def get_short_description(cls, config: Dict[str, Any] = None) -> str:
        """
        Get a short description of the strategy with optional configuration details.
        
        Args:
            config: Strategy parameters configuration
            
        Returns:
            Short description string
        """
        if config and 'short_window' in config and 'long_window' in config:
            return f"{cls.get_short_label()} {config['short_window']}/{config['long_window']}"
        return cls.get_short_label()
        
    @classmethod
    def get_label(cls) -> str:
        """
        Get the label of the strategy.
            
        Returns:
            Label string
        """
        return "Simple Moving Average"
    
    @classmethod
    def get_short_label(cls) -> str:
        """
        Get the short label of the strategy.
            
        Returns:
            Label string
        """
        return "SMA"
    
    @classmethod
    def get_predefined_configurations(cls) -> List[Dict[str, Any]]:
        """
        Get predefined configurations for strategy comparison.
        
        Returns:
            List of parameter dictionaries for comparison
        """
        return [
            {'short_window': 10, 'long_window': 30},
            {'short_window': 20, 'long_window': 50},
            {'short_window': 30, 'long_window': 70},
            {'short_window': 50, 'long_window': 100},
            {'short_window': 20, 'long_window': 100}
        ]
    
    def get_indicators(self) -> Dict[str, pd.Series]:
        """
        Return the calculated indicators for visualization.
        
        Returns:
            Dictionary of technical indicators
        """
        return getattr(self, 'indicators', {})