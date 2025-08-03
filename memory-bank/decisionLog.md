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

[2025-08-03 09:01:00] - Core Application Refactoring Implementation

## Decision

* Comprehensive refactoring of core application files with modern Python standards

## Rationale 

* Improve code maintainability and readability with complete type annotations
* Enhance error handling with custom exception classes and specific error messages
* Standardize documentation with professional docstring format
* Fix critical bugs and improve code quality for production readiness
* Ensure PEP8 compliance and consistent formatting throughout the codebase

## Implementation Details

* Fixed critical string formatting bug in backtest/performance_metrics.py:132
* Added complete type annotations to config.py, main.py, app.py, and cli.py
* Implemented professional docstring format with Args, Returns, and Raises sections
* Created custom exception classes (DailyScalperError, DataLoadError, StrategyError, etc.)
* Enhanced error handling with try-catch blocks and user-friendly error messages
* Improved code structure with helper functions and better separation of concerns
* Standardized all text to English and removed French comments
* Added comprehensive input validation and type checking


[2025-08-03 11:08:00] - Utils Module Comprehensive Refactoring Implementation

## Decision

* Complete refactoring of all utility modules with professional Python standards and enhanced functionality

## Rationale 

* Improve code maintainability and readability with complete type annotations across all utility modules
* Enhance error handling with custom exception classes specific to each utility module's domain
* Standardize documentation with professional docstring format throughout the utils package
* Improve modularity and separation of concerns within utility functions
* Ensure consistency with previously refactored core application and strategies modules
* Add comprehensive validation and data integrity checks across all utility operations
* Enhance user experience with better error messages and robust file handling

## Implementation Details

* Created custom exception hierarchies for each utility module (DataLoadError, VisualizationError, UIComponentError, etc.)
* Added complete type annotations using Optional, Union, Dict, List, pd.DataFrame, Path throughout all modules
* Implemented professional docstring format with Args, Returns, and Raises sections for all functions and classes
* Enhanced data validation with comprehensive parameter checking and data integrity verification
* Improved file handling with robust error management and proper resource cleanup
* Added theme management and validation system for consistent UI styling
* Enhanced interactive UI components with better navigation and error handling
* Improved visualization capabilities with comprehensive chart configuration and error handling
* Standardized all text to English and removed French comments for consistency
* Added helper functions and improved code organization for better maintainability
* Implemented comprehensive logging throughout all utility modules for better debugging


[2025-08-03 17:14:00] - Optional Logging Implementation

## Decision

* Implemented optional logging output controlled by command line arguments

## Rationale 

* Users requested the ability to control logging output, making it optional and configurable
* Previous implementation had hardcoded logging levels in individual modules
* Centralized logging configuration improves maintainability and user experience
* Command line control provides flexibility for different use cases (debugging, production, quiet operation)

## Implementation Details

* Created new `utils/logging_config.py` module with centralized logging configuration
* Added `LoggingConfig` class with methods to configure logging application-wide
* Implemented `setup_application_logging()` function for easy command line integration
* Added command line argument parsing in `cli.py` with options:
  - `--verbose` / `-v`: Enable INFO level logging
  - `--log-level`: Set specific log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - `--log-file`: Save logs to file in addition to console
  - `--quiet` / `-q`: Disable all logging output
* Updated all modules to use centralized logging configuration:
  - `backtest/backtest_engine.py`
  - `backtest/performance_metrics.py`
  - `utils/data_loader.py`
  - `utils/period_translator.py`
  - `utils/strategy_saver.py`
  - `utils/theme.py`
  - `utils/ui_components.py`
  - `utils/visualizer.py`
  - `strategies/strategy_registry.py`
* Replaced individual `logging.basicConfig()` calls with centralized `get_logger()` function
* Default behavior: Only WARNING and ERROR messages are shown (minimal logging)
* Added `--file-only` option to log exclusively to file without console output
* Enhanced logging configuration with file_only parameter and proper validation
* Comprehensive testing confirms all logging levels work correctly including quiet mode and file-only logging
