"""
Simple Moving Average Crossover Strategy Implementation.

This module implements a classic technical analysis strategy based on the crossover
of two simple moving averages (SMA). The strategy generates buy signals when a
shorter-period SMA crosses above a longer-period SMA, and sell signals when the
shorter SMA crosses below the longer SMA.

The SMA crossover strategy is one of the most fundamental trend-following strategies
in technical analysis, suitable for identifying medium to long-term trends in
financial markets.
"""

from typing import Dict, Any, Tuple, List, Optional
import pandas as pd
import numpy as np

from ..base.abstract_strategy import AbstractStrategy, ParameterValidationError, DataValidationError
from ..base.strategy_registry import register_strategy


@register_strategy
class SMAStrategy(AbstractStrategy):
    """
    Simple Moving Average Crossover Trading Strategy.
    
    This strategy implements a classic trend-following approach using two simple
    moving averages of different periods. It generates trading signals based on
    the crossover points between these averages:
    
    - Buy Signal: Short SMA crosses above Long SMA (bullish crossover)
    - Sell Signal: Short SMA crosses below Long SMA (bearish crossover)
    
    The strategy is particularly effective in trending markets but may generate
    false signals in sideways or choppy market conditions.
    
    Parameters:
        short_window: Period for the fast/short moving average (default: 20)
        long_window: Period for the slow/long moving average (default: 50)
    
    Technical Indicators:
        - Short SMA: Simple moving average over short_window periods
        - Long SMA: Simple moving average over long_window periods
    
    Example:
        strategy = SMAStrategy(short_window=10, long_window=30)
        buy_signals, sell_signals = strategy.generate_signals(data)
    """
    

    @classmethod
    def get_parameter_definitions(cls) -> Dict[str, Dict[str, Any]]:
        """
        Define parameters for the SMA strategy with validation constraints.
        
        Returns:
            Dictionary containing parameter definitions with types, defaults,
            ranges, and descriptions for validation and UI generation.
        """
        return {
            'short_window': {
                'type': int,
                'default': 20,
                'range': (5, 100),
                'description': 'Period for the fast/short simple moving average'
            },
            'long_window': {
                'type': int,
                'default': 50,
                'range': (10, 200),
                'description': 'Period for the slow/long simple moving average'
            }
        }
    

    def __init__(self, short_window: int = 20, long_window: int = 50, **kwargs: Any) -> None:
        """
        Initialize the Simple Moving Average Crossover strategy.
        
        Args:
            short_window: Period for the fast/short moving average. Must be positive
                         and less than long_window.
            long_window: Period for the slow/long moving average. Must be positive
                        and greater than short_window.
            **kwargs: Additional parameters passed to the base class.
        
        Raises:
            ParameterValidationError: If parameters are invalid or violate constraints.
        """
        # Validate parameters before initialization
        if not isinstance(short_window, int) or short_window < 1:
            raise ParameterValidationError(
                f"short_window must be a positive integer, got {short_window}"
            )
        
        if not isinstance(long_window, int) or long_window < 1:
            raise ParameterValidationError(
                f"long_window must be a positive integer, got {long_window}"
            )
        
        if short_window >= long_window:
            raise ParameterValidationError(
                f"short_window ({short_window}) must be less than long_window ({long_window})"
            )
        
        # Prepare parameters dictionary
        parameters = {
            'short_window': short_window,
            'long_window': long_window,
            **kwargs
        }
        
        # Initialize base class
        super().__init__(self.get_label(), parameters)
    

    def generate_signals(self, data: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """
        Generate buy and sell signals based on SMA crossovers.
        
        The strategy calculates two simple moving averages and identifies crossover
        points to generate trading signals:
        
        1. Calculate short-period and long-period simple moving averages
        2. Identify bullish crossover (short SMA crosses above long SMA) for buy signals
        3. Identify bearish crossover (short SMA crosses below long SMA) for sell signals
        
        Args:
            data: DataFrame containing OHLCV market data. Must include 'Close' column
                 and have sufficient rows for the longest moving average calculation.
        
        Returns:
            Tuple containing two boolean Series:
            - buy_signals: True where bullish crossovers occur
            - sell_signals: True where bearish crossovers occur
        
        Raises:
            DataValidationError: If input data is invalid or insufficient.
            ParameterValidationError: If strategy parameters are invalid.
        """
        # Validate input data
        self.validate_data(data)
        
        # Get strategy parameters
        short_window = self.parameters['short_window']
        long_window = self.parameters['long_window']
        
        # Check if we have sufficient data for the longest moving average
        if len(data) < long_window:
            raise DataValidationError(
                f"Insufficient data: {len(data)} rows available, "
                f"but {long_window} rows required for long_window calculation"
            )
        
        try:
            # Calculate simple moving averages
            close_prices = data['Close']
            sma_short = close_prices.rolling(window=short_window, min_periods=short_window).mean()
            sma_long = close_prices.rolling(window=long_window, min_periods=long_window).mean()
            
            # Generate crossover signals
            # Buy signal: Short SMA crosses above Long SMA (bullish crossover)
            current_bullish = sma_short > sma_long
            previous_bullish = sma_short.shift(1) <= sma_long.shift(1)
            buy_signals = current_bullish & previous_bullish
            
            # Sell signal: Short SMA crosses below Long SMA (bearish crossover)
            current_bearish = sma_short < sma_long
            previous_bearish = sma_short.shift(1) >= sma_long.shift(1)
            sell_signals = current_bearish & previous_bearish
            
            # Store calculated indicators for visualization and analysis
            self.indicators = {
                'sma_short': sma_short,
                'sma_long': sma_long,
                'short_window': short_window,
                'long_window': long_window
            }
            
            return buy_signals, sell_signals
            
        except KeyError as e:
            raise DataValidationError(f"Missing required column in data: {e}") from e
        except Exception as e:
            raise DataValidationError(f"Error calculating SMA signals: {e}") from e
    

    def get_explanation(self) -> str:
        """
        Get a detailed explanation of the strategy logic and current parameters.
        
        Returns:
            Human-readable explanation of how the strategy works, including
            current parameter values and signal generation logic.
        """
        short_window = self.parameters['short_window']
        long_window = self.parameters['long_window']
        
        return (
            f"{self.get_label()} Strategy with {short_window}-period and {long_window}-period moving averages.\n\n"
            f"Signal Generation:\n"
            f"• BUY: When SMA{short_window} crosses above SMA{long_window} (bullish crossover)\n"
            f"• SELL: When SMA{short_window} crosses below SMA{long_window} (bearish crossover)\n\n"
            f"This trend-following strategy works best in trending markets and may generate "
            f"false signals in sideways market conditions. The {short_window}-period SMA reacts "
            f"faster to price changes, while the {long_window}-period SMA provides trend confirmation."
        )
    

    @classmethod
    def get_short_description(cls, config: Optional[Dict[str, Any]] = None) -> str:
        """
        Get a concise description of the strategy with optional parameter details.
        
        Args:
            config: Optional dictionary containing strategy parameters to include
                   in the description.
        
        Returns:
            Short description string, optionally including parameter values.
        
        Example:
            "SMA 20/50" (with config) or "SMA" (without config)
        """
        if config and 'short_window' in config and 'long_window' in config:
            return f"{cls.get_short_label()} {config['short_window']}/{config['long_window']}"
        return cls.get_short_label()
    

    @classmethod
    def get_label(cls) -> str:
        """
        Get the full human-readable label of the strategy.
        
        Returns:
            Full strategy name for display in user interfaces.
        """
        return "Simple Moving Average"
    

    @classmethod
    def get_short_label(cls) -> str:
        """
        Get a short abbreviation for the strategy.
        
        Returns:
            Short strategy identifier for compact displays.
        """
        return "SMA"
    

    @classmethod
    def get_predefined_configurations(cls) -> List[Dict[str, Any]]:
        """
        Get predefined parameter configurations for strategy comparison and testing.
        
        Provides a variety of commonly used SMA crossover configurations that
        represent different trading timeframes and sensitivity levels.
        
        Returns:
            List of parameter dictionaries representing different strategy configurations.
            Each configuration includes short_window and long_window parameters.
        """
        return [
            # Fast/Aggressive configurations
            {'short_window': 5, 'long_window': 15},   # Very fast signals
            {'short_window': 10, 'long_window': 30},  # Fast signals
            
            # Standard configurations
            {'short_window': 20, 'long_window': 50},  # Classic configuration
            {'short_window': 12, 'long_window': 26},  # MACD-inspired periods
            
            # Slower/Conservative configurations
            {'short_window': 30, 'long_window': 70},  # Slower signals
            {'short_window': 50, 'long_window': 100}, # Conservative signals
            {'short_window': 50, 'long_window': 200}, # Long-term trend following
            
            # Alternative ratios
            {'short_window': 15, 'long_window': 45},  # 1:3 ratio
            {'short_window': 25, 'long_window': 75},  # 1:3 ratio (slower)
        ]
    
    
    def get_indicators(self) -> Dict[str, pd.Series]:
        """
        Get calculated technical indicators for visualization and analysis.
        
        Returns the moving averages and related data that were calculated during
        signal generation. This data can be used for plotting charts or further
        technical analysis.
        
        Returns:
            Dictionary containing calculated indicators:
            - 'sma_short': Short-period simple moving average
            - 'sma_long': Long-period simple moving average
            - 'short_window': Short window parameter value
            - 'long_window': Long window parameter value
        """
        return getattr(self, 'indicators', {})


    def _validate_parameters(self, parameters: Dict[str, Any]) -> None:
        """
        Validate strategy parameters against constraints.
        
        Performs comprehensive validation of strategy parameters including
        type checking, range validation, and logical consistency checks.
        
        Args:
            parameters: Dictionary of parameters to validate.
        
        Raises:
            ParameterValidationError: If any parameter is invalid.
        """
        # Call parent validation first
        super()._validate_parameters(parameters)
        
        # Additional SMA-specific validation
        short_window = parameters.get('short_window')
        long_window = parameters.get('long_window')
        
        if short_window is not None and long_window is not None:
            if short_window >= long_window:
                raise ParameterValidationError(
                    f"short_window ({short_window}) must be less than long_window ({long_window})"
                )
        
        # Validate reasonable ranges
        if short_window is not None and (short_window < 2 or short_window > 500):
            raise ParameterValidationError(
                f"short_window must be between 2 and 500, got {short_window}"
            )
        
        if long_window is not None and (long_window < 3 or long_window > 1000):
            raise ParameterValidationError(
                f"long_window must be between 3 and 1000, got {long_window}"
            )