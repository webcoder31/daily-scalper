# Decision Log

This file records architectural and implementation decisions using a list format.
2025-07-26 19:01:54 - Log of updates made.

*
      
## Decision

* Modular Architecture with SOLID Principles
      
## Rationale 

* Separating concerns into distinct modules (strategies, backtest, utils) improves maintainability
* Using abstract classes (BaseStrategy) enables easy extension with new strategy implementations
* Clear interfaces between components reduces coupling

## Implementation Details

* strategies/ module contains all trading strategy implementations
* backtest/ module encapsulates the backtesting engine
* utils/ module provides supporting functionality
* Abstract BaseStrategy class defines the interface for all strategies

*
      
## Decision

* Vectorized Backtesting with vectorbt
      
## Rationale 

* Performance: Vectorized operations are significantly faster than iterative approaches
* Consistency: Standardized calculations of performance metrics
* Reliability: Well-tested library reduces implementation errors

## Implementation Details

* BacktestEngine uses vectorbt's Portfolio class to run simulations
* Performance metrics calculated using vectorbt's stats methods
* Slippage and commission modeling included in backtest configuration

*
      
## Decision

* Data Caching System
      
## Rationale 

* Reduce redundant API calls to Yahoo Finance
* Improve application responsiveness
* Protect against API rate limits and network issues

## Implementation Details

* Data is stored in data/ directory
* Cache validity controlled by cache_max_age_hours parameter (default 24h)
* Automatic validation and refreshing of stale data

*
      
## Decision

* Rich Interactive Terminal UI
      
## Rationale 

* Improved user experience with formatted tables and color
* Clearer presentation of complex financial metrics
* Better error reporting and status indicators

## Implementation Details

* Uses rich library for terminal formatting
* Tables for presenting metrics and comparison results
* Panels for section headers and status messages
* Color coding for positive/negative performance indicators
*
      
## Decision

* Refactor Prompt Text Display to Avoid Duplicate Default Values
      
## Rationale 

* Current implementation shows default values twice:
  1. In the prompt text string with square brackets: `[BTC-USD]`
  2. Automatically by Rich's Prompt.ask() function with parentheses: `(BTC-USD)`
* This creates redundant UI like: `"Crypto pair [BTC-USD]: (BTC-USD):"`
* Cleaner UI would improve user experience

## Implementation Details

* Remove default values from prompt text strings in main.py
* Keep default values in the Prompt.ask() function parameters
* Document changes in memory-bank/prompt-refactoring.md
* This change maintains functionality while improving UI clarity