# Daily Scalper - Technical Documentation

## Project Architecture

### Overview
Daily Scalper is a modular Python application designed to test and evaluate cryptocurrency trading strategies. The architecture follows SOLID principles and uses an object-oriented approach to maximize reusability and maintainability.

### Module Structure

```
daily-scalper/
├── strategies/                # Trading strategies
│   ├── __init__.py
│   ├── base_strategy.py       # Base abstract class
│   └── sma_crossover.py       # Example: SMA Crossover
├── backtest/                  # Backtest engine
│   ├── __init__.py
│   ├── backtest_engine.py     # Main engine with vectorbt
│   └── performance_metrics.py # Metrics calculation
├── utils/                     # Utilities
│   ├── __init__.py
│   ├── data_loader.py         # Data loading (yfinance)
│   ├── visualizer.py          # Interactive charts (plotly)
│   └── strategy_saver.py      # Strategy saving
├── data/                      # Data cache
├── results/                   # Saved results
│   ├── strategies/            # Strategies in JSON/PKL format
│   ├── reports/               # Text reports
│   └── charts/                # HTML charts
├── main.py                    # Main application
├── test_setup.py              # Validation tests
├── start.sh                   # Startup script
└── config.py                  # Global configuration
```

## Main Components

### 1. Strategies (`strategies/`)

#### BaseStrategy (Abstract Class)
- **Role**: Defines the common interface for all strategies
- **Key methods**:
  - `generate_signals()`: Generates buy/sell signals
  - `validate_data()`: Validates input data
  - `get_description()`: Strategy description
  - `to_dict()`: Serialization for saving

#### SMACrossoverStrategy
- **Role**: Example strategy implementation
- **Logic**: Simple moving average crossover
- **Parameters**: `short_window`, `long_window`
- **Signals**:
  - Buy: Short SMA > Long SMA
  - Sell: Short SMA < Long SMA

### 2. Backtest Engine (`backtest/`)

#### BacktestEngine
- **Role**: Executes backtests with vectorbt
- **Features**:
  - Trading simulation with commissions/slippage
  - Automatic calculation of basic metrics
  - Error handling and data validation
- **Configuration**:
  - Initial capital: $10,000 (default)
  - Commission: 0.1% per transaction
  - Slippage: 0.01% per transaction

#### PerformanceMetrics
- **Role**: Calculation and analysis of advanced metrics
- **Calculated metrics**:
  - **Return**: Total return, Alpha vs Buy & Hold
  - **Risk**: Sharpe ratio, Volatility, Max Drawdown, VaR 95%
  - **Trading**: Win rate, Profit factor, Number of trades
  - **Advanced**: Calmar ratio, Sortino ratio

### 3. Utilities (`utils/`)

#### DataLoader
- **Role**: Retrieval and management of market data
- **Sources**: yfinance (Yahoo Finance)
- **Features**:
  - Automatic data caching
  - Data validation and cleaning
  - Support for multiple cryptocurrencies
  - Network error handling

#### Visualizer
- **Role**: Creation of interactive charts
- **Technologies**: Plotly for interactivity
- **Chart types**:
  - Candlestick with buy/sell signals
  - Portfolio evolution
  - Performance metrics (radar chart)
  - Drawdown analysis

#### StrategySaver
- **Role**: Persistence of strategies and results
- **Save formats**:
  - JSON: Metadata and parameters
  - Pickle: Complete data (portfolio, signals)
  - HTML: Interactive charts
  - TXT: Formatted reports

## Execution Flow

### 1. Data Loading
```python
# DataLoader retrieves data via yfinance
data = loader.load_crypto_data("BTC-USD", period="1y")  # 1y = 1 year
# Automatic validation and local cache
```

### 2. Strategy Initialization
```python
# Create a strategy with parameters
strategy = SMACrossoverStrategy(short_window=20, long_window=50)
# Parameter validation
```

### 3. Signal Generation
```python
# The strategy analyzes data and generates signals
buy_signals, sell_signals = strategy.generate_signals(data)
# Boolean signals indexed by date
```

### 4. Backtest Execution
```python
# BacktestEngine uses vectorbt for simulation
results = engine.run_backtest(strategy, data)
# Automatic metric calculation
```

### 5. Analysis and Visualization
```python
# Calculate advanced metrics
metrics = PerformanceMetrics.calculate_advanced_metrics(results)
# Generate interactive charts
Visualizer.show_all_plots(results)
```

### 6. Saving (Optional)
```python
# Save if the strategy is profitable
if PerformanceMetrics.is_strategy_profitable(metrics):
    saver.save_strategy_results(results)
```

## Profitability Criteria

A strategy is considered profitable if it meets **all** of the following criteria:

- **Minimum return**: 10% (`min_return = 0.1`)
- **Minimum Sharpe ratio**: 1.0 (`min_sharpe = 1.0`)
- **Maximum drawdown**: 20% (`max_drawdown = 0.2`)
- **Minimum number of trades**: 5 (`min_trades = 5`)

These criteria can be adjusted in `config.py`.

## System Extension

### Creating a New Strategy

1. **Inherit from BaseStrategy**:
```python
from strategies.base_strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    def __init__(self, param1, param2):
        super().__init__("My Strategy", {
            'param1': param1,
            'param2': param2
        })
```

2. **Implement required methods**:
```python
def generate_signals(self, data):
    # Your logic here
    buy_signals = ...
    sell_signals = ...
    return buy_signals, sell_signals

def get_description(self):
    return "Description of my strategy"
```

3. **Add to initialization**:
```python
# In strategies/__init__.py
from .my_strategy import MyStrategy
__all__ = ['BaseStrategy', 'SMACrossoverStrategy', 'MyStrategy']
```

### Adding New Metrics

1. **Extend PerformanceMetrics**:
```python
@staticmethod
def calculate_custom_metric(results):
    # Your custom calculation
    return custom_value
```

2. **Integrate into main calculation**:
```python
# In calculate_advanced_metrics()
metrics['custom_metric'] = calculate_custom_metric(results)
```

## Advanced Configuration

### Backtest Parameters
```python
# In config.py
DEFAULT_BACKTEST_CONFIG = {
    'initial_cash': 10000.0,    # Initial capital
    'commission': 0.001,        # 0.1% commission
    'slippage': 0.0001,         # 0.01% slippage
}
```

### Profitability Criteria
```python
PROFITABILITY_CRITERIA = {
    'min_return': 0.1,      # 10% minimum
    'min_sharpe': 1.0,      # Minimum Sharpe ratio
    'max_drawdown': 0.2,    # 20% maximum
    'min_trades': 5,        # Minimum number of trades
}
```

### Supported Symbols
```python
POPULAR_CRYPTO_SYMBOLS = [
    "BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "ADA-USD",
    # ... other cryptocurrencies
]
```

## Troubleshooting

### Common Issues

1. **Module import error**:
   - Check that the virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

2. **Missing data**:
   - Check internet connection
   - Delete cache: `rm -rf data/*.csv`

3. **Vectorbt calculation errors**:
   - Check that data has enough points (>100)
   - Ensure signals are not all empty

4. **Charts not displaying**:
   - Check that plotly is installed
   - Manually open HTML files in `results/charts/`

### Logs and Debug

To enable debug mode, modify the logging level in `main.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance and Optimization

### Data Cache
- Data is automatically cached in `data/`
- Cache valid for 24h by default
- Delete cache to force reload

### Backtest Optimization
- Use shorter periods for quick tests
- Vectorbt automatically optimizes calculations
- Avoid strategies with too many signals (>1000 trades)

### Memory
- Complete results are stored in memory
- For large datasets, consider incremental saving
- Limit the number of strategies compared simultaneously

## Security and Best Practices

### Data Management
- Never commit cache files (`data/`)
- API keys (if added) should be in environment variables
- Regularly save important results

### Code Quality
- Follow PEP 8 conventions
- Add docstrings for new functions
- Test new strategies with `test_setup.py`

### Limitations
- **No real-time trading**: Backtesting only
- **Limited data**: Dependent on yfinance
- **No automatic optimization**: Parameters must be adjusted manually