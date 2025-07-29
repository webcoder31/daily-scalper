"""
Bollinger Bands Strategy.
"""

from typing import Dict, Any, Tuple, List
import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy
from .strategy_registry import register_strategy


@register_strategy
class BBStrategy(BaseStrategy):
    """
    Strategy based on Bollinger Bands.
    
    Buy signal: Price crosses below lower band
    Sell signal: Price crosses above upper band
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
                'default': 20,
                'range': (5, 50),
                'description': 'Period for moving average'
            },
            'std_dev': {
                'type': float,
                'default': 2.0,
                'range': (1.0, 3.0),
                'description': 'Number of standard deviations'
            }
        }
    
    def __init__(self, 
                period: int = 20, 
                std_dev: float = 2.0,
                **kwargs):
        """
        Initialize the Bollinger Bands strategy.
        
        Args:
            period: Period for moving average
            std_dev: Number of standard deviations
            **kwargs: Additional parameters
        """
        parameters = {
            'period': period,
            'std_dev': std_dev,
            **kwargs
        }
        super().__init__(self.get_label(), parameters)
        
        if period < 2:
            raise ValueError("Period must be at least 2")
        if std_dev <= 0:
            raise ValueError("Standard deviation must be positive")
    
    def generate_signals(self, data: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """
        Generate buy and sell signals based on Bollinger Bands.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Tuple containing entry and exit signals
        """
        if not self.validate_data(data):
            raise ValueError("Invalid data: OHLCV columns required")
        
        period = self.parameters['period']
        std_dev = self.parameters['std_dev']
        
        # Calculate Bollinger Bands
        middle_band = data['Close'].rolling(window=period).mean()
        std = data['Close'].rolling(window=period).std()
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)
        
        # Buy signal: Price crosses below lower band
        buy_signals = (data['Close'] < lower_band) & (data['Close'].shift(1) >= lower_band.shift(1))
        
        # Sell signal: Price crosses above upper band
        sell_signals = (data['Close'] > upper_band) & (data['Close'].shift(1) <= upper_band.shift(1))
        
        # Store indicators for visualization
        self.indicators = {
            'middle_band': middle_band,
            'upper_band': upper_band,
            'lower_band': lower_band
        }
        
        return buy_signals, sell_signals
    
    def get_explanation(self) -> str:
        """
        Return an explanation of the strategy.
        
        Returns:
            Textual explanation of the strategy
        """
        period = self.parameters['period']
        std_dev = self.parameters['std_dev']
        
        return (
            f"{self.get_label()} with period={period} and std_dev={std_dev:.2f}.\n"
            f"Buy when price crosses below lower band, " 
            f"sell when price crosses above upper band."
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
        if config and 'period' in config and 'std_dev' in config:
            return f"{cls.get_short_label()} {config['period']}/{config['std_dev']:.2f}"
        return cls.get_short_label()
        
    @classmethod
    def get_label(cls) -> str:
        """
        Get the label of the strategy.
            
        Returns:
            Label string
        """
        return "Bollinger Bands"
    
    @classmethod
    def get_short_label(cls) -> str:
        """
        Get the short label of the strategy.
            
        Returns:
            Label string
        """
        return "BB"
    
    @classmethod
    def get_predefined_configurations(cls) -> List[Dict[str, Any]]:
        """
        Get predefined configurations for strategy comparison.
        
        Returns:
            List of parameter dictionaries for comparison
        """
        return [
            {'period': 20, 'std_dev': 2.0},  # Standard
            {'period': 20, 'std_dev': 1.5},  # Tighter bands
            {'period': 20, 'std_dev': 2.5},  # Wider bands
            {'period': 10, 'std_dev': 2.0},  # Shorter period
            {'period': 50, 'std_dev': 2.0}   # Longer period
        ]
    
    def get_indicators(self) -> Dict[str, pd.Series]:
        """
        Return the calculated indicators for visualization.
        
        Returns:
            Dictionary of technical indicators
        """
        return getattr(self, 'indicators', {})