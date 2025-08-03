"""
Relative Strength Index (RSI) Threshold Strategy Implementation.

This module implements a momentum-based trading strategy using the Relative Strength
Index (RSI) indicator. The strategy generates buy signals when the RSI indicates
oversold conditions and sell signals when it indicates overbought conditions.

The RSI is a momentum oscillator that measures the speed and magnitude of price
changes, oscillating between 0 and 100. It's particularly effective for identifying
potential reversal points in trending markets.
"""

from typing import Dict, Any, Tuple, List, Optional
import pandas as pd
import numpy as np

from ..base.abstract_trading_strategy import AbstractTradingStrategy, ParameterValidationError, DataValidationError
from ..base.strategy_registry import register_strategy


@register_strategy
class RSIStrategy(AbstractTradingStrategy):
    """
    Relative Strength Index (RSI) Threshold Trading Strategy.
    
    This strategy implements a mean-reversion approach using the RSI momentum
    oscillator to identify overbought and oversold market conditions:
    
    - Buy Signal: RSI crosses below oversold threshold (typically 30)
    - Sell Signal: RSI crosses above overbought threshold (typically 70)
    
    The RSI oscillates between 0 and 100, with values above 70 generally considered
    overbought and values below 30 considered oversold. This strategy works best
    in ranging markets and may generate false signals in strong trending conditions.
    
    Parameters:
        period: Period for RSI calculation (default: 14)
        oversold_threshold: RSI level considered oversold for buy signals (default: 30)
        overbought_threshold: RSI level considered overbought for sell signals (default: 70)
    
    Technical Indicators:
        - RSI: Relative Strength Index over specified period
        - Oversold Line: Horizontal line at oversold threshold
        - Overbought Line: Horizontal line at overbought threshold
    
    Example:
        strategy = RSIStrategy(period=14, oversold_threshold=25, overbought_threshold=75)
        buy_signals, sell_signals = strategy.generate_signals(data)
    """
    

    @classmethod
    def get_parameter_definitions(cls) -> Dict[str, Dict[str, Any]]:
        """
        Define parameters for the RSI strategy with validation constraints.
        
        Returns:
            Dictionary containing parameter definitions with types, defaults,
            ranges, and descriptions for validation and UI generation.
        """
        return {
            'period': {
                'type': int,
                'default': 14,
                'range': (2, 50),
                'description': 'Period for RSI calculation (number of periods to look back)'
            },
            'oversold_threshold': {
                'type': float,
                'default': 30.0,
                'range': (10.0, 40.0),
                'description': 'RSI threshold below which market is considered oversold (buy signal)'
            },
            'overbought_threshold': {
                'type': float,
                'default': 70.0,
                'range': (60.0, 90.0),
                'description': 'RSI threshold above which market is considered overbought (sell signal)'
            }
        }
    

    def __init__(self, 
                 period: int = 14, 
                 oversold_threshold: float = 30.0, 
                 overbought_threshold: float = 70.0,
                 **kwargs: Any) -> None:
        """
        Initialize the RSI Threshold strategy.
        
        Args:
            period: Period for RSI calculation. Must be at least 2.
            oversold_threshold: RSI level for buy signals. Must be between 0 and 100,
                              and less than overbought_threshold.
            overbought_threshold: RSI level for sell signals. Must be between 0 and 100,
                                and greater than oversold_threshold.
            **kwargs: Additional parameters passed to the base class.
        
        Raises:
            ParameterValidationError: If parameters are invalid or violate constraints.
        """
        # Validate parameters before initialization
        if not isinstance(period, int) or period < 2:
            raise ParameterValidationError(
                f"period must be an integer >= 2, got {period}"
            )
        
        if not isinstance(oversold_threshold, (int, float)):
            raise ParameterValidationError(
                f"oversold_threshold must be a number, got {type(oversold_threshold)}"
            )
        
        if not isinstance(overbought_threshold, (int, float)):
            raise ParameterValidationError(
                f"overbought_threshold must be a number, got {type(overbought_threshold)}"
            )
        
        # Convert to float for consistency
        oversold_threshold = float(oversold_threshold)
        overbought_threshold = float(overbought_threshold)
        
        # Validate threshold ranges and relationships
        if not (0 <= oversold_threshold <= 100):
            raise ParameterValidationError(
                f"oversold_threshold must be between 0 and 100, got {oversold_threshold}"
            )
        
        if not (0 <= overbought_threshold <= 100):
            raise ParameterValidationError(
                f"overbought_threshold must be between 0 and 100, got {overbought_threshold}"
            )
        
        if oversold_threshold >= overbought_threshold:
            raise ParameterValidationError(
                f"oversold_threshold ({oversold_threshold}) must be less than "
                f"overbought_threshold ({overbought_threshold})"
            )
        
        # Prepare parameters dictionary
        parameters = {
            'period': period,
            'oversold_threshold': oversold_threshold,
            'overbought_threshold': overbought_threshold,
            **kwargs
        }
        
        # Initialize base class
        super().__init__(self.get_label(), parameters)
    

    def generate_signals(self, data: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """
        Generate buy and sell signals based on RSI threshold crossings.
        
        The strategy calculates the RSI indicator and generates signals when
        the RSI crosses the defined threshold levels:
        
        1. Calculate RSI using exponential moving averages of gains and losses
        2. Generate buy signals when RSI crosses below oversold threshold
        3. Generate sell signals when RSI crosses above overbought threshold
        
        Args:
            data: DataFrame containing OHLCV market data. Must include 'Close' column
                 and have sufficient rows for RSI calculation.
        
        Returns:
            Tuple containing two boolean Series:
            - buy_signals: True where RSI crosses below oversold threshold
            - sell_signals: True where RSI crosses above overbought threshold
        
        Raises:
            DataValidationError: If input data is invalid or insufficient.
        """
        # Validate input data
        self.validate_data(data)
        
        # Get strategy parameters
        period = self.parameters['period']
        oversold = self.parameters['oversold_threshold']
        overbought = self.parameters['overbought_threshold']
        
        # Check if we have sufficient data for RSI calculation
        min_required_rows = period + 10  # Extra buffer for stable RSI calculation
        if len(data) < min_required_rows:
            raise DataValidationError(
                f"Insufficient data: {len(data)} rows available, "
                f"but at least {min_required_rows} rows recommended for RSI({period}) calculation"
            )
        
        try:
            # Calculate RSI indicator
            rsi = self._calculate_rsi(data['Close'], period)
            
            # Generate threshold crossing signals
            # Buy signal: RSI crosses below oversold threshold (enters oversold territory)
            current_oversold = rsi < oversold
            previous_not_oversold = rsi.shift(1) >= oversold
            buy_signals = current_oversold & previous_not_oversold
            
            # Sell signal: RSI crosses above overbought threshold (enters overbought territory)
            current_overbought = rsi > overbought
            previous_not_overbought = rsi.shift(1) <= overbought
            sell_signals = current_overbought & previous_not_overbought
            
            # Store calculated indicators for visualization and analysis
            self.indicators = {
                'rsi': rsi,
                'oversold_line': pd.Series(oversold, index=data.index, name='Oversold'),
                'overbought_line': pd.Series(overbought, index=data.index, name='Overbought'),
                'period': period,
                'oversold_threshold': oversold,
                'overbought_threshold': overbought
            }
            
            return buy_signals, sell_signals
            
        except KeyError as e:
            raise DataValidationError(f"Missing required column in data: {e}") from e
        except Exception as e:
            raise DataValidationError(f"Error calculating RSI signals: {e}") from e
    

    def _calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """
        Calculate the Relative Strength Index (RSI) indicator.
        
        The RSI is calculated using the standard formula:
        RSI = 100 - (100 / (1 + RS))
        where RS = Average Gain / Average Loss over the specified period
        
        This implementation uses exponential moving averages for smoothing,
        which is the most common approach for RSI calculation.
        
        Args:
            prices: Series of closing prices.
            period: Period for RSI calculation.
        
        Returns:
            Series containing RSI values (0-100 range).
        
        Raises:
            ValueError: If calculation fails due to invalid data.
        """
        try:
            # Calculate price changes (deltas)
            delta = prices.diff()
            
            # Separate gains and losses
            gains = delta.where(delta > 0, 0.0)  # Positive changes only
            losses = -delta.where(delta < 0, 0.0)  # Absolute value of negative changes
            
            # Calculate exponential moving averages of gains and losses
            # Using adjust=False for consistency with standard RSI calculation
            avg_gains = gains.ewm(span=period, adjust=False).mean()
            avg_losses = losses.ewm(span=period, adjust=False).mean()
            
            # Handle division by zero case
            # When avg_losses is 0, RSI should be 100
            rs = avg_gains / avg_losses.replace(0, np.inf)
            
            # Calculate RSI using standard formula
            rsi = 100.0 - (100.0 / (1.0 + rs))
            
            # Handle edge cases where RS is infinite (avg_losses = 0)
            rsi = rsi.replace([np.inf, -np.inf], 100.0)
            
            # Ensure RSI is within valid range [0, 100]
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
        period = self.parameters['period']
        oversold = self.parameters['oversold_threshold']
        overbought = self.parameters['overbought_threshold']
        
        return (
            f"{self.get_label()} Strategy with {period}-period RSI calculation.\n\n"
            f"Signal Generation:\n"
            f"• BUY: When RSI crosses below {oversold:.1f} (enters oversold territory)\n"
            f"• SELL: When RSI crosses above {overbought:.1f} (enters overbought territory)\n\n"
            f"The RSI oscillates between 0 and 100, measuring momentum and identifying "
            f"potential reversal points. This mean-reversion strategy works best in "
            f"ranging markets but may generate false signals during strong trends. "
            f"Lower oversold thresholds and higher overbought thresholds reduce signal "
            f"frequency but may improve signal quality."
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
            "RSI 14 (30.0/70.0)" (with config) or "RSI" (without config)
        """
        if config and 'period' in config:
            oversold = config.get('oversold_threshold', 30)
            overbought = config.get('overbought_threshold', 70)
            return f"{cls.get_short_label()} {config['period']} ({oversold:.1f}/{overbought:.1f})"
        return cls.get_short_label()
    

    @classmethod
    def get_label(cls) -> str:
        """
        Get the full human-readable label of the strategy.
        
        Returns:
            Full strategy name for display in user interfaces.
        """
        return "Relative Strength Index"
    

    @classmethod
    def get_short_label(cls) -> str:
        """
        Get a short abbreviation for the strategy.
        
        Returns:
            Short strategy identifier for compact displays.
        """
        return "RSI"
    

    @classmethod
    def get_predefined_configurations(cls) -> List[Dict[str, Any]]:
        """
        Get predefined parameter configurations for strategy comparison and testing.
        
        Provides a variety of commonly used RSI configurations that represent
        different sensitivity levels and threshold combinations.
        
        Returns:
            List of parameter dictionaries representing different strategy configurations.
            Each configuration includes period, oversold_threshold, and overbought_threshold.
        """
        return [
            # Standard configurations with different periods
            {'period': 7, 'oversold_threshold': 30.0, 'overbought_threshold': 70.0},   # Fast RSI
            {'period': 14, 'oversold_threshold': 30.0, 'overbought_threshold': 70.0},  # Classic RSI
            {'period': 21, 'oversold_threshold': 30.0, 'overbought_threshold': 70.0},  # Slower RSI
            
            # More sensitive thresholds (more signals)
            {'period': 14, 'oversold_threshold': 35.0, 'overbought_threshold': 65.0},  # Sensitive
            {'period': 14, 'oversold_threshold': 40.0, 'overbought_threshold': 60.0},  # Very sensitive
            
            # Less sensitive thresholds (fewer, potentially higher quality signals)
            {'period': 14, 'oversold_threshold': 25.0, 'overbought_threshold': 75.0},  # Conservative
            {'period': 14, 'oversold_threshold': 20.0, 'overbought_threshold': 80.0},  # Very conservative
            
            # Alternative period combinations
            {'period': 9, 'oversold_threshold': 25.0, 'overbought_threshold': 75.0},   # Fast + conservative
            {'period': 28, 'oversold_threshold': 35.0, 'overbought_threshold': 65.0},  # Slow + sensitive
        ]
    
    
    def get_indicators(self) -> Dict[str, pd.Series]:
        """
        Get calculated technical indicators for visualization and analysis.
        
        Returns the RSI values and threshold lines that were calculated during
        signal generation. This data can be used for plotting charts or further
        technical analysis.
        
        Returns:
            Dictionary containing calculated indicators:
            - 'rsi': Relative Strength Index values
            - 'oversold_line': Horizontal line at oversold threshold
            - 'overbought_line': Horizontal line at overbought threshold
            - 'period': RSI calculation period
            - 'oversold_threshold': Oversold threshold value
            - 'overbought_threshold': Overbought threshold value
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
        
        # Additional RSI-specific validation
        period = parameters.get('period')
        oversold = parameters.get('oversold_threshold')
        overbought = parameters.get('overbought_threshold')
        
        # Validate period
        if period is not None and (period < 2 or period > 100):
            raise ParameterValidationError(
                f"period must be between 2 and 100, got {period}"
            )
        
        # Validate threshold relationship
        if oversold is not None and overbought is not None:
            if oversold >= overbought:
                raise ParameterValidationError(
                    f"oversold_threshold ({oversold}) must be less than "
                    f"overbought_threshold ({overbought})"
                )
        
        # Validate threshold ranges
        if oversold is not None and not (0 <= oversold <= 50):
            raise ParameterValidationError(
                f"oversold_threshold should be between 0 and 50, got {oversold}"
            )
        
        if overbought is not None and not (50 <= overbought <= 100):
            raise ParameterValidationError(
                f"overbought_threshold should be between 50 and 100, got {overbought}"
            )