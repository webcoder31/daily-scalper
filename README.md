# Trading Strategy Backtester

A user-friendly Python application for testing, evaluating, 
and saving cryptocurrency trading strategies.

---

## Overview

Trading Strategy Backtester lets you backtest and compare crypto trading strategies 
with an interactive menu and clear visualizations. No coding required for basic use.

---

## Features

- Test built-in trading strategies on historical crypto data
- Compare strategy performance with multiple configurations
- Interactive charts and comprehensive performance metrics
- Automatic saving of profitable strategies
- Simple, menu-driven interface
- Flexible logging control with multiple output options
- Professional modular architecture with clear separation of concerns

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. **Clone the project**
   ```bash
   git clone <your-repo-url>
   cd trading-strategy-backtester
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Test the installation**
   ```bash
   python test_setup.py
   ```
   If all tests pass, you're ready to go!

---

## Usage

### Quick Start

```bash
source venv/bin/activate
python main.py
```

### Logging Options

Trading Strategy Backtester provides flexible logging control through command-line options:

```bash
# Default: Minimal logging (WARNING and ERROR only)
python main.py

# Verbose logging with detailed operation information
python main.py --verbose

# Debug logging with full debugging information
python main.py --log-level DEBUG

# Quiet mode with no logging output
python main.py --quiet

# Save logs to file in addition to console output
python main.py --log-file

# Log exclusively to file without console output
python main.py --file-only
```

### Application Architecture

- The entrypoint is [`main.py`](main.py), which launches the interactive CLI.
- The CLI/menu logic is in [`core/interactive_cli.py`](core/interactive_cli.py).
- The core application logic is in [`core/strategy_backtester.py`](core/strategy_backtester.py).

### Menu Options

1. Test a single strategy configuration
2. Compare different strategy configurations
3. View saved profitable strategies
4. View application settings
5. Exit application

### Available Strategies

- **Simple Moving Average Crossover (SMA)**
- **Relative Strength Index (RSI) Threshold**
- **Bollinger Bands**
- **EMA + RSI Combined Strategy**

Each strategy can be customized via the menu with various parameter configurations.

---

## Project Structure

The application follows a professional modular architecture:

```
trading-strategy-backtester/
├── main.py                               # Entry point
├── config.py                             # Global configuration
├── functional_test.py                    # Functional testing
├── test_setup.py                         # Setup validation
├── validation_test.py                    # Comprehensive validation
├── backtesting/                          # Backtesting engine and analysis
│   ├── __init__.py
│   ├── backtest_engine.py                # Backtesting execution
│   └── performance_analyzer.py           # Performance analysis and metrics
├── cache/                                # Cached market data (created at runtime)
├── core/                                 # Core application logic
│   ├── __init__.py
│   ├── interactive_cli.py                # CLI and menu system
│   └── strategy_backtester.py            # Main application controller
├── market_data/                          # Market data management
│   ├── __init__.py
│   ├── market_data_provider.py           # Data fetching and caching
│   └── period_translator.py              # Period string conversions
├── persistence/                          # Data persistence
│   ├── __init__.py
│   └── strategy_archiver.py              # Strategy results management
├── results/                              # Output directory (created at runtime)
│   ├── charts/                           # Generated charts (created at runtime)
│   ├── reports/                          # Performance reports (created at runtime)
│   └── strategies/                       # Saved strategy results (created at runtime)
├── strategies/                           # Trading strategies
│   ├── __init__.py
│   ├── base/                             # Fundation for strategy implementation
|   │   ├── __init__.py
│   │   ├── abstract_strategy.py          # Abstract strategy class
│   │   └── strategy_registry.py          # Strategy registration system
│   └── implementations/                  # Strategy implementations
|       ├── __init__.py
│       ├── bb_strategy.py                # Bollinger Bands strategy
│       ├── ema_rsi_strategy.py           # EMA + RSI strategy
│       ├── rsi_strategy.py               # RSI strategy
│       └── sma_strategy.py               # SMA Crossover strategy
├── ui/                                   # User interface components
│   ├── __init__.py
│   ├── components.py                     # UI components and menus
│   └── theme.py                          # Theme and styling
├── logging/                              # Application logging
│   ├── __init__.py
│   └── logging_manager.py                # Logging configuration manager
└── charting/                             # Chart generation
    ├── __init__.py
    └── backtest_chart_builder.py         # Interactive chart builder
```

---

## Core Components

### TradingStrategyBacktester (Main Application Controller)
The main application controller that orchestrates backtesting operations:
- `execute_strategy_backtest()` - Execute single strategy backtest
- `analyze_strategy_variants()` - Compare multiple strategy configurations
- `display_saved_results()` - Show previously saved profitable strategies

### MarketDataProvider
Handles cryptocurrency data fetching and caching:
- `fetch_cryptocurrency_data()` - Load market data from Yahoo Finance
- `get_supported_cryptocurrency_symbols()` - Get available trading pairs
- `is_cached_data_fresh()` - Check cache validity

### BacktestEngine
Executes vectorized backtests using vectorbt:
- `execute_strategy_evaluation()` - Run strategy backtest simulation
- `build_vectorbt_portfolio()` - Construct trading portfolio
- `compute_performance_statistics()` - Calculate basic metrics

### PerformanceAnalyzer
Calculates comprehensive performance metrics:
- `compute_extended_performance_stats()` - Advanced metrics calculation
- `meets_profitability_criteria()` - Evaluate strategy profitability
- `sort_strategies_by_performance()` - Rank strategy performance
- `create_detailed_analysis_report()` - Generate performance reports

### BacktestChartBuilder
Creates interactive visualizations:
- `create_backtest_charts()` - Create strategy performance charts
- `display_charts()` - Show comprehensive chart suite

### StrategyArchiver
Manages strategy result storage:
- `persist_strategy_results()` - Save profitable strategies
- `retrieve_strategy_results()` - Load saved strategies
- `list_persisted_strategies()` - Display saved strategy list

---

## Configuration

All settings (default capital, commission, cache, etc.) can be changed in [`config.py`](config.py).  
To modify: edit the file and restart the app.

Key configuration sections:
- `DEFAULT_BACKTEST_CONFIG`: Initial cash, commission, slippage settings
- `DEFAULT_DATA_CONFIG`: Default symbol, period, cache settings
- `PROFITABILITY_CRITERIA`: Minimum return, Sharpe ratio, drawdown thresholds
- `POPULAR_CRYPTO_SYMBOLS`: List of supported cryptocurrency symbols

---

## Results & Visualizations

- Results and charts are saved in the `results/` directory.
- Interactive charts open in your browser.
- Profitable strategies are saved automatically based on configurable criteria.
- Charts include buy/sell signals, performance metrics, and technical indicators.

---

## Troubleshooting

- **Dependency error:**  
  Update pip and reinstall requirements:
  ```bash
  pip install --upgrade pip
  pip install -r requirements.txt
  ```

- **Data download error:**  
  Check your internet connection and use correct symbol format (e.g., 'BTC-USD').

- **"Module not found" error:**  
  Ensure your virtual environment is activated.

- **Slow performance:**  
  Use a shorter data period or enable cache.

- **Logging issues:**
  Use `--quiet` for no logging or `--verbose` for detailed output.

---

## More Information

For technical details, developer documentation, and instructions on adding new strategies, see:
- [`TECHNICAL_DOCUMENTATION.md`](TECHNICAL_DOCUMENTATION.md) - Technical architecture and development guide
- [`STRATEGY_IMPLEMENTATION_GUIDE.md`](STRATEGY_IMPLEMENTATION_GUIDE.md) - Step-by-step strategy creation guide

---

## License

MIT License. See LICENSE file for details.
