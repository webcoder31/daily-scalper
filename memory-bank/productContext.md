# Product Context

This file provides a high-level overview of the project and the expected product that will be created. Initially it is based upon projectBrief.md (if provided) and all other available project-related information in the working directory. This file is intended to be updated as the project evolves, and should be used to inform all other modes of the project's goals and context.
2025-07-26 18:58:23 - Log of updates made will be appended as footnotes to the end of this file.

*

## Project Goal

* Daily Scalper is a modular Python application designed to test, evaluate, and save cryptocurrency trading strategies using vectorbt.
* The project's main goal is to provide a tool for traders and analysts to backtest trading strategies on historical cryptocurrency data.
* It aims to offer a user-friendly interface for strategy testing with comprehensive performance metrics and visualizations.

## Key Features

* **Modular Strategy Architecture**: Easily extendable with new trading strategies
* **Vectorized Backtesting**: High-performance backtesting using vectorbt
* **Interactive Visualization**: Charts with buy/sell signals and performance metrics
* **Strategy Comparison**: Ability to compare multiple strategy configurations
* **Automatic Saving**: Profitable strategies are automatically saved
* **Data Caching**: Intelligent caching of market data to improve performance
* **Comprehensive Metrics**: Detailed performance metrics including Sharpe ratio, drawdown, win rate, etc.

## Overall Architecture

* **strategies/**: Contains trading strategies (SMA Crossover, RSI Threshold)
* **backtest/**: Contains the backtesting engine and performance metrics
* **utils/**: Contains utilities like data loading, visualization, and strategy saving
* **data/**: Contains cached market data
* **results/**: Contains saved strategy results and charts
* **main.py**: Main application with interactive menu interface
* **config.py**: Global configuration settings