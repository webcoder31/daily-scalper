# Strategy Implementation Guide for Trading Strategy Backtester

This document provides a comprehensive guide on how to implement new trading strategies for the Trading Strategy Backtester application.

## Table of Contents
- [Strategy Implementation Guide for Trading Strategy Backtester](#strategy-implementation-guide-for-trading-strategy-backtester)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Strategy Architecture](#strategy-architecture)
    - [Directory Structure](#directory-structure)
  - [Step-by-Step Implementation Guide](#step-by-step-implementation-guide)
    - [1. Create a New Strategy File](#1-create-a-new-strategy-file)
    - [2. Import Required Modules](#2-import-required-modules)
    - [3. Define Your Strategy Class](#3-define-your-strategy-class)
    - [4. Implement Instance Methods](#4-implement-instance-methods)
    - [5. Implement Parameter Definitions Method](#5-implement-parameter-definitions-method)
    - [6. Implement Label, Abbreviated Name and Parameter Summary Methods](#6-implement-label-abbreviated-name-and-parameter-summary-methods)
    - [7. Implement Predefined Configurations](#7-implement-predefined-configurations)
    - [8. (Optional) Implement Additional Methods](#8-optional-implement-additional-methods)
  - [Required Methods](#required-methods)
  - [Optional Methods](#optional-methods)
  - [Strategy Registration](#strategy-registration)
  - [Parameter Definition Best Practices](#parameter-definition-best-practices)
  - [Example Implementation](#example-implementation)
  - [Testing Your Strategy](#testing-your-strategy)
  - [Troubleshooting](#troubleshooting)
    - [Common Issues](#common-issues)
    - [Getting Help](#getting-help)

## Overview

The Trading Strategy Backtester application uses a registry-based strategy system that allows you to add new trading strategies without modifying the core application. Each strategy is automatically discovered and made available in the UI.

Strategies must:
1. Inherit from the `AbstractStrategy` class
2. Be decorated with `@register_strategy`
3. Implement all required methods

## Strategy Architecture

The strategy system consists of these key components:

- **AbstractStrategy**: Abstract base class that all strategies must inherit from
- **Strategy Registry**: Manages strategy registration and discovery
- **Strategy Implementations**: Concrete strategies (e.g., SMAStrategy, RSIStrategy, etc.)

### Directory Structure

```
strategies/
├── __init__.py                      # (No manual import required)
├── base/                            # Base strategy components
│   ├── __init__.py
│   ├── abstract_strategy.py         # Abstract base class (AbstractStrategy)
│   └── strategy_registry.py         # Registry system
└── implementations/                 # Strategy implementations
    ├── __init__.py
    ├── sma_strategy.py              # SMA Crossover strategy implementation
    ├── rsi_strategy.py              # RSI strategy implementation
    ├── bb_strategy.py               # Bollinger Bands strategy
    ├── ema_rsi_strategy.py          # EMA + RSI strategy
    └── your_strategy.py             # Your new strategy
```

## Step-by-Step Implementation Guide

### 1. Create a New Strategy File

Create a new Python file in the `strategies/implementations/` directory with a descriptive name:

```bash
touch strategies/implementations/macd_strategy.py  # Replace with your strategy name
```

### 2. Import Required Modules

```python
"""
MACD Strategy (Moving Average Convergence Divergence).
"""

from typing import Dict, Any, Tuple, List
import pandas as pd
import numpy as np
from strategies.base.abstract_strategy import AbstractStrategy
from strategies.base.strategy_registry import register_strategy
```

### 3. Define Your Strategy Class

```python
@register_strategy
class MACDStrategy(AbstractStrategy):
    """
    Strategy based on the MACD (Moving Average Convergence Divergence) indicator.

    Buy signal: When MACD crosses above signal line
    Sell signal: When MACD crosses below signal line
    """

    def __init__(self, 
                 fast_period: int = 12, 
                 slow_period: int = 26, 
                 signal_period: int = 9,
                 **kwargs):
        """
        Initialize the MACD strategy.

        Args:
            fast_period: Period for fast EMA
            slow_period: Period for slow EMA
            signal_period: Period for signal line
            **kwargs: Additional parameters
        """
        parameters = {
            'fast_period': fast_period,
            'slow_period': slow_period,
            'signal_period': signal_period,
            **kwargs
        }

        # NOTE: Notice the use of get_label() class method 
        #       to name the strategy in order to ensure consistency.
        super().__init__(self.get_label(), parameters)

        # Parameter validation
        if fast_period >= slow_period:
            raise ValueError("Fast period must be less than slow period")
        if fast_period < 1 or slow_period < 1 or signal_period < 1:
            raise ValueError("Periods must be positive")
```

### 4. Implement Instance Methods

```python
def generate_signals(self, data: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    """
    Generate buy and sell signals based on MACD.

    Args:
        data: DataFrame with OHLCV data

    Returns:
        Tuple containing entry and exit signals
    """
    if not self.validate_data(data):
        raise ValueError("Invalid data: OHLCV columns required")

    fast = self.parameters['fast_period']
    slow = self.parameters['slow_period']
    signal = self.parameters['signal_period']

    # Calculate MACD
    fast_ema = data['Close'].ewm(span=fast, adjust=False).mean()
    slow_ema = data['Close'].ewm(span=slow, adjust=False).mean()
    macd = fast_ema - slow_ema
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    macd_histogram = macd - macd_signal

    # Buy when MACD crosses above signal line
    buy_signals = (macd > macd_signal) & (macd.shift(1) <= macd_signal.shift(1))
    # Sell when MACD crosses below signal line
    sell_signals = (macd < macd_signal) & (macd.shift(1) >= macd_signal.shift(1))

    # Store indicators for charting
    self.indicators = {
        'macd': macd,
        'signal': macd_signal,
        'histogram': macd_histogram
    }

    return buy_signals, sell_signals

def get_explanation(self) -> str:
    """
    Return an explanation of the strategy.

    Returns:
        Description of the MACD strategy
    """
    fast = self.parameters['fast_period']
    slow = self.parameters['slow_period']
    signal = self.parameters['signal_period']
    return (f"{self.get_label()} with parameters: Fast={fast}, Slow={slow}, Signal={signal}.\n"
            f"Buy when {self.get_abbreviated_name()} crosses above signal line, " 
            f"sell when {self.get_abbreviated_name()} crosses below signal line.")
```

### 5. Implement Parameter Definitions Method

```python
@classmethod
def get_parameter_definitions(cls) -> Dict[str, Dict[str, Any]]:
    """
    Define parameters for this strategy with constraints.

    Returns:
        Dictionary of parameter definitions
    """
    return {
        'fast_period': {
            'type': int,
            'default': 12,
            'range': (5, 30),
            'description': 'Period for fast EMA'
        },
        'slow_period': {
            'type': int,
            'default': 26,
            'range': (15, 50),
            'description': 'Period for slow EMA'
        },
        'signal_period': {
            'type': int,
            'default': 9,
            'range': (5, 20),
            'description': 'Period for signal line'
        }
    }
```

### 6. Implement Label, Abbreviated Name and Parameter Summary Methods

```python
@classmethod
def get_label(cls) -> str:
    return "Moving Average Convergence Divergence"

@classmethod
def get_abbreviated_name(cls) -> str:
    return "MACD"

@classmethod
def get_parameter_summary(cls, config: Dict[str, Any] = None) -> str:
    if config and 'fast_period' in config and 'slow_period' in config and 'signal_period' in config:
        return f"{cls.get_abbreviated_name()} {config['fast_period']}/{config['slow_period']}/{config['signal_period']}"
    return cls.get_abbreviated_name()
```

### 7. Implement Predefined Configurations

If this method is not defined, parameter variations will be automatically generated as a configuration set (see `abstract_strategy.py`)

```python
@classmethod
def get_comparison_parameter_sets(cls) -> List[Dict[str, Any]]:
    return [
        {'fast_period': 12, 'slow_period': 26, 'signal_period': 9},  # Standard
        {'fast_period': 8, 'slow_period': 17, 'signal_period': 9},   # Faster
        {'fast_period': 16, 'slow_period': 35, 'signal_period': 9},  # Slower
        {'fast_period': 12, 'slow_period': 26, 'signal_period': 5},  # Faster signal
        {'fast_period': 12, 'slow_period': 26, 'signal_period': 14}  # Slower signal
    ]
```

### 8. (Optional) Implement Additional Methods

```python
def get_indicators(self) -> Dict[str, pd.Series]:
    """
    Return the calculated indicators for charting.
    """
    return getattr(self, 'indicators', {})
```

---

## Required Methods

| Method | Description | Return Type |
|--------|-------------|-------------|
| `get_label` *(class method)* | Strategy label | `str` |
| `get_abbreviated_name` *(class method)* | Strategy short label | `str` |
| `get_parameter_summary` *(class method)* | Short description for UI | `str` |
| `get_parameter_definitions` *(class method)* | Define strategy parameters | `Dict[str, Dict[str, Any]]` |
| `get_comparison_parameter_sets` *(class method)* | Default parameter sets for strategy configuration comparison | `List[Dict[str, Any]]` |
| `__init__` | Instantiate strategy with parameters | `None` |
| `generate_signals` | Create buy/sell signals from OHLCV data set | `Tuple[pd.Series, pd.Series]` |
| `get_explanation` | Explanation of the strategy | `str` |

## Optional Methods

| Method | Description | Return Type |
|--------|-------------|-------------|
| `get_indicators` | Return calculated indicators | `Dict[str, pd.Series]` |
| `validate_data` | Validate input data | `bool` |

---

## Strategy Registration

The `@register_strategy` decorator automatically registers your strategy with the system. 
No manual import or export in `__init__.py` is required. 

As long as your class:
1. Inherits from `AbstractStrategy`
2. Is decorated with `@register_strategy`

it will be discovered and available in the application menu.

---

## Parameter Definition Best Practices

Parameter definitions should include:

```python
{
    'parameter_name': {
        'type': type,           # Python type (int, float, str, bool)
        'default': value,       # Default value
        'range': (min, max),    # Optional range for numeric parameters
        'description': 'text'   # Human-readable description
    },
    # etc...
}
```

Example:
```python
{
    'rsi_period': {
        'type': int,
        'default': 14,
        'range': (2, 50),
        'description': 'Period for RSI calculation'
    }
    # etc...
}
```

---

## Example Implementation

Here's a complete example of a Bollinger Bands strategy (matches the current codebase):

```python
"""
Bollinger Bands Strategy.
"""

from typing import Dict, Any, Tuple, List
import pandas as pd
import numpy as np
from strategies.base.abstract_strategy import AbstractStrategy
from strategies.base.strategy_registry import register_strategy

@register_strategy
class BBStrategy(AbstractStrategy):
    """
    Strategy based on Bollinger Bands.

    Buy signal: Price crosses below lower band
    Sell signal: Price crosses above upper band
    """

    @classmethod
    def get_label(cls) -> str:
        return "Bollinger Bands"

    @classmethod
    def get_abbreviated_name(cls) -> str:
        return "BB"

    @classmethod
    def get_parameter_definitions(cls) -> Dict[str, Dict[str, Any]]:
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

    @classmethod
    def get_comparison_parameter_sets(cls) -> List[Dict[str, Any]]:
        return [
            {'period': 20, 'std_dev': 2.0},  # Standard
            {'period': 20, 'std_dev': 1.5},  # Tighter bands
            {'period': 20, 'std_dev': 2.5},  # Wider bands
            {'period': 10, 'std_dev': 2.0},  # Shorter period
            {'period': 50, 'std_dev': 2.0}   # Longer period
        ]

    @classmethod
    def get_parameter_summary(cls, config: Dict[str, Any] = None) -> str:
        if config and 'period' in config and 'std_dev' in config:
            return f"{cls.get_abbreviated_name()} {config['period']}/{config['std_dev']:.2f}"
        return cls.get_abbreviated_name()

    def __init__(self, 
                 period: int = 20, 
                 std_dev: float = 2.0,
                 **kwargs):
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
        if not self.validate_data(data):
            raise ValueError("Invalid data: OHLCV columns required")
        period = self.parameters['period']
        std_dev = self.parameters['std_dev']
        middle_band = data['Close'].rolling(window=period).mean()
        std = data['Close'].rolling(window=period).std()
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)
        buy_signals = (data['Close'] < lower_band) & (data['Close'].shift(1) >= lower_band.shift(1))
        sell_signals = (data['Close'] > upper_band) & (data['Close'].shift(1) <= upper_band.shift(1))
        self.indicators = {
            'middle_band': middle_band,
            'upper_band': upper_band,
            'lower_band': lower_band
        }
        return buy_signals, sell_signals

    def get_explanation(self) -> str:
        period = self.parameters['period']
        std_dev = self.parameters['std_dev']
        return (
            f"{self.get_label()} with period={period} and std_dev={std_dev:.2f}.\n"
            f"Buy when price crosses below lower band, " 
            f"sell when price crosses above upper band."
        )

    def get_indicators(self) -> Dict[str, pd.Series]:
        return getattr(self, 'indicators', {})
```

---

## Testing Your Strategy

1. **Implement your strategy** following the guidelines above.
2. **Run the application** to test it:
   ```bash
   python main.py
   ```
3. **Select your strategy** from the menu.
4. **Backtest with various parameters** to validate its performance.
5. **Compare different configurations** to find optimal settings.

---

## Troubleshooting

### Common Issues

1. **Strategy not appearing in the menu**:
   - Check that it's decorated with `@register_strategy`
   - Verify the class inherits from `AbstractStrategy`
   - Ensure the file is in the `strategies/implementations/` directory

2. **Parameter validation errors**:
   - Ensure parameter definitions match the types expected
   - Check that ranges are valid for numeric parameters

3. **Import errors**:
   - Verify import paths use the new structure:
     ```python
     from strategies.base.abstract_strategy import AbstractStrategy
     from strategies.base.strategy_registry import register_strategy
     ```

4. **Method name errors**:
   - Use the new method names:
     - `get_abbreviated_name()` (not `get_short_label()`)
     - `get_parameter_summary()` (not `get_short_description()`)
     - `get_predefined_configurations()` (not `get_comparison_parameter_sets()`)

5. **Charting issues**:
   - Make sure your `indicators` dictionary contains valid Series objects
   - Verify all Series have the same index as the input data

6. **Performance problems**:
   - Use vectorized operations (avoid loops)
   - Leverage pandas and numpy for calculations
   - Profile your code to identify bottlenecks

### Getting Help

If you need additional help implementing a strategy, consult:
- The existing strategy implementations in [`strategies/implementations/`](strategies/implementations/) for examples
- The `AbstractStrategy` class in [`strategies/base/abstract_strategy.py`](strategies/base/abstract_strategy.py) for interface requirements
- The `strategy_registry.py` in [`strategies/base/strategy_registry.py`](strategies/base/strategy_registry.py) for registration details
- The [`TECHNICAL_DOCUMENTATION.md`](TECHNICAL_DOCUMENTATION.md) for architectural details
