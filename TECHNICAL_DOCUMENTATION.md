# Trading Strategy Backtester - Technical Documentation

## Purpose

This document is for developers and contributors. It covers the internal architecture, code structure, extension points, and best practices for maintaining and extending Trading Strategy Backtester.

For installation and user instructions, see [`README.md`](README.md).

---

## Architecture Overview

Trading Strategy Backtester is a modular, object-oriented Python application for backtesting and analyzing cryptocurrency trading strategies. It follows professional software engineering principles with clear separation of concerns, comprehensive type annotations, and robust error handling.

### Core Design Principles

- **Modular Architecture**: Clear separation between core logic, strategies, data management, and UI
- **Professional Naming**: Semantic class and method names that clearly indicate functionality
- **Type Safety**: Comprehensive type annotations throughout the codebase
- **Error Handling**: Custom exception classes and robust error management
- **Extensibility**: Easy addition of new strategies through registry system
- **Performance**: Vectorized operations using vectorbt for fast backtesting

---

## Project Structure

```
daily-scalper/
├── main.py                               # Entry point
├── config.py                             # Global configuration
├── core/                                 # Core application logic
│   ├── __init__.py
│   ├── trading_strategy_backtester.py    # Main application controller
│   └── command_line_interface.py         # CLI and menu system
├── strategies/                           # Trading strategies
│   ├── __init__.py
│   ├── base/                             # Base strategy components
│   │   ├── __init__.py
│   │   ├── abstract_trading_strategy.py  # Abstract base class
│   │   └── strategy_registry.py          # Strategy registration system
│   └── implementations/                  # Concrete strategy implementations
│       ├── __init__.py
│       ├── sma_strategy.py               # SMA Crossover strategy
│       ├── rsi_strategy.py               # RSI strategy
│       ├── bb_strategy.py                # Bollinger Bands strategy
│       └── ema_rsi_strategy.py           # EMA + RSI strategy
├── backtesting/                          # Backtesting engine and analysis
│   ├── __init__.py
│   ├── strategy_backtest_engine.py       # Backtesting execution
│   └── performance_analyzer.py           # Performance analysis and metrics
├── market_data/                          # Market data management
│   ├── __init__.py
│   ├── market_data_provider.py           # Data fetching and caching
│   └── period_translator.py              # Period string conversions
├── visualization/                        # Chart generation
│   ├── __init__.py
│   └── backtest_chart_generator.py       # Interactive visualizations
├── persistence/                          # Data persistence
│   ├── __init__.py
│   └── strategy_archiver.py              # Strategy results management
├── ui/                                   # User interface components
│   ├── __init__.py
│   ├── components.py                     # UI components and menus
│   └── theme.py                          # Theme and styling
├── utils/                                # General utilities
│   ├── __init__.py
│   └── logging_config.py                 # Centralized logging configuration
├── cache/                                # Cached market data (created at runtime)
└── results/                              # Output directory (created at runtime)
    ├── strategies/                       # Saved strategy results
    ├── reports/                          # Performance reports
    └── charts/                           # Generated charts
```

---

## Core Components

### TradingStrategyBacktester (Main Application Controller)

**Location**: [`core/trading_strategy_backtester.py`](core/trading_strategy_backtester.py)

The central orchestrator that coordinates all backtesting operations.

**Key Methods**:
- `execute_strategy_backtest()` - Execute single strategy backtest with comprehensive analysis
- `analyze_strategy_variants()` - Compare multiple strategy configurations and rank performance
- `display_saved_results()` - Show previously saved profitable strategies
- `render_backtest_summary()` - Generate formatted results display

**Dependencies**:
- `StrategyBacktestEngine` for backtest execution
- `PerformanceAnalyzer` for metrics calculation
- `MarketDataProvider` for data loading
- `BacktestChartGenerator` for visualization
- `StrategyArchiver` for result storage

### Strategy System

#### AbstractTradingStrategy (Abstract Base Class)

**Location**: [`strategies/base/abstract_trading_strategy.py`](strategies/base/abstract_trading_strategy.py)

Abstract base class that all trading strategies must inherit from.

**Key Methods**:
- `generate_signals()` - Generate buy/sell signals from OHLCV data
- `get_abbreviated_name()` - Short strategy identifier for UI
- `get_parameter_summary()` - Concise parameter description
- `get_predefined_configurations()` - Predefined configurations for comparison
- `get_parameter_definitions()` - Parameter constraints and types

#### Strategy Registry System

**Location**: [`strategies/base/strategy_registry.py`](strategies/base/strategy_registry.py)

Automatic strategy discovery and registration system using decorators.

**Usage**:
```python
from strategies.base.strategy_registry import register_strategy
from strategies.base.abstract_trading_strategy import AbstractTradingStrategy

@register_strategy
class MyStrategy(AbstractTradingStrategy):
    # Implementation here
```

#### Strategy Implementations

All concrete strategies are located in [`strategies/implementations/`](strategies/implementations/):

- **SMAStrategy**: Simple Moving Average crossover
- **RSIStrategy**: Relative Strength Index threshold
- **BBStrategy**: Bollinger Bands mean reversion
- **EmaRsiStrategy**: Combined EMA and RSI signals

### Backtesting Engine

#### StrategyBacktestEngine

**Location**: [`backtesting/strategy_backtest_engine.py`](backtesting/strategy_backtest_engine.py)

Executes vectorized backtests using vectorbt for high performance.

**Key Methods**:
- `execute_strategy_evaluation()` - Run complete strategy backtest
- `build_vectorbt_portfolio()` - Construct trading portfolio with signals
- `compute_performance_statistics()` - Calculate basic performance metrics
- `slice_data_by_date_range()` - Filter data by date range

**Features**:
- Vectorized operations for speed
- Commission and slippage modeling
- Comprehensive signal validation
- Portfolio construction with proper sizing

#### PerformanceAnalyzer

**Location**: [`backtesting/performance_analyzer.py`](backtesting/performance_analyzer.py)

Calculates comprehensive performance metrics and strategy evaluation.

**Key Methods**:
- `compute_extended_performance_stats()` - Advanced metrics calculation
- `meets_profitability_criteria()` - Evaluate strategy against profitability thresholds
- `sort_strategies_by_performance()` - Rank strategies by multiple criteria
- `create_detailed_analysis_report()` - Generate comprehensive performance reports

**Metrics Calculated**:
- Return, Sharpe ratio, Sortino ratio, Calmar ratio
- Maximum drawdown, volatility, skewness, kurtosis
- Win rate, profit factor, average trade metrics
- Value at Risk (VaR) calculations

### Data Management

#### MarketDataProvider

**Location**: [`market_data/market_data_provider.py`](market_data/market_data_provider.py)

Handles cryptocurrency data fetching, caching, and validation.

**Key Methods**:
- `fetch_cryptocurrency_data()` - Load market data from Yahoo Finance
- `get_supported_cryptocurrency_symbols()` - Available trading pairs
- `is_cached_data_fresh()` - Cache validity checking
- `validate_and_sanitize_market_data()` - Data quality assurance

**Features**:
- Intelligent caching system
- Data validation and cleaning
- Configurable cache expiration
- Support for multiple timeframes

### Visualization

#### BacktestChartGenerator

**Location**: [`visualization/backtest_chart_generator.py`](visualization/backtest_chart_generator.py)

Creates interactive charts using Plotly for strategy analysis.

**Key Methods**:
- `generate_backtest_chart()` - Create comprehensive strategy charts
- `display_all_charts()` - Show complete visualization suite
- Chart generation with buy/sell signals, indicators, and performance metrics

### Persistence

#### StrategyArchiver

**Location**: [`persistence/strategy_archiver.py`](persistence/strategy_archiver.py)

Manages saving and loading of strategy results and configurations.

**Key Methods**:
- `persist_strategy_results()` - Save profitable strategies with metadata
- `retrieve_strategy_results()` - Load saved strategies
- `list_persisted_strategies()` - Display available saved strategies

### User Interface

#### Command Line Interface

**Location**: [`core/command_line_interface.py`](core/command_line_interface.py)

Handles all user interaction through Rich-based terminal interface.

**Key Methods**:
- `prompt_user_for_input()` - Collect user input with validation
- `handle_single_strategy_test()` - Single strategy testing workflow
- `handle_strategy_comparison()` - Strategy comparison workflow
- `handle_saved_results_display()` - Display saved strategies
- `handle_configuration_display()` - Show application settings

---

## Configuration System

All configuration is centralized in [`config.py`](config.py):

### Key Configuration Sections

- **`DEFAULT_BACKTEST_CONFIG`**: Initial cash, commission, slippage settings
- **`DEFAULT_DATA_CONFIG`**: Default symbol, period, cache settings  
- **`PROFITABILITY_CRITERIA`**: Minimum return, Sharpe ratio, drawdown thresholds
- **`POPULAR_CRYPTO_SYMBOLS`**: List of supported cryptocurrency symbols

### Logging Configuration

**Location**: [`utils/logging_config.py`](utils/logging_config.py)

Centralized logging system with flexible control:

```python
from utils.logging_config import setup_application_logging

# Configure logging based on command line arguments
setup_application_logging(
    verbose=args.verbose,
    log_level=args.log_level,
    log_file=args.log_file,
    quiet=args.quiet,
    file_only=args.file_only
)
```

**Logging Levels**:
- Default: WARNING and ERROR only
- Verbose: INFO, WARNING, ERROR
- Debug: All levels including DEBUG
- Quiet: No output
- File-only: Log to file without console output

---

## Execution Flow

### Single Strategy Backtest

1. **Data Loading**: `MarketDataProvider.fetch_cryptocurrency_data()`
2. **Strategy Initialization**: Create strategy instance with parameters
3. **Signal Generation**: `strategy.generate_signals(data)`
4. **Backtest Execution**: `StrategyBacktestEngine.execute_strategy_evaluation()`
5. **Metrics Calculation**: `PerformanceAnalyzer.compute_extended_performance_stats()`
6. **Visualization**: `BacktestChartGenerator.display_all_charts()`
7. **Persistence**: `StrategyArchiver.persist_strategy_results()` (if profitable)

### Strategy Comparison

1. **Configuration Collection**: Gather multiple parameter sets
2. **Batch Execution**: Run backtests for all configurations
3. **Performance Ranking**: `PerformanceAnalyzer.sort_strategies_by_performance()`
4. **Comparative Analysis**: Generate comparison reports
5. **Best Strategy Selection**: Identify optimal configuration

---

## Adding New Strategies

### Step-by-Step Process

1. **Create Strategy File**: Add new file in [`strategies/implementations/`](strategies/implementations/)

2. **Implement Base Class**: Inherit from `AbstractTradingStrategy`

3. **Add Registration Decorator**: Use `@register_strategy`

4. **Implement Required Methods**:
   ```python
   from strategies.base.abstract_trading_strategy import AbstractTradingStrategy
   from strategies.base.strategy_registry import register_strategy
   
   @register_strategy
   class MyStrategy(AbstractTradingStrategy):
       @classmethod
       def get_label(cls) -> str:
           return "My Trading Strategy"
       
       @classmethod
       def get_abbreviated_name(cls) -> str:
           return "MTS"
       
       def generate_signals(self, data: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
           # Implementation here
           return buy_signals, sell_signals
   ```

5. **Test Strategy**: Strategy will automatically appear in the application menu

For detailed implementation guide, see [`STRATEGY_IMPLEMENTATION_GUIDE.md`](STRATEGY_IMPLEMENTATION_GUIDE.md).

---

## Development Best Practices

### Code Quality Standards

- **Type Annotations**: Use comprehensive type hints throughout
- **Docstrings**: Follow Google-style docstring format
- **Error Handling**: Use custom exception classes
- **PEP 8 Compliance**: Follow Python style guidelines
- **Testing**: Validate with existing test suite

### Custom Exception Classes

The application uses custom exceptions for better error handling:

```python
# Core exceptions
from core.trading_strategy_backtester import TradingStrategyBacktesterError

# Strategy exceptions
from strategies.base.abstract_trading_strategy import StrategyError

# Data exceptions
from market_data.market_data_provider import DataLoadError

# Backtesting exceptions
from backtesting.strategy_backtest_engine import BacktestError
```

### Performance Considerations

- **Vectorized Operations**: Use pandas/numpy for data processing
- **Caching**: Leverage data caching for repeated operations
- **Memory Management**: Handle large datasets efficiently
- **Profiling**: Monitor performance for optimization opportunities

---

## Testing Strategy

### Test Files

- **[`test_setup.py`](test_setup.py)**: Environment and dependency validation
- **[`functional_test.py`](functional_test.py)**: End-to-end functionality testing
- **[`validation_test.py`](validation_test.py)**: Comprehensive system validation

### Running Tests

```bash
# Environment validation
python test_setup.py

# Functional testing
python functional_test.py

# Comprehensive validation
python validation_test.py
```

---

## Developer Troubleshooting

### Common Issues

- **Module import error**: Check virtual environment and PYTHONPATH
- **Missing data**: Verify internet connection, clear cache if needed
- **Vectorbt errors**: Ensure data sufficiency and signal validity
- **Charts not displaying**: Check Plotly installation, verify HTML files in `results/charts/`
- **Performance issues**: Use shorter periods, limit simultaneous comparisons

### Debugging Tools

- **Logging**: Use `--verbose` or `--log-level DEBUG` for detailed output
- **File Logging**: Use `--log-file` to save logs for analysis
- **Validation Tests**: Run comprehensive test suite to identify issues

---

## Extension Points

### Adding New Data Sources

Extend `MarketDataProvider` to support additional data sources beyond Yahoo Finance.

### Custom Performance Metrics

Add new metrics to `PerformanceAnalyzer` for specialized analysis requirements.

### Enhanced Visualizations

Extend `BacktestChartGenerator` with additional chart types and indicators.

### Alternative UI Interfaces

Create new interface modules while maintaining the same core logic.

---

## Limitations and Future Enhancements

### Current Limitations

- **Data Source**: Limited to Yahoo Finance
- **Real-time Trading**: Backtesting only, no live trading
- **Parameter Optimization**: Manual parameter tuning only
- **Asset Classes**: Cryptocurrency focus, limited multi-asset support

### Potential Enhancements

- **Multiple Data Sources**: Integration with additional market data providers
- **Automated Optimization**: Parameter optimization algorithms
- **Portfolio Backtesting**: Multi-asset portfolio strategies
- **Real-time Capabilities**: Live data feeds and paper trading
- **Advanced Analytics**: Machine learning integration
- **Web Interface**: Browser-based UI alternative

---

## See Also

- [`README.md`](README.md): Installation, usage, and end-user instructions
- [`STRATEGY_IMPLEMENTATION_GUIDE.md`](STRATEGY_IMPLEMENTATION_GUIDE.md): Detailed strategy creation guide