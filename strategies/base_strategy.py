"""
Base class for all trading strategies.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, List
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
            'description': self.get_explanation()
        }
    
    @abstractmethod
    def get_explanation(self) -> str:
        """
        Return an explanation of the strategy.
        
        Returns:
            Textual explanation of the strategy
        """
        pass
    
    @classmethod
    def get_short_description(cls, config: Dict[str, Any] = None) -> str:
        """
        Get a short description of the strategy with optional configuration details.
        
        Args:
            config: Strategy parameters configuration
            
        Returns:
            Short description string
        """
        # Default implementation - should be overridden by subclasses
        if config:
            param_str = ", ".join([f"{k}={v}" for k, v in config.items()])
            return f"{cls.get_short_label()} ({param_str})"
        return cls.get_short_label()
    
    @classmethod
    def get_label(cls) -> str:
        """
        Get the label of the strategy.
            
        Returns:
            Label string
        """
        # Default implementation - should be overridden by subclasses
        return "Base Strategy"
    
    @classmethod
    def get_short_label(cls) -> str:
        """
        Get the short label of the strategy.
            
        Returns:
            Label string
        """
        # Default implementation - should be overridden by subclasses
        return "BS"

    @classmethod
    def get_predefined_configurations(cls) -> List[Dict[str, Any]]:
        """
        Get predefined configurations for strategy comparison.
        
        Returns:
            List of parameter dictionaries for comparison
        """
        # Default implementation - should be overridden by subclasses
        # Try to create variations based on parameter definitions
        try:
            param_info = cls.get_parameter_definitions()
            key_params = list(param_info.keys())[:2]  # Use first two parameters
            
            if key_params:
                # Create variations based on default values
                configs = []
                for i in range(11):
                    config = {}
                    for param in key_params:
                        default = param_info[param].get('default')
                        if isinstance(default, (int, float)):
                            # Vary parameter from -50% to +50% by increments of 10%
                            factor = 0.5 + (i * 0.1)
                            config[param] = int(default * factor) if isinstance(default, int) else (default * factor)
                        else:
                            config[param] = default
                    configs.append(config)
                return configs
        except:
            pass
            
        # Return a single empty configuration if no variations can be created
        return [{}]