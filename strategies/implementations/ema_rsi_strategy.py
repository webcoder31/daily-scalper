"""
EMA + RSI Combined Strategy Implementation.

This module implements a sophisticated trading strategy that combines Exponential
Moving Average (EMA) crossover signals with Relative Strength Index (RSI) filtering.
The strategy uses EMA crossovers to identify trend direction and RSI to filter
signals based on momentum conditions.

This combined approach aims to reduce false signals by requiring both trend
confirmation (EMA crossover) and momentum validation (RSI filter) before
generating trading signals.
"""

from typing import Dict, Any, Tuple, List, Optional
from itertools import product
import pandas as pd
import numpy as np

from ..base.abstract_strategy import AbstractStrategy, ParameterValidationError, DataValidationError
from ..base.strategy_registry import register_strategy


@register_strategy
class EMARSIStrategy(AbstractStrategy):
    """
    EMA + RSI Combined Trading Strategy.
    
    This strategy combines two popular technical indicators to create a more
    sophisticated trading approach:
    
    1. EMA Crossover: Uses fast and slow Exponential Moving Averages to identify trend direction
    2. RSI Filter: Uses Relative Strength Index to validate momentum conditions
    
    Trading Signals:
    - Buy Signal: Fast EMA crosses above Slow EMA AND RSI > entry threshold
    - Sell Signal: Fast EMA crosses below Slow EMA OR RSI < exit threshold
    
    The strategy aims to capture trending moves while avoiding trades during
    weak momentum conditions. The RSI filter helps reduce false breakouts
    and improves signal quality.
    
    Parameters:
        ema_fast: Period for the fast EMA (default: 10)
        ema_slow: Period for the slow EMA (default: 30)
        rsi_period: Period for RSI calculation (default: 14)
        rsi_entry: Minimum RSI level to allow buy signals (default: 50)
        rsi_exit: Maximum RSI level before forcing sell signals (default: 40)
    
    Technical Indicators:
        - Fast EMA: Exponential moving average over ema_fast periods
        - Slow EMA: Exponential moving average over ema_slow periods
        - RSI: Relative Strength Index over rsi_period periods
    
    Example:
        strategy = EMARSIStrategy(ema_fast=8, ema_slow=25, rsi_period=14, 
                                 rsi_entry=45, rsi_exit=35)
        buy_signals, sell_signals = strategy.generate_signals(data)
    """
    

    @classmethod
    def get_parameter_definitions(cls) -> Dict[str, Dict[str, Any]]:
        """
        Define parameters for the EMA+RSI strategy with validation constraints.
        
        Returns:
            Dictionary containing parameter definitions with types, defaults,
            ranges, and descriptions for validation and UI generation.
        """
        return {
            'ema_fast': {
                'type': int,
                'default': 10,
                'range': (5, 50),
                'description': 'Period for the fast Exponential Moving Average'
            },
            'ema_slow': {
                'type': int,
                'default': 30,
                'range': (10, 200),
                'description': 'Period for the slow Exponential Moving Average'
            },
            'rsi_period': {
                'type': int,
                'default': 14,
                'range': (5, 50),
                'description': 'Period for RSI calculation'
            },
            'rsi_entry': {
                'type': float,
                'default': 50.0,
                'range': (40.0, 60.0),
                'description': 'Minimum RSI level to allow buy signals (momentum filter)'
            },
            'rsi_exit': {
                'type': float,
                'default': 40.0,
                'range': (30.0, 50.0),
                'description': 'Maximum RSI level before forcing sell signals (weakness filter)'
            }
        }
    

    def __init__(self, 
                 ema_fast: int = 10, 
                 ema_slow: int = 30, 
                 rsi_period: int = 14, 
                 rsi_entry: float = 50.0, 
                 rsi_exit: float = 40.0, 
                 **kwargs: Any) -> None:
        """
        Initialize the EMA + RSI combined strategy.
        
        Args:
            ema_fast: Period for the fast EMA. Must be positive and less than ema_slow.
            ema_slow: Period for the slow EMA. Must be positive and greater than ema_fast.
            rsi_period: Period for RSI calculation. Must be at least 2.
            rsi_entry: Minimum RSI level for buy signals. Must be between 0 and 100,
                      and greater than rsi_exit.
            rsi_exit: Maximum RSI level before sell signals. Must be between 0 and 100,
                     and less than rsi_entry.
            **kwargs: Additional parameters passed to the base class.
        
        Raises:
            ParameterValidationError: If parameters are invalid or violate constraints.
        """
        # Validate parameters before initialization
        if not isinstance(ema_fast, int) or ema_fast < 1:
            raise ParameterValidationError(
                f"ema_fast must be a positive integer, got {ema_fast}"
            )
        
        if not isinstance(ema_slow, int) or ema_slow < 1:
            raise ParameterValidationError(
                f"ema_slow must be a positive integer, got {ema_slow}"
            )
        
        if not isinstance(rsi_period, int) or rsi_period < 2:
            raise ParameterValidationError(
                f"rsi_period must be an integer >= 2, got {rsi_period}"
            )
        
        if not isinstance(rsi_entry, (int, float)):
            raise ParameterValidationError(
                f"rsi_entry must be a number, got {type(rsi_entry)}"
            )
        
        if not isinstance(rsi_exit, (int, float)):
            raise ParameterValidationError(
                f"rsi_exit must be a number, got {type(rsi_exit)}"
            )
        
        # Convert to appropriate types
        rsi_entry = float(rsi_entry)
        rsi_exit = float(rsi_exit)
        
        # Validate EMA relationship
        if ema_fast >= ema_slow:
            raise ParameterValidationError(
                f"ema_fast ({ema_fast}) must be less than ema_slow ({ema_slow})"
            )
        
        # Validate RSI ranges
        if not (0 <= rsi_entry <= 100):
            raise ParameterValidationError(
                f"rsi_entry must be between 0 and 100, got {rsi_entry}"
            )
        
        if not (0 <= rsi_exit <= 100):
            raise ParameterValidationError(
                f"rsi_exit must be between 0 and 100, got {rsi_exit}"
            )
        
        # Validate RSI relationship
        if rsi_exit >= rsi_entry:
            raise ParameterValidationError(
                f"rsi_exit ({rsi_exit}) must be less than rsi_entry ({rsi_entry})"
            )
        
        # Prepare parameters dictionary
        parameters = {
            'ema_fast': ema_fast,
            'ema_slow': ema_slow,
            'rsi_period': rsi_period,
            'rsi_entry': rsi_entry,
            'rsi_exit': rsi_exit,
            **kwargs
        }
        
        # Initialize base class
        super().__init__(self.get_label(), parameters)
    

    def generate_signals(self, data: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """
        Generate buy and sell signals based on EMA crossovers with RSI filtering.
        
        The strategy combines EMA crossover signals with RSI momentum filtering:
        
        1. Calculate fast and slow EMAs
        2. Calculate RSI indicator
        3. Generate buy signals when fast EMA crosses above slow EMA AND RSI > entry threshold
        4. Generate sell signals when fast EMA crosses below slow EMA OR RSI < exit threshold
        
        Args:
            data: DataFrame containing OHLCV market data. Must include 'Close' column
                 and have sufficient rows for the longest calculation period.
        
        Returns:
            Tuple containing two boolean Series:
            - buy_signals: True where EMA bullish crossover occurs with RSI confirmation
            - sell_signals: True where EMA bearish crossover occurs OR RSI weakness detected
        
        Raises:
            DataValidationError: If input data is invalid or insufficient.
        """
        # Validate input data
        self.validate_data(data)
        
        # Get strategy parameters
        params = self.parameters
        ema_fast_period = params['ema_fast']
        ema_slow_period = params['ema_slow']
        rsi_period = params['rsi_period']
        rsi_entry_threshold = params['rsi_entry']
        rsi_exit_threshold = params['rsi_exit']
        
        # Check if we have sufficient data for calculations
        max_period = max(ema_slow_period, rsi_period)
        min_required_rows = max_period + 10  # Extra buffer for stable calculations
        if len(data) < min_required_rows:
            raise DataValidationError(
                f"Insufficient data: {len(data)} rows available, "
                f"but at least {min_required_rows} rows required for EMA({ema_slow_period}) "
                f"and RSI({rsi_period}) calculations"
            )
        
        try:
            close_prices = data['Close']
            
            # Calculate Exponential Moving Averages
            ema_fast = close_prices.ewm(span=ema_fast_period, adjust=False).mean()
            ema_slow = close_prices.ewm(span=ema_slow_period, adjust=False).mean()
            
            # Calculate RSI using simple moving average method for consistency
            rsi = self._calculate_rsi(close_prices, rsi_period)
            
            # Identify EMA crossovers
            # Bullish crossover: Fast EMA crosses above Slow EMA
            current_bullish = ema_fast > ema_slow
            previous_bearish = ema_fast.shift(1) <= ema_slow.shift(1)
            ema_bullish_crossover = current_bullish & previous_bearish
            
            # Bearish crossover: Fast EMA crosses below Slow EMA
            current_bearish = ema_fast < ema_slow
            previous_bullish = ema_fast.shift(1) >= ema_slow.shift(1)
            ema_bearish_crossover = current_bearish & previous_bullish
            
            # Apply RSI filters
            # Buy signal: EMA bullish crossover AND RSI above entry threshold
            buy_signals = ema_bullish_crossover & (rsi > rsi_entry_threshold)
            
            # Sell signal: EMA bearish crossover OR RSI below exit threshold
            sell_signals = ema_bearish_crossover | (rsi < rsi_exit_threshold)
            
            # Store calculated indicators for visualization and analysis
            self.indicators = {
                'ema_fast': ema_fast,
                'ema_slow': ema_slow,
                'rsi': rsi,
                'ema_fast_period': ema_fast_period,
                'ema_slow_period': ema_slow_period,
                'rsi_period': rsi_period,
                'rsi_entry_threshold': rsi_entry_threshold,
                'rsi_exit_threshold': rsi_exit_threshold,
                'ema_spread': ema_fast - ema_slow,  # EMA spread for analysis
                'rsi_entry_line': pd.Series(rsi_entry_threshold, index=data.index),
                'rsi_exit_line': pd.Series(rsi_exit_threshold, index=data.index)
            }
            
            return buy_signals, sell_signals
            
        except KeyError as e:
            raise DataValidationError(f"Missing required column in data: {e}") from e
        except Exception as e:
            raise DataValidationError(f"Error calculating EMA+RSI signals: {e}") from e
    

    def _calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """
        Calculate the Relative Strength Index (RSI) indicator.
        
        Uses simple moving averages for gain and loss calculations to ensure
        consistency and stability in the RSI calculation.
        
        Args:
            prices: Series of closing prices.
            period: Period for RSI calculation.
        
        Returns:
            Series containing RSI values (0-100 range).
        
        Raises:
            ValueError: If calculation fails due to invalid data.
        """
        try:
            # Calculate price changes
            delta = prices.diff()
            
            # Separate gains and losses
            gains = delta.clip(lower=0)  # Positive changes only
            losses = -delta.clip(upper=0)  # Absolute value of negative changes
            
            # Calculate simple moving averages of gains and losses
            avg_gains = gains.rolling(window=period, min_periods=period).mean()
            avg_losses = losses.rolling(window=period, min_periods=period).mean()
            
            # Calculate Relative Strength (RS) and RSI
            # Handle division by zero case
            rs = avg_gains / avg_losses.replace(0, np.inf)
            rsi = 100.0 - (100.0 / (1.0 + rs))
            
            # Handle edge cases
            rsi = rsi.replace([np.inf, -np.inf], 100.0)
            rsi = rsi.clip(0.0, 100.0)
            
            return rsi
            
        except Exception as e:
            raise ValueError(f"Failed to calculate RSI: {e}") from e
    

    def get_explanation(self) -> str:
        """
        Get a detailed explanation of the strategy logic and current parameters.
        
        Returns:
            Human-readable explanation of how the strategy works, including
            current parameter values and signal generation logic.
        """
        params = self.parameters
        
        return (
            f"{self.get_label()} combining EMA crossover with RSI momentum filtering.\n\n"
            f"EMA Configuration:\n"
            f"• Fast EMA: {params['ema_fast']} periods\n"
            f"• Slow EMA: {params['ema_slow']} periods\n\n"
            f"RSI Configuration:\n"
            f"• RSI Period: {params['rsi_period']} periods\n"
            f"• Entry Threshold: {params['rsi_entry']:.1f} (minimum RSI for buy signals)\n"
            f"• Exit Threshold: {params['rsi_exit']:.1f} (maximum RSI before sell signals)\n\n"
            f"Signal Generation:\n"
            f"• BUY: Fast EMA crosses above Slow EMA AND RSI > {params['rsi_entry']:.1f}\n"
            f"• SELL: Fast EMA crosses below Slow EMA OR RSI < {params['rsi_exit']:.1f}\n\n"
            f"This combined strategy aims to capture trending moves while filtering out "
            f"weak momentum conditions. The RSI filter helps avoid false breakouts and "
            f"ensures trades are taken only when momentum supports the trend direction."
        )
    

    @classmethod
    def get_label(cls) -> str:
        """
        Get the full human-readable label of the strategy.
        
        Returns:
            Full strategy name for display in user interfaces.
        """
        return "EMA + RSI Strategy"


    @classmethod
    def get_short_label(cls) -> str:
        """
        Get a short abbreviation for the strategy.
        
        Returns:
            Short strategy identifier for compact displays.
        """
        return "EMA+RSI"


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
            "EMA10/30 + RSI(14), entry>50, exit<40" (with config) or "EMA+RSI" (without config)
        """
        if config:
            ema_fast = config.get('ema_fast', 10)
            ema_slow = config.get('ema_slow', 30)
            rsi_period = config.get('rsi_period', 14)
            rsi_entry = config.get('rsi_entry', 50)
            rsi_exit = config.get('rsi_exit', 40)
            
            return (
                f"EMA{ema_fast}/{ema_slow} + RSI({rsi_period}), "
                f"entry>{rsi_entry:.0f}, exit<{rsi_exit:.0f}"
            )
        return cls.get_short_label()


    @classmethod
    def get_predefined_configurations(cls) -> List[Dict[str, Any]]:
        """
        Get predefined parameter configurations for strategy comparison and testing.
        
        Provides a comprehensive grid of parameter combinations around optimized
        values, allowing for systematic testing and comparison of different
        configuration variations.
        
        Returns:
            List of parameter dictionaries representing different strategy configurations.
            Each configuration includes all required parameters with valid combinations.
        """
        # Define parameter ranges around optimal values found through testing
        ema_fast_range = [8, 10, 12]
        ema_slow_range = [25, 30, 35]
        rsi_period_range = [14]  # Can be expanded to [12, 14, 16] for more variations
        rsi_entry_range = [40, 42, 44]
        rsi_exit_range = [28, 30, 32]

        # Generate all valid combinations using Cartesian product
        parameter_grid = product(
            ema_fast_range,
            ema_slow_range,
            rsi_period_range,
            rsi_entry_range,
            rsi_exit_range,
        )

        # Create configuration dictionaries with validation
        configurations = []
        for ema_fast, ema_slow, rsi_period, rsi_entry, rsi_exit in parameter_grid:
            # Filter out invalid combinations
            if ema_fast < ema_slow and rsi_exit < rsi_entry:
                configurations.append({
                    'ema_fast': ema_fast,
                    'ema_slow': ema_slow,
                    'rsi_period': rsi_period,
                    'rsi_entry': rsi_entry,
                    'rsi_exit': rsi_exit
                })
        
        # Add some additional hand-picked configurations for variety
        additional_configs = [
            # Conservative configurations
            {'ema_fast': 15, 'ema_slow': 45, 'rsi_period': 21, 'rsi_entry': 55, 'rsi_exit': 35},
            {'ema_fast': 20, 'ema_slow': 50, 'rsi_period': 14, 'rsi_entry': 52, 'rsi_exit': 38},
            
            # Aggressive configurations
            {'ema_fast': 5, 'ema_slow': 15, 'rsi_period': 7, 'rsi_entry': 45, 'rsi_exit': 35},
            {'ema_fast': 8, 'ema_slow': 21, 'rsi_period': 10, 'rsi_entry': 48, 'rsi_exit': 32},
        ]
        
        configurations.extend(additional_configs)
        
        return configurations


    def get_indicators(self) -> Dict[str, pd.Series]:
        """
        Get calculated technical indicators for visualization and analysis.
        
        Returns all indicators calculated during signal generation, including
        EMAs, RSI, and derived metrics that can be used for plotting charts
        or further technical analysis.
        
        Returns:
            Dictionary containing calculated indicators:
            - 'ema_fast': Fast Exponential Moving Average
            - 'ema_slow': Slow Exponential Moving Average
            - 'rsi': Relative Strength Index values
            - 'ema_spread': Difference between fast and slow EMAs
            - 'rsi_entry_line': Horizontal line at RSI entry threshold
            - 'rsi_exit_line': Horizontal line at RSI exit threshold
            - Parameter values for reference
        """
        return getattr(self, 'indicators', {})


    def _validate_parameters(self, parameters: Dict[str, Any]) -> None:
        """
        Validate strategy parameters against constraints.
        
        Performs comprehensive validation of strategy parameters including
        type checking, range validation, and logical consistency checks
        specific to the EMA+RSI strategy.
        
        Args:
            parameters: Dictionary of parameters to validate.
        
        Raises:
            ParameterValidationError: If any parameter is invalid.
        """
        # Call parent validation first
        super()._validate_parameters(parameters)
        
        # Additional EMA+RSI-specific validation
        ema_fast = parameters.get('ema_fast')
        ema_slow = parameters.get('ema_slow')
        rsi_period = parameters.get('rsi_period')
        rsi_entry = parameters.get('rsi_entry')
        rsi_exit = parameters.get('rsi_exit')
        
        # Validate EMA relationship
        if ema_fast is not None and ema_slow is not None:
            if ema_fast >= ema_slow:
                raise ParameterValidationError(
                    f"ema_fast ({ema_fast}) must be less than ema_slow ({ema_slow})"
                )
        
        # Validate RSI relationship
        if rsi_entry is not None and rsi_exit is not None:
            if rsi_exit >= rsi_entry:
                raise ParameterValidationError(
                    f"rsi_exit ({rsi_exit}) must be less than rsi_entry ({rsi_entry})"
                )
        
        # Validate reasonable parameter ranges
        if ema_fast is not None and (ema_fast < 2 or ema_fast > 100):
            raise ParameterValidationError(
                f"ema_fast must be between 2 and 100, got {ema_fast}"
            )
        
        if ema_slow is not None and (ema_slow < 5 or ema_slow > 500):
            raise ParameterValidationError(
                f"ema_slow must be between 5 and 500, got {ema_slow}"
            )
        
        if rsi_period is not None and (rsi_period < 2 or rsi_period > 100):
            raise ParameterValidationError(
                f"rsi_period must be between 2 and 100, got {rsi_period}"
            )
        
        if rsi_entry is not None and not (20 <= rsi_entry <= 80):
            raise ParameterValidationError(
                f"rsi_entry should be between 20 and 80 for practical use, got {rsi_entry}"
            )
        
        if rsi_exit is not None and not (10 <= rsi_exit <= 70):
            raise ParameterValidationError(
                f"rsi_exit should be between 10 and 70 for practical use, got {rsi_exit}"
            )
