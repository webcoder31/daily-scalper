"""
Abstract Base Strategy Class for Trading Strategies.

This module defines the abstract base class that all trading strategies must inherit from.
It provides a consistent interface and common functionality for strategy implementation,
parameter management, and signal generation.

The AbstractStrategy class enforces the Strategy Pattern design, ensuring all concrete
strategy implementations follow the same interface while allowing for flexible
customization of trading logic.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, List, Optional, Union
import pandas as pd
import numpy as np


class StrategyError(Exception):
    """Custom exception for strategy-related errors."""
    pass


class ParameterValidationError(StrategyError):
    """Exception raised when strategy parameters are invalid."""
    pass


class DataValidationError(StrategyError):
    """Exception raised when input data is invalid or insufficient."""
    pass


class AbstractStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    
    This class defines the interface that all trading strategies must implement.
    It provides common functionality for parameter management, data validation,
    and strategy serialization while enforcing implementation of core methods
    for signal generation and strategy explanation.
    
    All concrete strategy classes must inherit from this base class and implement
    the abstract methods: generate_signals() and get_explanation().
    
    Attributes:
        name: Human-readable name of the strategy.
        parameters: Dictionary containing strategy configuration parameters.
        results: Optional storage for backtest results.
        indicators: Optional storage for calculated technical indicators.
    """


    def __init__(self, name: str, parameters: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the base strategy with name and parameters.
        
        Args:
            name: Human-readable name of the strategy.
            parameters: Dictionary of configuration parameters for the strategy.
                       If None, an empty dictionary will be used.
        
        Raises:
            ParameterValidationError: If the name is empty or parameters are invalid.
        """
        if not name or not isinstance(name, str):
            raise ParameterValidationError("Strategy name must be a non-empty string")
        
        self.name: str = name
        self.parameters: Dict[str, Any] = parameters or {}
        self.results: Optional[Any] = None
        self.indicators: Dict[str, pd.Series] = {}
        
        # Validate parameters if validation method exists
        if hasattr(self, '_validate_parameters'):
            self._validate_parameters(self.parameters)


    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """
        Generate buy and sell signals based on market data.
        
        This is the core method that must be implemented by all concrete strategy
        classes. It analyzes the provided market data and returns boolean series
        indicating when to enter (buy) and exit (sell) positions.
        
        Args:
            data: DataFrame containing OHLCV market data with columns:
                 ['Open', 'High', 'Low', 'Close', 'Volume'].
        
        Returns:
            Tuple containing two pandas Series:
            - buy_signals: Boolean series indicating buy entry points
            - sell_signals: Boolean series indicating sell exit points
        
        Raises:
            DataValidationError: If the input data is invalid or insufficient.
            StrategyError: If signal generation fails due to strategy-specific issues.
        """
        pass


    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validate that the input data contains required columns and is sufficient.
        
        Checks for the presence of standard OHLCV columns and ensures the data
        has sufficient rows for strategy calculations.
        
        Args:
            data: DataFrame to validate.
        
        Returns:
            True if the data is valid and sufficient for strategy calculations.
        
        Raises:
            DataValidationError: If the data is invalid or insufficient.
        """
        if not isinstance(data, pd.DataFrame):
            raise DataValidationError("Input data must be a pandas DataFrame")
        
        if data.empty:
            raise DataValidationError("Input data cannot be empty")
        
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            raise DataValidationError(
                f"Missing required columns: {missing_columns}. "
                f"Required columns are: {required_columns}"
            )
        
        # Check for sufficient data rows (minimum 2 for basic calculations)
        if len(data) < 2:
            raise DataValidationError(
                f"Insufficient data: {len(data)} rows. Minimum 2 rows required."
            )
        
        return True


    def get_parameters(self) -> Dict[str, Any]:
        """
        Get a copy of the current strategy parameters.
        
        Returns:
            Dictionary containing a copy of all strategy parameters.
        """
        return self.parameters.copy()


    def set_parameters(self, parameters: Dict[str, Any]) -> None:
        """
        Update the strategy parameters with new values.
        
        Args:
            parameters: Dictionary of new parameter values to update.
        
        Raises:
            ParameterValidationError: If the new parameters are invalid.
        """
        if not isinstance(parameters, dict):
            raise ParameterValidationError("Parameters must be a dictionary")
        
        # Create updated parameters
        updated_params = self.parameters.copy()
        updated_params.update(parameters)
        
        # Validate updated parameters if validation method exists
        if hasattr(self, '_validate_parameters'):
            self._validate_parameters(updated_params)
        
        # Update parameters if validation passes
        self.parameters = updated_params


    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the strategy to a dictionary representation for serialization.
        
        This method creates a dictionary containing all essential strategy
        information that can be used for saving, loading, or transmitting
        strategy configurations.
        
        Returns:
            Dictionary containing strategy name, class, parameters, and description.
        """
        return {
            'name': self.name,
            'class': self.__class__.__name__,
            'parameters': self.parameters.copy(),
            'description': self.get_explanation()
        }
    
    
    @abstractmethod
    def get_explanation(self) -> str:
        """
        Get a detailed explanation of the strategy logic and parameters.
        
        This method must be implemented by all concrete strategy classes to
        provide a human-readable explanation of how the strategy works,
        including its current parameter values.
        
        Returns:
            Detailed textual explanation of the strategy.
        """
        pass


    @classmethod
    def get_parameter_summary(cls, config: Optional[Dict[str, Any]] = None) -> str:
        """
        Get a concise description of the strategy with optional configuration details.
        
        This method provides a brief, formatted description that can include
        parameter values when a configuration is provided.
        
        Args:
            config: Optional dictionary of strategy parameters to include in description.
        
        Returns:
            Short description string, optionally including parameter values.
        """
        if config:
            param_str = ", ".join([f"{k}={v}" for k, v in config.items()])
            return f"{cls.get_abbreviated_name()} ({param_str})"
        return cls.get_abbreviated_name()


    @classmethod
    def get_label(cls) -> str:
        """
        Get the full human-readable label of the strategy.
        
        This method should be overridden by subclasses to provide a descriptive
        name for the strategy that will be displayed in user interfaces.
        
        Returns:
            Full strategy label string.
        """
        return "Base Strategy"


    @classmethod
    def get_abbreviated_name(cls) -> str:
        """
        Get a short abbreviation or code for the strategy.
        
        This method should be overridden by subclasses to provide a brief
        identifier that can be used in compact displays or file names.
        
        Returns:
            Short strategy label string.
        """
        return "BS"


    @classmethod
    def get_comparison_parameter_sets(cls) -> List[Dict[str, Any]]:
        """
        Get a list of predefined parameter configurations for strategy comparison.
        
        This method provides multiple parameter combinations that can be used
        for backtesting and comparison purposes. Subclasses should override
        this method to provide meaningful parameter variations.
        
        Returns:
            List of parameter dictionaries representing different configurations.
        """
        # Default implementation attempts to create variations based on parameter definitions
        try:
            if hasattr(cls, 'get_parameter_definitions'):
                param_info = cls.get_parameter_definitions()
                key_params = list(param_info.keys())[:2]  # Use first two parameters
                
                if key_params:
                    configs = []
                    for i in range(5):  # Create 5 variations
                        config = {}
                        for param in key_params:
                            param_def = param_info[param]
                            default = param_def.get('default')
                            
                            if isinstance(default, (int, float)):
                                # Vary parameter from -20% to +20% by increments of 10%
                                factor = 0.8 + (i * 0.1)
                                if isinstance(default, int):
                                    config[param] = max(1, int(default * factor))
                                else:
                                    config[param] = round(default * factor, 2)
                            else:
                                config[param] = default
                        configs.append(config)
                    return configs
        except Exception:
            # If automatic generation fails, return empty configuration
            pass
        
        # Return a single empty configuration as fallback
        return [{}]


    @classmethod
    def get_parameter_definitions(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get parameter definitions with types, defaults, and constraints.
        
        This method should be overridden by subclasses to define their
        specific parameters with validation information.
        
        Returns:
            Dictionary mapping parameter names to their definitions.
            Each definition should include 'type', 'default', 'range', and 'description'.
        """
        return {}


    def get_indicators(self) -> Dict[str, pd.Series]:
        """
        Get calculated technical indicators for charting purposes.
        
        This method returns any technical indicators that were calculated
        during signal generation and can be used for plotting or analysis.
        
        Returns:
            Dictionary mapping indicator names to their calculated Series.
        """
        return getattr(self, 'indicators', {})


    def _validate_parameters(self, parameters: Dict[str, Any]) -> None:
        """
        Validate strategy parameters against their definitions.
        
        This is a helper method that can be used by subclasses to validate
        parameters against their parameter definitions.
        
        Args:
            parameters: Dictionary of parameters to validate.
        
        Raises:
            ParameterValidationError: If any parameter is invalid.
        """
        if not hasattr(self.__class__, 'get_parameter_definitions'):
            return
        
        param_defs = self.__class__.get_parameter_definitions()
        
        for param_name, param_value in parameters.items():
            if param_name in param_defs:
                param_def = param_defs[param_name]
                
                # Check type if specified
                expected_type = param_def.get('type')
                if expected_type and not isinstance(param_value, expected_type):
                    raise ParameterValidationError(
                        f"Parameter '{param_name}' must be of type {expected_type.__name__}, "
                        f"got {type(param_value).__name__}"
                    )
                
                # Check range if specified
                param_range = param_def.get('range')
                if param_range and isinstance(param_value, (int, float)):
                    min_val, max_val = param_range
                    if not (min_val <= param_value <= max_val):
                        raise ParameterValidationError(
                            f"Parameter '{param_name}' must be between {min_val} and {max_val}, "
                            f"got {param_value}"
                        )