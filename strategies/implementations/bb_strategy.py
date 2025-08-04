"""
Bollinger Bands Mean Reversion Strategy Implementation.

This module implements a mean reversion trading strategy using Bollinger Bands,
a technical analysis tool that consists of a moving average and two standard
deviation bands above and below it. The strategy generates buy signals when
price touches or crosses below the lower band and sell signals when price
touches or crosses above the upper band.

Bollinger Bands are particularly effective for identifying overbought and
oversold conditions in ranging markets, making this strategy well-suited
for mean reversion trading approaches.
"""

from typing import Dict, Any, Tuple, List, Optional
import pandas as pd
import numpy as np

from ..base.abstract_strategy import AbstractStrategy, ParameterValidationError, DataValidationError
from ..base.strategy_registry import register_strategy


@register_strategy
class BBStrategy(AbstractStrategy):
    """
    Bollinger Bands Mean Reversion Trading Strategy.
    
    This strategy implements a mean reversion approach using Bollinger Bands,
    which consist of three components:
    
    1. Middle Band: Simple Moving Average (SMA) of closing prices
    2. Upper Band: Middle Band + (Standard Deviation × Multiplier)
    3. Lower Band: Middle Band - (Standard Deviation × Multiplier)
    
    Trading Signals:
    - Buy Signal: Price crosses below the lower Bollinger Band (oversold condition)
    - Sell Signal: Price crosses above the upper Bollinger Band (overbought condition)
    
    The strategy assumes that prices tend to revert to the mean (middle band)
    after touching the outer bands, making it effective in ranging markets
    but potentially problematic in strong trending conditions.
    
    Parameters:
        period: Period for the moving average and standard deviation calculation (default: 20)
        std_dev: Number of standard deviations for band calculation (default: 2.0)
    
    Technical Indicators:
        - Middle Band: Simple moving average of closing prices
        - Upper Band: Middle band + (std_dev × standard deviation)
        - Lower Band: Middle band - (std_dev × standard deviation)
    
    Example:
        strategy = BBStrategy(period=20, std_dev=2.5)
        buy_signals, sell_signals = strategy.generate_signals(data)
    """


    @classmethod
    def get_parameter_definitions(cls) -> Dict[str, Dict[str, Any]]:
        """
        Define parameters for the Bollinger Bands strategy with validation constraints.
        
        Returns:
            Dictionary containing parameter definitions with types, defaults,
            ranges, and descriptions for validation and UI generation.
        """
        return {
            'period': {
                'type': int,
                'default': 20,
                'range': (5, 50),
                'description': 'Period for moving average and standard deviation calculation'
            },
            'std_dev': {
                'type': float,
                'default': 2.0,
                'range': (1.0, 3.0),
                'description': 'Number of standard deviations for upper and lower bands'
            }
        }
    

    def __init__(self, 
                 period: int = 20, 
                 std_dev: float = 2.0,
                 **kwargs: Any) -> None:
        """
        Initialize the Bollinger Bands strategy.
        
        Args:
            period: Period for moving average and standard deviation calculation.
                   Must be at least 2.
            std_dev: Number of standard deviations for band calculation.
                    Must be positive.
            **kwargs: Additional parameters passed to the base class.
        
        Raises:
            ParameterValidationError: If parameters are invalid or violate constraints.
        """
        # Validate parameters before initialization
        if not isinstance(period, int) or period < 2:
            raise ParameterValidationError(
                f"period must be an integer >= 2, got {period}"
            )
        
        if not isinstance(std_dev, (int, float)) or std_dev <= 0:
            raise ParameterValidationError(
                f"std_dev must be a positive number, got {std_dev}"
            )
        
        # Convert to float for consistency
        std_dev = float(std_dev)
        
        # Validate reasonable ranges
        if period > 200:
            raise ParameterValidationError(
                f"period should not exceed 200 for practical purposes, got {period}"
            )
        
        if std_dev > 5.0:
            raise ParameterValidationError(
                f"std_dev should not exceed 5.0 for practical purposes, got {std_dev}"
            )
        
        # Prepare parameters dictionary
        parameters = {
            'period': period,
            'std_dev': std_dev,
            **kwargs
        }
        
        # Initialize base class
        super().__init__(self.get_label(), parameters)
    

    def generate_signals(self, data: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """
        Generate buy and sell signals based on Bollinger Bands crossings.
        
        The strategy calculates Bollinger Bands and generates signals when
        price crosses the outer bands:
        
        1. Calculate middle band (SMA) and standard deviation
        2. Calculate upper and lower bands using std_dev multiplier
        3. Generate buy signals when price crosses below lower band
        4. Generate sell signals when price crosses above upper band
        
        Args:
            data: DataFrame containing OHLCV market data. Must include 'Close' column
                 and have sufficient rows for moving average calculation.
        
        Returns:
            Tuple containing two boolean Series:
            - buy_signals: True where price crosses below lower Bollinger Band
            - sell_signals: True where price crosses above upper Bollinger Band
        
        Raises:
            DataValidationError: If input data is invalid or insufficient.
        """
        # Validate input data
        self.validate_data(data)
        
        # Get strategy parameters
        period = self.parameters['period']
        std_dev_multiplier = self.parameters['std_dev']
        
        # Check if we have sufficient data for calculation
        min_required_rows = period + 5  # Extra buffer for stable calculation
        if len(data) < min_required_rows:
            raise DataValidationError(
                f"Insufficient data: {len(data)} rows available, "
                f"but at least {min_required_rows} rows required for Bollinger Bands({period}) calculation"
            )
        
        try:
            # Calculate Bollinger Bands components
            close_prices = data['Close']
            
            # Middle band: Simple Moving Average
            middle_band = close_prices.rolling(window=period, min_periods=period).mean()
            
            # Standard deviation over the same period
            rolling_std = close_prices.rolling(window=period, min_periods=period).std()
            
            # Upper and lower bands
            upper_band = middle_band + (rolling_std * std_dev_multiplier)
            lower_band = middle_band - (rolling_std * std_dev_multiplier)
            
            # Generate crossing signals
            # Buy signal: Price crosses below lower band (enters oversold territory)
            current_below_lower = close_prices < lower_band
            previous_above_lower = close_prices.shift(1) >= lower_band.shift(1)
            buy_signals = current_below_lower & previous_above_lower
            
            # Sell signal: Price crosses above upper band (enters overbought territory)
            current_above_upper = close_prices > upper_band
            previous_below_upper = close_prices.shift(1) <= upper_band.shift(1)
            sell_signals = current_above_upper & previous_below_upper
            
            # Store calculated indicators for visualization and analysis
            self.indicators = {
                'middle_band': middle_band,
                'upper_band': upper_band,
                'lower_band': lower_band,
                'period': period,
                'std_dev': std_dev_multiplier,
                'bandwidth': (upper_band - lower_band) / middle_band * 100,  # Bollinger Band Width
                'percent_b': (close_prices - lower_band) / (upper_band - lower_band)  # %B indicator
            }
            
            return buy_signals, sell_signals
            
        except KeyError as e:
            raise DataValidationError(f"Missing required column in data: {e}") from e
        except Exception as e:
            raise DataValidationError(f"Error calculating Bollinger Bands signals: {e}") from e
    

    def get_explanation(self) -> str:
        """
        Get a detailed explanation of the strategy logic and current parameters.
        
        Returns:
            Human-readable explanation of how the strategy works, including
            current parameter values and signal generation logic.
        """
        period = self.parameters['period']
        std_dev = self.parameters['std_dev']
        
        return (
            f"{self.get_label()} Strategy with {period}-period moving average and "
            f"{std_dev:.1f} standard deviation bands.\n\n"
            f"Band Calculation:\n"
            f"• Middle Band: {period}-period Simple Moving Average\n"
            f"• Upper Band: Middle Band + ({std_dev:.1f} × Standard Deviation)\n"
            f"• Lower Band: Middle Band - ({std_dev:.1f} × Standard Deviation)\n\n"
            f"Signal Generation:\n"
            f"• BUY: When price crosses below the Lower Band (mean reversion from oversold)\n"
            f"• SELL: When price crosses above the Upper Band (mean reversion from overbought)\n\n"
            f"This mean reversion strategy assumes prices will return to the middle band "
            f"after touching the outer bands. It works best in ranging markets but may "
            f"generate false signals during strong trends. Wider bands (higher std_dev) "
            f"reduce signal frequency but may improve signal quality."
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
            "BB 20/2.0" (with config) or "BB" (without config)
        """
        if config and 'period' in config and 'std_dev' in config:
            return f"{cls.get_short_label()} {config['period']}/{config['std_dev']:.1f}"
        return cls.get_short_label()
    

    @classmethod
    def get_label(cls) -> str:
        """
        Get the full human-readable label of the strategy.
        
        Returns:
            Full strategy name for display in user interfaces.
        """
        return "Bollinger Bands"
    

    @classmethod
    def get_short_label(cls) -> str:
        """
        Get a short abbreviation for the strategy.
        
        Returns:
            Short strategy identifier for compact displays.
        """
        return "BB"
    

    @classmethod
    def get_predefined_configurations(cls) -> List[Dict[str, Any]]:
        """
        Get predefined parameter configurations for strategy comparison and testing.
        
        Provides a variety of commonly used Bollinger Bands configurations that
        represent different sensitivity levels and band widths.
        
        Returns:
            List of parameter dictionaries representing different strategy configurations.
            Each configuration includes period and std_dev parameters.
        """
        return [
            # Standard configurations
            {'period': 20, 'std_dev': 2.0},   # Classic Bollinger Bands
            {'period': 20, 'std_dev': 1.5},   # Tighter bands (more sensitive)
            {'period': 20, 'std_dev': 2.5},   # Wider bands (less sensitive)
            
            # Different periods with standard deviation
            {'period': 10, 'std_dev': 2.0},   # Shorter period (more responsive)
            {'period': 30, 'std_dev': 2.0},   # Longer period (smoother)
            {'period': 50, 'std_dev': 2.0},   # Long-term bands
            
            # Alternative combinations
            {'period': 15, 'std_dev': 1.8},   # Moderate sensitivity
            {'period': 25, 'std_dev': 2.2},   # Conservative approach
            {'period': 12, 'std_dev': 2.5},   # Fast with wide bands
            
            # Extreme configurations for testing
            {'period': 5, 'std_dev': 1.0},    # Very fast and tight
            {'period': 40, 'std_dev': 3.0},   # Very slow and wide
        ]
    
    
    def get_indicators(self) -> Dict[str, pd.Series]:
        """
        Get calculated technical indicators for visualization and analysis.
        
        Returns the Bollinger Bands components and additional indicators that were
        calculated during signal generation. This data can be used for plotting
        charts or further technical analysis.
        
        Returns:
            Dictionary containing calculated indicators:
            - 'middle_band': Simple moving average (middle Bollinger Band)
            - 'upper_band': Upper Bollinger Band
            - 'lower_band': Lower Bollinger Band
            - 'period': Moving average period
            - 'std_dev': Standard deviation multiplier
            - 'bandwidth': Bollinger Band Width (volatility measure)
            - 'percent_b': %B indicator (position within bands)
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
        
        # Additional Bollinger Bands-specific validation
        period = parameters.get('period')
        std_dev = parameters.get('std_dev')
        
        # Validate period range
        if period is not None and (period < 2 or period > 500):
            raise ParameterValidationError(
                f"period must be between 2 and 500, got {period}"
            )
        
        # Validate std_dev range
        if std_dev is not None and (std_dev <= 0 or std_dev > 10):
            raise ParameterValidationError(
                f"std_dev must be between 0 and 10, got {std_dev}"
            )
        
        # Warn about potentially problematic combinations
        if period is not None and std_dev is not None:
            if period < 10 and std_dev < 1.5:
                # This combination might generate too many signals
                pass  # Could add warning logging here
            
            if period > 50 and std_dev > 3.0:
                # This combination might generate too few signals
                pass  # Could add warning logging here