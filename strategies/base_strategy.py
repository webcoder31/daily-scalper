"""
Base class for all trading strategies.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    
    All strategies must inherit from this class and implement
    the required abstract methods.
    """
    
    def __init__(self, name: str, parameters: Dict[str, Any] = None):
        """
        Initialize the base strategy.
        
        Args:
            name: Name of the strategy
            parameters: Configuration parameters for the strategy
        """
        self.name = name
        self.parameters = parameters or {}
        self.results = None
        
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """
        Generate buy and sell signals based on data.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Tuple containing entry and exit signals (buy_signals, sell_signals)
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Return a description of the strategy.
        
        Returns:
            Textual description of the strategy
        """
        pass
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validate that the data contains the required columns.
        
        Args:
            data: DataFrame to validate
            
        Returns:
            True if the data is valid, False otherwise
        """
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        return all(col in data.columns for col in required_columns)
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Return the strategy parameters.
        
        Returns:
            Dictionary of parameters
        """
        return self.parameters.copy()
    
    def set_parameters(self, parameters: Dict[str, Any]) -> None:
        """
        Update the strategy parameters.
        
        Args:
            parameters: New parameters
        """
        self.parameters.update(parameters)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the strategy to a dictionary for saving.
        
        Returns:
            Dictionary representing the strategy
        """
        return {
            'name': self.name,
            'class': self.__class__.__name__,
            'parameters': self.parameters,
            'description': self.get_description()
        }