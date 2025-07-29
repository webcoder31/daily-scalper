"""
RSI Threshold (Relative Strength Index) - Extension example.
"""

from typing import Dict, Any, Tuple, List
import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy
from .strategy_registry import register_strategy


@register_strategy
class RSIStrategy(BaseStrategy):
    """
    Strategy based on the RSI (Relative Strength Index) indicator.
    
    Buy signal: RSI < lower threshold (oversold)
    Sell signal: RSI > upper threshold (overbought)
    """
    
    @classmethod
    def get_parameter_definitions(cls) -> Dict[str, Dict[str, Any]]:
        """
        Define parameters for this strategy with constraints.
        
        Returns:
            Dictionary of parameter definitions
        """
        return {
            'period': {
                'type': int,
                'default': 14,
                'range': (2, 50),
                'description': 'Period for RSI calculation'
            },
            'oversold_threshold': {
                'type': float,
                'default': 30.0,
                'range': (10.0, 40.0),
                'description': 'Oversold threshold (buy signal)'
            },
            'overbought_threshold': {
                'type': float,
                'default': 70.0,
                'range': (60.0, 90.0),
                'description': 'Overbought threshold (sell signal)'
            }
        }
    
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
        super().__init__(self.get_label(), parameters)
        
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
    
    def get_explanation(self) -> str:
        """
        Return an explanation of the strategy.
        
        Returns:
            Textual explanation of the strategy
        """
        period = self.parameters['period']
        oversold = self.parameters['oversold_threshold']
        overbought = self.parameters['overbought_threshold']
        
        return (
            f"{self.get_label()} with period {period}.\n"
            f"Buy when {self.get_short_label()} < {oversold:.2f} (oversold), " 
            f"sell when {self.get_short_label()} > {overbought:.2f} (overbought)."
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
        if config and 'period' in config:
            oversold = config.get('oversold_threshold', 30)
            overbought = config.get('overbought_threshold', 70)
            return f"{cls.get_short_label()} {config['period']} ({oversold:.2f}/{overbought:.2f})"
        return cls.get_short_label()
        
    @classmethod
    def get_label(cls) -> str:
        """
        Get the label of the strategy.
            
        Returns:
            Label string
        """
        return "Relative Strengh Index"
    
    @classmethod
    def get_short_label(cls) -> str:
        """
        Get the short label of the strategy.
            
        Returns:
            Label string
        """
        return "RSI"
    
    @classmethod
    def get_predefined_configurations(cls) -> List[Dict[str, Any]]:
        """
        Get predefined configurations for strategy comparison.
        
        Returns:
            List of parameter dictionaries for comparison
        """
        return [
            {'period': 7, 'oversold_threshold': 30, 'overbought_threshold': 70},
            {'period': 14, 'oversold_threshold': 30, 'overbought_threshold': 70},
            {'period': 21, 'oversold_threshold': 30, 'overbought_threshold': 70},
            {'period': 14, 'oversold_threshold': 20, 'overbought_threshold': 80},
            {'period': 14, 'oversold_threshold': 40, 'overbought_threshold': 60}
        ]
    
    def get_indicators(self) -> Dict[str, pd.Series]:
        """
        Return the calculated indicators for visualization.
        
        Returns:
            Dictionary of technical indicators
        """
        return getattr(self, 'indicators', {})