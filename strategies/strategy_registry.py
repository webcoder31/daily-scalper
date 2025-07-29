"""
Strategy Registry module - Manages registered trading strategies.
"""

from typing import Dict, Any, Type, List, Optional
import inspect
from .base_strategy import BaseStrategy

# Global registry of trading strategies
STRATEGY_REGISTRY = {}

def register_strategy(cls):
    """
    Decorator to register a strategy class in the registry.
    
    Args:
        cls: The strategy class to register
        
    Returns:
        The original class
    """
    if not inspect.isclass(cls) or not issubclass(cls, BaseStrategy):
        raise TypeError("Only BaseStrategy subclasses can be registered")
    
    STRATEGY_REGISTRY[cls.__name__] = cls
    return cls

def get_strategy_names() -> List[str]:
    """
    Get names of all registered strategies using their short descriptions.
    
    Returns:
        List of strategy names (short descriptions)
    """
    names = []
    for strategy_class in STRATEGY_REGISTRY.values():
        names.append(strategy_class.get_label())
    return names

# def get_strategy_classes() -> Dict[str, Type[BaseStrategy]]:
#     """
#     Get all registered strategy classes.
    
#     Returns:
#         Dictionary of strategy names and classes
#     """
#     return STRATEGY_REGISTRY.copy()

def get_strategy_classes() -> Dict[str, Type[BaseStrategy]]:
    """
    Get all registered strategy classes with their short descriptions as keys.
    
    Returns:
        Dictionary mapping strategy short descriptions to their classes
    """
    return {
        strategy_class.get_label(): strategy_class
        for strategy_class in STRATEGY_REGISTRY.values()
    }

def get_strategy_class(name: str) -> Optional[Type[BaseStrategy]]:
    """
    Get a strategy class by its short description.
    
    Args:
        name: Short description of the strategy
        
    Returns:
        Strategy class or None if not found
    """
    strategy_classes = get_strategy_classes()
    return strategy_classes.get(name)

def get_strategy_class_by_classname(classname: str) -> Optional[Type[BaseStrategy]]:
    """
    Get a strategy class by its class name.
    
    Args:
        classname: Name of the strategy class
        
    Returns:
        Strategy class or None if not found
    """
    return STRATEGY_REGISTRY.get(classname)

def create_strategy(name: str, **params) -> BaseStrategy:
    """
    Create a strategy instance by its short description.
    
    Args:
        name: Short description of the strategy
        **params: Parameters to pass to the strategy constructor
        
    Returns:
        Strategy instance
        
    Raises:
        ValueError: If strategy not found
    """
    strategy_class = get_strategy_class(name)
    if not strategy_class:
        # Try finding by class name as fallback
        strategy_class = get_strategy_class_by_classname(name)
        if not strategy_class:
            raise ValueError(f"Strategy '{name}' not found in registry")
    
    return strategy_class(**params)

def get_strategy_parameter_info(name: str) -> Dict[str, Any]:
    """
    Get parameter information for a strategy.
    
    Args:
        name: Short description or class name of the strategy
        
    Returns:
        Dictionary with parameter information
        
    Raises:
        ValueError: If strategy not found
    """
    # First try to get by short description
    strategy_class = get_strategy_class(name)
    if not strategy_class:
        # Try by class name as fallback
        strategy_class = get_strategy_class_by_classname(name)
        if not strategy_class:
            raise ValueError(f"Strategy '{name}' not found in registry")
    
    # Get parameter information from class method if available
    if hasattr(strategy_class, 'get_parameter_definitions'):
        return strategy_class.get_parameter_definitions()
    
    # Otherwise, use inspection to get default parameters
    params = {}
    signature = inspect.signature(strategy_class.__init__)
    for param_name, param in signature.parameters.items():
        # Skip self and **kwargs
        if param_name in ('self', 'kwargs'):
            continue
            
        params[param_name] = {
            'type': param.annotation if param.annotation != inspect.Parameter.empty else None,
            'default': param.default if param.default != inspect.Parameter.empty else None,
            'required': param.default == inspect.Parameter.empty
        }
    
    return params