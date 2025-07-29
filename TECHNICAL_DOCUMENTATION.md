# Daily Scalper - Technical Documentation

## Purpose

This document is for developers and contributors. It covers the internal architecture, code structure, extension points, and best practices for maintaining and extending Daily Scalper.

For installation and user instructions, see [`README.md`](README.md).

---

## Architecture Overview

Daily Scalper is a modular, object-oriented Python application for backtesting and analyzing cryptocurrency trading strategies. It is designed for easy extension and maintainability.

### Main Modules

- **strategies/**: All trading strategies and the strategy registry system.
- **backtest/**: Backtest engine and performance metrics.
- **utils/**: Data loading, visualization, strategy saving, and period utilities.
- **results/**: Output directory for saved strategies, reports, and charts (created at runtime).
- **main.py**: Entry point and interactive CLI.
- **config.py**: All configuration (capital, commission, cache, profitability criteria, etc.).

---

## Project Structure

```
daily-scalper/
├── strategies/
│   ├── __init__.py
│   ├── base_strategy.py
│   ├── sma_strategy.py
│   ├── rsi_strategy.py
│   ├── bb_strategy.py
│   └── strategy_registry.py
├── backtest/
│   ├── __init__.py
│   ├── backtest_engine.py
│   └── performance_metrics.py
├── utils/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── visualizer.py
│   ├── strategy_saver.py
│   └── period_translator.py
├── results/
│   ├── strategies/
│   ├── reports/
│   └── charts/
├── main.py
├── test_setup.py
├── run.sh
├── start.sh
├── config.py
├── README.md
└── STRATEGY_IMPLEMENTATION_GUIDE.md
```

---

## Core Components

### Strategies

- **BaseStrategy**: Abstract class. All strategies must implement `generate_signals`, `get_explanation`, and parameter logic.
- **SMAStrategy**: Simple moving average crossover.
- **RSIStrategy**: Relative Strength Index threshold.
- **BBStrategy**: Bollinger Bands.
- **strategy_registry.py**: Uses `@register_strategy` decorator for automatic discovery and menu integration.

#### Adding a New Strategy

1. Create a new file in `strategies/` and subclass `BaseStrategy`.
2. Use the `@register_strategy` decorator.
3. Implement required methods.
4. Your strategy will appear in the app menu automatically.

See [`STRATEGY_IMPLEMENTATION_GUIDE.md`](STRATEGY_IMPLEMENTATION_GUIDE.md) for a step-by-step guide.

---

### Backtest Engine

- **BacktestEngine**: Runs vectorbt-based backtests, handles simulation, commissions, slippage, and result packaging.
- **PerformanceMetrics**: Calculates advanced metrics (return, Sharpe, drawdown, win rate, etc.).

---

### Utilities

- **DataLoader**: Loads and caches OHLCV data from yfinance.
- **Visualizer**: Generates interactive charts (Plotly).
- **StrategySaver**: Saves results, strategies, and reports.
- **PeriodTranslator**: Handles period string conversions.

---

## Configuration

All configuration is in [`config.py`](config.py):

- `DEFAULT_BACKTEST_CONFIG`: initial cash, commission, slippage
- `DEFAULT_DATA_CONFIG`: default symbol, period, cache
- `PROFITABILITY_CRITERIA`: min return, Sharpe, drawdown, min trades
- `POPULAR_CRYPTO_SYMBOLS`: list of supported symbols

---

## Execution Flow

1. **Data Loading**: `DataLoader.load_crypto_data()`
2. **Strategy Initialization**: Instantiate a strategy with parameters.
3. **Signal Generation**: `strategy.generate_signals(data)`
4. **Backtest Execution**: `BacktestEngine.run_backtest(strategy, data)`
5. **Metrics Calculation**: `PerformanceMetrics.calculate_advanced_metrics(results)`
6. **Visualization**: `Visualizer.show_all_plots(results)`
7. **Saving**: `StrategySaver.save_strategy_results(results)`

---

## Developer Troubleshooting

- **Module import error**: Check your virtual environment and PYTHONPATH.
- **Missing data**: Check internet connection, clear cache if needed.
- **Vectorbt errors**: Ensure data is sufficient and signals are valid.
- **Charts not displaying**: Check Plotly installation, open HTML files in `results/charts/`.
- **Performance**: Use shorter periods for tests, limit simultaneous strategy comparisons.

---

## Best Practices

- Follow PEP 8 and add docstrings for all new code.
- Never commit cache or results files.
- Use environment variables for any API keys (if added).
- Test new strategies with `test_setup.py`.
- Keep user-facing and developer documentation separate.

---

## Limitations

- No real-time trading (backtesting only)
- Data limited to Yahoo Finance
- No automatic parameter optimization (manual only)

---

## See Also

- [`README.md`](README.md): For installation, usage, and end-user instructions.
- [`STRATEGY_IMPLEMENTATION_GUIDE.md`](STRATEGY_IMPLEMENTATION_GUIDE.md): For a detailed guide on adding new strategies.
