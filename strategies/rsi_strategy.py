"""
RSI Strategy (Relative Strength Index) - Extension example.
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy


class RSIStrategy(BaseStrategy):
    """
    Strategy based on the RSI (Relative Strength Index) indicator.
    
    Buy signal: RSI < lower threshold (oversold)
    Sell signal: RSI > upper threshold (overbought)
    """
    
    def __init__(self, 
                 period: int = 14, 
                 oversold_threshold: float = 30, 
                 overbought_threshold: float = 70,
                 **kwargs):
        """
        Initialize the RSI strategy.
        
        Args:
            period: Period for RSI calculation
            oversold_threshold: Oversold threshold (buy signal)
            overbought_threshold: Overbought threshold (sell signal)
            **kwargs: Additional parameters
        """
        parameters = {
            'period': period,
            'oversold_threshold': oversold_threshold,
            'overbought_threshold': overbought_threshold,
            **kwargs
        }
        super().__init__('RSI Strategy', parameters)
        
        # Parameter validation
        if not (0 < oversold_threshold < overbought_threshold < 100):
            raise ValueError("Thresholds must respect: 0 < oversold < overbought < 100")
        if period < 2:
            raise ValueError("Period must be greater than 1")
    
    def generate_signals(self, data: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """
        Generate buy and sell signals based on RSI.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Tuple containing entry and exit signals
        """
        if not self.validate_data(data):
            raise ValueError("Invalid data: OHLCV columns required")
        
        period = self.parameters['period']
        oversold = self.parameters['oversold_threshold']
        overbought = self.parameters['overbought_threshold']
        
        # Calculate RSI
        rsi = self._calculate_rsi(data['Close'], period)
        
        # Signals based on thresholds
        # Buy signal: RSI goes below the oversold threshold
        buy_signals = (rsi < oversold) & (rsi.shift(1) >= oversold)
        
        # Sell signal: RSI goes above the overbought threshold
        sell_signals = (rsi > overbought) & (rsi.shift(1) <= overbought)
        
        # Store indicators for visualization
        self.indicators = {
            'rsi': rsi,
            'oversold_line': pd.Series(oversold, index=data.index),
            'overbought_line': pd.Series(overbought, index=data.index)
        }
        
        return buy_signals, sell_signals
    
    def _calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """
        Calculate the RSI indicator.
        
        Args:
            prices: Series of closing prices
            period: Period for calculation
            
        Returns:
            RSI series
        """
        # Calculate price changes
        delta = prices.diff()
        
        # Separate gains and losses
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        
        # Exponential moving averages of gains and losses
        avg_gains = gains.ewm(span=period, adjust=False).mean()
        avg_losses = losses.ewm(span=period, adjust=False).mean()
        
        # Calculate RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def get_description(self) -> str:
        """
        Return a description of the strategy.
        
        Returns:
            Description of the RSI strategy
        """
        period = self.parameters['period']
        oversold = self.parameters['oversold_threshold']
        overbought = self.parameters['overbought_threshold']
        
        return (f"RSI Strategy with period {period}. "
                f"Buy when RSI < {oversold} (oversold), "
                f"sell when RSI > {overbought} (overbought).")
    
    def get_indicators(self) -> Dict[str, pd.Series]:
        """
        Return the calculated indicators for visualization.
        
        Returns:
            Dictionary of technical indicators
        """
        return getattr(self, 'indicators', {})