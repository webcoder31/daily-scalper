# Daily Scalper - Crypto Trading Strategy Tester

Modular Python application for testing, evaluating, and saving cryptocurrency trading strategies using vectorbt.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Available Strategies](#available-strategies)
- [Backtest Configuration](#backtest-configuration)
- [Usage Examples](#usage-examples)
- [Results and Visualization](#results-and-visualization)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### 1. Clone the project
```bash
git clone <your-repo-url>
cd daily-scalper
```

### 2. Create a virtual environment (recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Test the installation
```bash
python test_setup.py
```

If all tests pass, your installation is ready! 🎉

## ⚙️ Configuration

### Default configuration

The `config.py` file contains all default configurations:

```python
# Backtest configuration
DEFAULT_BACKTEST_CONFIG = {
    'initial_cash': 10000.0,     # Initial capital in USD
    'commission': 0.001,         # Commission (0.1%)
    'slippage': 0.0001,          # Slippage (0.01%)
}

# Data configuration
DEFAULT_DATA_CONFIG = {
    'default_symbol': 'BTC-USD', # Default symbol
    'default_period': '1y',      # Default period (1 year)
    'cache_enabled': True,       # Data cache enabled
    'cache_max_age_hours': 24,   # Cache duration (24h)
}
```

### Supported symbols

The application supports all crypto symbols available on Yahoo Finance:
- **Bitcoin**: BTC-USD
- **Ethereum**: ETH-USD
- **Binance Coin**: BNB-USD
- **XRP**: XRP-USD
- **Cardano**: ADA-USD
- **Solana**: SOL-USD
- And many others...

## Usage

### Quick start

```bash
# Activate the virtual environment
source venv/bin/activate

# Launch the application
python main.py
```

### Interactive interface

The application offers an interactive menu with the following options:

1. **Test a strategy** - Run a backtest on a strategy
2. **Compare strategies** - Compare multiple strategies
3. **View saved results** - View previous results
4. **Configuration** - Modify parameters
5. **Exit** - Close the application

## Available Strategies

### 1. SMA Crossover (Simple Moving Average Crossover)
**File**: `strategies/sma_crossover.py`

**Description**: Strategy based on the crossing of two simple moving averages.

**Parameters**:
- `short_window`: Period for the short moving average (default: 10)
- `long_window`: Period for the long moving average (default: 20)

**Signals**:
- **Buy**: When the short average crosses above the long average
- **Sell**: When the short average crosses below the long average

### 2. RSI Strategy (Relative Strength Index)
**File**: `strategies/rsi_strategy.py`

**Description**: Strategy based on the RSI indicator to identify overbought/oversold zones.

**Parameters**:
- `rsi_period`: RSI calculation period (default: 14)
- `oversold_threshold`: Oversold threshold (default: 30)
- `overbought_threshold`: Overbought threshold (default: 70)

**Signals**:
- **Buy**: When RSI exits the oversold zone (< 30)
- **Sell**: When RSI enters the overbought zone (> 70)

## 🔧 Backtest Configuration

### Basic parameters

```python
backtest_config = {
    'initial_cash': 10000.0,    # Starting capital
    'commission': 0.001,        # Transaction fees (0.1%)
    'slippage': 0.0001,         # Price slippage (0.01%)
}
```

### Profitability criteria

```python
PROFITABILITY_CRITERIA = {
    'min_return': 0.1,          # Minimum return (10%)
    'min_sharpe': 1.0,          # Minimum Sharpe ratio
    'max_drawdown': 0.2,        # Maximum drawdown (20%)
    'min_trades': 5,            # Minimum number of trades
}
```

### Data periods

You can use different periods for your backtests:

- `'1d'` - 1 day
- `'5d'` - 5 days
- `'1mo'` - 1 month
- `'3mo'` - 3 months
- `'6mo'` - 6 months
- `'1y'` - 1 year (default)
- `'2y'` - 2 years
- `'5y'` - 5 years
- `'max'` - Maximum available

## Usage Examples

### Example 1: Simple backtest with SMA Crossover

```python
from strategies import SMACrossoverStrategy
from backtest import BacktestEngine
from utils import DataLoader

# 1. Load data
loader = DataLoader()
data = loader.get_data('BTC-USD', period='1y')  # 1y = 1 year

# 2. Create the strategy
strategy = SMACrossoverStrategy(short_window=10, long_window=20)

# 3. Configure the backtest
engine = BacktestEngine(initial_cash=10000, commission=0.001)

# 4. Execute the backtest
results = engine.run_backtest(strategy, data)

# 5. Display results
print(f"Total return: {results['metrics']['total_return']:.2%}")
print(f"Sharpe ratio: {results['metrics']['sharpe_ratio']:.2f}")
```

### Example 2: Compare multiple strategies

```python
from strategies import SMACrossoverStrategy, RSIStrategy
from backtest import BacktestEngine
from utils import DataLoader, Visualizer

# Load data
loader = DataLoader()
data = loader.get_data('ETH-USD', period='6mo')  # 6mo = 6 months

# Create strategies
sma_strategy = SMACrossoverStrategy(short_window=5, long_window=15)
rsi_strategy = RSIStrategy(rsi_period=14, oversold_threshold=30)

# Backtest strategies
engine = BacktestEngine(initial_cash=10000)
sma_results = engine.run_backtest(sma_strategy, data)
rsi_results = engine.run_backtest(rsi_strategy, data)

# Compare results
print("SMA Strategy:")
print(f"  Return: {sma_results['metrics']['total_return']:.2%}")
print(f"  Sharpe: {sma_results['metrics']['sharpe_ratio']:.2f}")

print("RSI Strategy:")
print(f"  Return: {rsi_results['metrics']['total_return']:.2%}")
print(f"  Sharpe: {rsi_results['metrics']['sharpe_ratio']:.2f}")
```

### Example 3: Parameter optimization

```python
from strategies import SMACrossoverStrategy
from backtest import BacktestEngine
from utils import DataLoader

loader = DataLoader()
data = loader.get_data('BTC-USD', period='1y')  # 1y = 1 year
engine = BacktestEngine(initial_cash=10000)

best_return = 0
best_params = None

# Test different parameters
for short in range(5, 20, 5):
    for long in range(20, 50, 10):
        strategy = SMACrossoverStrategy(short_window=short, long_window=long)
        results = engine.run_backtest(strategy, data)
        
        if results['metrics']['total_return'] > best_return:
            best_return = results['metrics']['total_return']
            best_params = (short, long)

print(f"Best parameters: short={best_params[0]}, long={best_params[1]}")
print(f"Return: {best_return:.2%}")
```

## Results and Visualization

### Calculated metrics

Each backtest generates the following metrics:

- **Total return** (`total_return`): Overall performance
- **Annualized return** (`annualized_return`): Annual performance
- **Volatility** (`volatility`): Strategy risk
- **Sharpe ratio** (`sharpe_ratio`): Risk-adjusted return
- **Maximum drawdown** (`max_drawdown`): Maximum loss
- **Number of trades** (`total_trades`): Trading frequency
- **Win rate** (`win_rate`): Percentage of winning trades

### Available visualizations

1. **Price chart** with buy/sell signals
2. **Portfolio evolution** vs Buy & Hold
3. **Drawdown curve**
4. **Return distribution**
5. **Technical indicators** used by the strategy

### Saving results

Results are automatically saved in the `results/` folder:

```
results/
├── strategies/              # Saved strategies
├── backtests/               # Backtest results
└── visualizations/          # Generated charts
```

## 🛠️ Troubleshooting

### Common problems

#### 1. Dependency installation error
```bash
# Solution: Update pip
pip install --upgrade pip
pip install -r requirements.txt
```

#### 2. Data download error
```bash
# Check internet connection and symbol
# Example: 'BTCUSD' doesn't exist, use 'BTC-USD'
```

#### 3. "Module not found" error
```bash
# Check that the virtual environment is activated
source venv/bin/activate
python test_setup.py
```

#### 4. Slow performance
- Reduce the data period (`period='3mo'` (3 months) instead of `period='5y'` (5 years))
- Enable cache in configuration
- Use less complex strategy parameters

### Logs and debugging

To enable detailed logs, modify the logging level in your script:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Support

If you encounter problems:

1. Check that all tests pass: `python test_setup.py`
2. Check error logs
3. Check your internet connection for data download
4. Make sure you're using Python 3.8+

## Project Structure

```
daily-scalper/
├── data/                        # Market data and cache
│   └── cache/                   # Downloaded data cache
├── strategies/                  # Trading strategy modules
│   ├── __init__.py              # Strategy exports
│   ├── base_strategy.py         # Base class for strategies
│   ├── sma_crossover.py         # SMA Crossover strategy
│   └── rsi_strategy.py          # RSI Strategy
├── backtest/                    # Backtest engine
│   ├── __init__.py              # Engine exports
│   ├── engine.py                # Main backtest engine
│   └── metrics.py               # Performance metrics calculation
├── utils/                       # Utilities and helpers
│   ├── __init__.py              # Utility exports
│   ├── data_loader.py           # Market data loading
│   ├── visualizer.py            # Chart generation
│   └── strategy_saver.py        # Strategy saving
├── results/                     # Results and saves
│   ├── strategies/              # Saved strategies
│   ├── backtests/               # Backtest results
│   └── visualizations/          # Generated charts
├── main.py                      # Main script with interface
├── config.py                    # Global configuration
├── requirements.txt             # Python dependencies
├── test_setup.py                # Validation tests
└── README.md                    # This documentation
```

## Features

- **Modular strategies** with parameters
- **Vectorized backtest** with vectorbt for optimal performance
- **Interactive visualization** of results with Plotly
- **Automatic saving** of performant strategies
- **Automatic data retrieval** via yfinance
- **Intelligent cache** to avoid repeated downloads
- **Complete metrics** for performance and risk
- **User interface** simple and intuitive
- **Automated tests** to validate installation

## License

This project is under MIT license. See the LICENSE file for more details.

---

**Happy Trading!**