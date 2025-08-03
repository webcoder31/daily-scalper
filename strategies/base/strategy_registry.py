"""
Strategy Registry Module for Dynamic Strategy Management.

This module provides a centralized registry system for managing trading strategies
in the Trading Strategy Backtester application. It implements a decorator-based registration
pattern that allows strategies to automatically register themselves when imported.

The registry provides type-safe operations for:
- Strategy registration and discovery
- Strategy instantiation with parameter validation
- Parameter information retrieval
- Strategy class lookup by various identifiers

The registry follows the Registry Pattern design, providing a single point of
access for all available trading strategies while maintaining type safety
and comprehensive error handling.
"""

from typing import Dict, Any, Type, List, Optional, Union
import inspect
import logging

# Import base strategy and exceptions
from .abstract_trading_strategy import AbstractTradingStrategy, StrategyError, ParameterValidationError

# Configure logging
from utils.logging_config import get_logger
logger = get_logger(__name__)


class RegistryError(StrategyError):
    """Exception raised for strategy registry-related errors."""
    pass


class StrategyNotFoundError(RegistryError):
    """Exception raised when a requested strategy is not found in the registry."""
    pass


class DuplicateStrategyError(RegistryError):
    """Exception raised when attempting to register a strategy that already exists."""
    pass


# Global registry of trading strategies
# Maps class names to strategy classes
STRATEGY_REGISTRY: Dict[str, Type[AbstractTradingStrategy]] = {}


def register_strategy(cls: Type[AbstractTradingStrategy]) -> Type[AbstractTradingStrategy]:
    """
    Decorator to register a strategy class in the global registry.
    
    This decorator validates that the class is a proper AbstractTradingStrategy subclass
    and registers it for later retrieval. It should be applied to all concrete
    strategy implementations.
    
    Args:
        cls: The strategy class to register. Must be a subclass of AbstractTradingStrategy.
    
    Returns:
        The original class unchanged (decorator pattern).
    
    Raises:
        RegistryError: If the class is not a valid AbstractTradingStrategy subclass.
        DuplicateStrategyError: If a strategy with the same name is already registered.
    
    Example:
        @register_strategy
        class MyStrategy(AbstractTradingStrategy):
            pass
    """
    # Validate that the class is a proper AbstractTradingStrategy subclass
    if not inspect.isclass(cls):
        raise RegistryError(f"Only classes can be registered as strategies, got {type(cls)}")
    
    if not issubclass(cls, AbstractTradingStrategy):
        raise RegistryError(
            f"Strategy class '{cls.__name__}' must inherit from AbstractTradingStrategy"
        )
    
    # Check for duplicate registration
    class_name = cls.__name__
    if class_name in STRATEGY_REGISTRY:
        existing_class = STRATEGY_REGISTRY[class_name]
        if existing_class is not cls:  # Allow re-registration of the same class
            raise DuplicateStrategyError(
                f"Strategy '{class_name}' is already registered. "
                f"Existing: {existing_class}, New: {cls}"
            )
    
    # Register the strategy
    STRATEGY_REGISTRY[class_name] = cls
    logger.debug(f"Registered strategy: {class_name}")
    
    return cls


def get_strategy_names() -> List[str]:
    """
    Get human-readable names of all registered strategies.
    
    Returns the display labels (from get_label() method) of all registered
    strategies, which are more user-friendly than class names.
    
    Returns:
        List of strategy display names sorted alphabetically.
    
    Example:
        ['Bollinger Bands', 'EMA + RSI Strategy', 'Relative Strength Index', 'Simple Moving Average']
    """
    try:
        names = []
        for strategy_class in STRATEGY_REGISTRY.values():
            try:
                label = strategy_class.get_label()
                names.append(label)
            except Exception as e:
                logger.warning(f"Failed to get label for {strategy_class.__name__}: {e}")
                names.append(strategy_class.__name__)  # Fallback to class name
        
        return sorted(names)
    except Exception as e:
        logger.error(f"Error getting strategy names: {e}")
        return []


def get_strategy_classes() -> Dict[str, Type[AbstractTradingStrategy]]:
    """
    Get all registered strategy classes mapped by their display labels.
    
    Creates a mapping from user-friendly strategy names (from get_label())
    to their corresponding strategy classes.
    
    Returns:
        Dictionary mapping strategy display names to their classes.
    
    Example:
        {
            'Simple Moving Average': SMAStrategy,
            'Relative Strength Index': RSIStrategy,
            ...
        }
    """
    try:
        label_to_class = {}
        for strategy_class in STRATEGY_REGISTRY.values():
            try:
                label = strategy_class.get_label()
                label_to_class[label] = strategy_class
            except Exception as e:
                logger.warning(f"Failed to get label for {strategy_class.__name__}: {e}")
                # Use class name as fallback
                label_to_class[strategy_class.__name__] = strategy_class
        
        return label_to_class
    except Exception as e:
        logger.error(f"Error getting strategy classes: {e}")
        return {}


def get_strategy_class(name: str) -> Optional[Type[AbstractTradingStrategy]]:
    """
    Get a strategy class by its display label.
    
    Looks up a strategy class using its user-friendly display name
    (from the get_label() method).
    
    Args:
        name: Display label of the strategy to find.
    
    Returns:
        Strategy class if found, None otherwise.
    
    Example:
        strategy_class = get_strategy_class("Simple Moving Average")
    """
    if not isinstance(name, str) or not name.strip():
        logger.warning(f"Invalid strategy name: {name}")
        return None
    
    try:
        strategy_classes = get_strategy_classes()
        return strategy_classes.get(name.strip())
    except Exception as e:
        logger.error(f"Error getting strategy class for '{name}': {e}")
        return None


def get_strategy_class_by_classname(classname: str) -> Optional[Type[AbstractTradingStrategy]]:
    """
    Get a strategy class by its Python class name.
    
    Directly looks up a strategy class using its Python class name
    (e.g., 'SMAStrategy', 'RSIStrategy').
    
    Args:
        classname: Python class name of the strategy.
    
    Returns:
        Strategy class if found, None otherwise.
    
    Example:
        strategy_class = get_strategy_class_by_classname("SMAStrategy")
    """
    if not isinstance(classname, str) or not classname.strip():
        logger.warning(f"Invalid class name: {classname}")
        return None
    
    try:
        return STRATEGY_REGISTRY.get(classname.strip())
    except Exception as e:
        logger.error(f"Error getting strategy class by classname '{classname}': {e}")
        return None


def create_strategy(name: str, **params: Any) -> AbstractTradingStrategy:
    """
    Create a strategy instance by its display label or class name.
    
    Attempts to find the strategy by display label first, then falls back
    to class name lookup. Creates an instance with the provided parameters.
    
    Args:
        name: Display label or class name of the strategy.
        **params: Parameters to pass to the strategy constructor.
    
    Returns:
        Initialized strategy instance.
    
    Raises:
        StrategyNotFoundError: If the strategy is not found in the registry.
        ParameterValidationError: If the provided parameters are invalid.
        StrategyError: If strategy instantiation fails.
    
    Example:
        strategy = create_strategy("Simple Moving Average", short_window=10, long_window=30)
    """
    if not isinstance(name, str) or not name.strip():
        raise StrategyNotFoundError(f"Invalid strategy name: {name}")
    
    name = name.strip()
    
    # First try to find by display label
    strategy_class = get_strategy_class(name)
    
    # If not found, try by class name
    if not strategy_class:
        strategy_class = get_strategy_class_by_classname(name)
    
    if not strategy_class:
        available_strategies = get_strategy_names()
        raise StrategyNotFoundError(
            f"Strategy '{name}' not found in registry. "
            f"Available strategies: {available_strategies}"
        )
    
    try:
        # Create strategy instance with provided parameters
        return strategy_class(**params)
    except TypeError as e:
        # Handle invalid constructor parameters
        raise ParameterValidationError(
            f"Invalid parameters for strategy '{name}': {e}"
        ) from e
    except Exception as e:
        # Handle other instantiation errors
        raise StrategyError(
            f"Failed to create strategy '{name}': {e}"
        ) from e


def get_strategy_parameter_info(name: str) -> Dict[str, Any]:
    """
    Get parameter information for a strategy by name.
    
    Retrieves detailed parameter definitions including types, defaults,
    ranges, and descriptions for the specified strategy.
    
    Args:
        name: Display label or class name of the strategy.
    
    Returns:
        Dictionary containing parameter information with the following structure:
        {
            'param_name': {
                'type': parameter_type,
                'default': default_value,
                'range': (min_val, max_val),  # if applicable
                'description': 'parameter description',
                'required': boolean
            }
        }
    
    Raises:
        StrategyNotFoundError: If the strategy is not found in the registry.
    
    Example:
        param_info = get_strategy_parameter_info("Simple Moving Average")
    """
    if not isinstance(name, str) or not name.strip():
        raise StrategyNotFoundError(f"Invalid strategy name: {name}")
    
    name = name.strip()
    
    # First try to get by display label
    strategy_class = get_strategy_class(name)
    
    # If not found, try by class name
    if not strategy_class:
        strategy_class = get_strategy_class_by_classname(name)
    
    if not strategy_class:
        available_strategies = get_strategy_names()
        raise StrategyNotFoundError(
            f"Strategy '{name}' not found in registry. "
            f"Available strategies: {available_strategies}"
        )
    
    try:
        # Try to get parameter definitions from the strategy class
        if hasattr(strategy_class, 'get_parameter_definitions'):
            return strategy_class.get_parameter_definitions()
        
        # Fallback: use inspection to get constructor parameters
        return _extract_constructor_parameters(strategy_class)
    
    except Exception as e:
        logger.error(f"Error getting parameter info for '{name}': {e}")
        raise StrategyError(
            f"Failed to get parameter information for strategy '{name}': {e}"
        ) from e


def _extract_constructor_parameters(strategy_class: Type[AbstractTradingStrategy]) -> Dict[str, Any]:
    """
    Extract parameter information from strategy constructor using inspection.
    
    This is a fallback method used when a strategy doesn't implement
    get_parameter_definitions().
    
    Args:
        strategy_class: Strategy class to inspect.
    
    Returns:
        Dictionary of parameter information extracted from constructor.
    """
    params = {}
    
    try:
        signature = inspect.signature(strategy_class.__init__)
        
        for param_name, param in signature.parameters.items():
            # Skip 'self' and **kwargs parameters
            if param_name in ('self', 'kwargs'):
                continue
            
            # Skip *args parameters
            if param.kind == inspect.Parameter.VAR_POSITIONAL:
                continue
            
            param_info = {
                'type': param.annotation if param.annotation != inspect.Parameter.empty else Any,
                'required': param.default == inspect.Parameter.empty,
                'description': f'Parameter for {strategy_class.__name__}'
            }
            
            # Add default value if available
            if param.default != inspect.Parameter.empty:
                param_info['default'] = param.default
            
            params[param_name] = param_info
    
    except Exception as e:
        logger.warning(f"Failed to extract constructor parameters for {strategy_class.__name__}: {e}")
    
    return params


def list_registered_strategies() -> Dict[str, Dict[str, Any]]:
    """
    Get detailed information about all registered strategies.
    
    Returns comprehensive information about each registered strategy including
    class name, display label, short label, and parameter definitions.
    
    Returns:
        Dictionary mapping class names to strategy information.
    
    Example:
        {
            'SMAStrategy': {
                'class_name': 'SMAStrategy',
                'label': 'Simple Moving Average',
                'short_label': 'SMA',
                'parameters': {...}
            }
        }
    """
    strategies_info = {}
    
    for class_name, strategy_class in STRATEGY_REGISTRY.items():
        try:
            info = {
                'class_name': class_name,
                'label': strategy_class.get_label(),
                'short_label': strategy_class.get_short_label(),
            }
            
            # Try to get parameter definitions
            try:
                if hasattr(strategy_class, 'get_parameter_definitions'):
                    info['parameters'] = strategy_class.get_parameter_definitions()
                else:
                    info['parameters'] = _extract_constructor_parameters(strategy_class)
            except Exception as e:
                logger.warning(f"Failed to get parameters for {class_name}: {e}")
                info['parameters'] = {}
            
            strategies_info[class_name] = info
            
        except Exception as e:
            logger.error(f"Error getting info for strategy {class_name}: {e}")
            # Include basic info even if some details fail
            strategies_info[class_name] = {
                'class_name': class_name,
                'label': class_name,  # Fallback to class name
                'short_label': class_name[:3].upper(),  # Simple abbreviation
                'parameters': {}
            }
    
    return strategies_info


def clear_registry() -> None:
    """
    Clear all registered strategies from the registry.
    
    This function is primarily intended for testing purposes to ensure
    a clean state between test runs.
    
    Warning:
        This will remove all registered strategies and may break functionality
        if called during normal operation.
    """
    global STRATEGY_REGISTRY
    STRATEGY_REGISTRY.clear()
    logger.info("Strategy registry cleared")


def get_registry_size() -> int:
    """
    Get the number of strategies currently registered.
    
    Returns:
        Number of registered strategies.
    """
    return len(STRATEGY_REGISTRY)