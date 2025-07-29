# System Patterns

This file documents recurring patterns and standards used in the project.
It is optional, but recommended to be updated as the project evolves.
2025-07-26 19:04:31 - Log of updates made.

*

## Coding Patterns

* **Strategy Pattern**: Used extensively with BaseStrategy as the abstract interface and concrete implementations like SMACrossoverStrategy and RSIThresholdStrategy
* **Dependency Injection**: Components receive their dependencies (e.g., DataLoader passed to BacktestEngine) rather than creating them
* **Factory Methods**: Class methods that create and return objects (e.g., get_period_description in PeriodTranslator)
* **Rich Docstrings**: Comprehensive documentation in Python docstrings using Google-style format
* **Type Annotations**: Extensive use of typing hints throughout the codebase
* **Error Handling**: Try/except blocks with specific error handling in critical sections
* **Configuration Centralization**: All configurable parameters defined in config.py

## Architectural Patterns

* **MVC-like Structure**:
  * Model: Strategies and backtest engine
  * View: Visualizer and Rich UI components
  * Controller: Main application class and menu functions
* **Module Separation**: Clear boundaries between modules (strategies, backtest, utils)
* **Interface Segregation**: Each class has a single responsibility
* **Composition Over Inheritance**: Components composed together rather than deep inheritance hierarchies
* **Stateless Processing**: Most components are designed to be stateless for easier testing
* **Caching Layer**: Data access abstracted behind a caching layer

## Testing Patterns

* **Validation Testing**: test_setup.py validates the environment and dependencies
* **Profitability Criteria**: Standardized criteria for evaluating strategy performance
* **Comparison Framework**: Standard method for ranking and comparing strategies
* **Visual Validation**: Interactive charts for visual verification of strategy performance
* **Configurable Test Parameters**: Easily adjustable test parameters via configuration