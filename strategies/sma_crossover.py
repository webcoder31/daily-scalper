"""
Simple Moving Average Crossover strategy (SMA Crossover).
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy


class SMACrossoverStrategy(BaseStrategy):
    """
    Strategy based on the crossing of two simple moving averages.
    
    Buy signal: when the short SMA crosses above the long SMA
    Sell signal: when the short SMA crosses below the long SMA
    """
    
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
        super().__init__('SMA Crossover', parameters)
        
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
    
    def get_description(self) -> str:
        """
        Return a description of the strategy.
        
        Returns:
            Description of the SMA Crossover strategy
        """
        short_window = self.parameters['short_window']
        long_window = self.parameters['long_window']
        
        return (f"Simple Moving Average Crossover Strategy "
                f"(SMA {short_window} / SMA {long_window}).\n"
                f"Buy when SMA{short_window} > SMA{long_window}, "
                f"sell when SMA{short_window} < SMA{long_window}.")
    
    def get_indicators(self) -> Dict[str, pd.Series]:
        """
        Return the calculated indicators for visualization.
        
        Returns:
            Dictionary of technical indicators
        """
        return getattr(self, 'indicators', {})