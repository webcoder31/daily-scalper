"""
Centralized logging configuration for the Trading Strategy Backtester application.

This module provides centralized logging configuration that can be controlled
via command line arguments. It supports different log levels and optional
logging output.
"""

import logging
import sys
from typing import Optional, Dict, Any
from pathlib import Path


class LoggingConfig:
    """
    Centralized logging configuration manager.
    
    This class provides methods to configure logging for the entire application
    based on command line arguments or programmatic settings.
    """
    
    # Available log levels
    LOG_LEVELS: Dict[str, int] = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    @classmethod
    def configure_logging(
        cls,
        enabled: bool = True,
        level: str = 'WARNING',
        log_file: Optional[str] = None,
        format_string: Optional[str] = None,
        file_only: bool = False
    ) -> None:
        """
        Configure logging for the entire application.
        
        Args:
            enabled: Whether logging is enabled. If False, logging is disabled.
            level: Log level as string ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
            log_file: Optional path to log file. If None, logs to console only.
            format_string: Optional custom format string for log messages.
            file_only: If True, logs only to file (no console output). Requires log_file.
        
        Raises:
            ValueError: If log level is invalid or file_only is True without log_file.
        """
        # Clear any existing handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        if not enabled:
            # Disable logging by setting level to CRITICAL+1
            logging.disable(logging.CRITICAL)
            return
        else:
            # Re-enable logging if it was previously disabled
            logging.disable(logging.NOTSET)
        
        # Validate log level
        level_upper = level.upper()
        if level_upper not in cls.LOG_LEVELS:
            raise ValueError(f"Invalid log level: {level}. Must be one of: {list(cls.LOG_LEVELS.keys())}")
        
        # Set default format if none provided
        if format_string is None:
            format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # Validate file_only option
        if file_only and not log_file:
            raise ValueError("file_only=True requires log_file to be specified")
        
        # Configure basic logging
        handlers = []
        
        # Console handler (unless file_only is True)
        if not file_only:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(logging.Formatter(format_string))
            handlers.append(console_handler)
        
        # File handler if specified
        if log_file:
            try:
                log_path = Path(log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                file_handler = logging.FileHandler(log_file)
                file_handler.setFormatter(logging.Formatter(format_string))
                handlers.append(file_handler)
            except Exception as e:
                # If file logging fails and file_only is True, this is a critical error
                if file_only:
                    raise ValueError(f"Could not create log file {log_file}: {e}")
                else:
                    # If file logging fails but console is available, continue with console only
                    print(f"Warning: Could not create log file {log_file}: {e}", file=sys.stderr)
        
        # Configure root logger
        logging.basicConfig(
            level=cls.LOG_LEVELS[level_upper],
            handlers=handlers,
            format=format_string,
            force=True  # Override any existing configuration
        )
    
    @classmethod
    def get_available_levels(cls) -> list[str]:
        """
        Get list of available log levels.
        
        Returns:
            List of available log level names.
        """
        return list(cls.LOG_LEVELS.keys())
    
    @classmethod
    def is_valid_level(cls, level: str) -> bool:
        """
        Check if a log level is valid.
        
        Args:
            level: Log level to validate.
        
        Returns:
            True if level is valid, False otherwise.
        """
        return level.upper() in cls.LOG_LEVELS
    
    @classmethod
    def get_current_level(cls) -> str:
        """
        Get the current effective log level.
        
        Returns:
            Current log level as string.
        """
        current_level = logging.getLogger().getEffectiveLevel()
        for name, value in cls.LOG_LEVELS.items():
            if value == current_level:
                return name
        return 'UNKNOWN'
    
    @classmethod
    def disable_logging(cls) -> None:
        """
        Completely disable logging for the application.
        """
        logging.disable(logging.CRITICAL)
    
    @classmethod
    def enable_logging(cls, level: str = 'INFO') -> None:
        """
        Re-enable logging with specified level.
        
        Args:
            level: Log level to set when re-enabling.
        """
        logging.disable(logging.NOTSET)
        if cls.is_valid_level(level):
            logging.getLogger().setLevel(cls.LOG_LEVELS[level.upper()])


def setup_application_logging(
    verbose: bool = False,
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    quiet: bool = False,
    file_only: bool = False
) -> None:
    """
    Setup logging for the Trading Strategy Backtester application based on command line arguments.
    
    This is a convenience function that translates common command line arguments
    into appropriate logging configuration.
    
    Args:
        verbose: If True, enables INFO level logging.
        log_level: Explicit log level (overrides verbose).
        log_file: Optional path to log file.
        quiet: If True, disables all logging output.
        file_only: If True, logs only to file (no console output). Requires log_file.
    """
    if quiet:
        LoggingConfig.configure_logging(enabled=False)
        return
    
    # Determine log level
    if log_level:
        level = log_level
    elif verbose:
        level = 'INFO'
    else:
        level = 'WARNING'  # Default: only warnings and errors
    
    LoggingConfig.configure_logging(
        enabled=True,
        level=level,
        log_file=log_file,
        file_only=file_only
    )


# Module-level convenience functions for backward compatibility
def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Logger name (typically __name__).
    
    Returns:
        Logger instance.
    """
    return logging.getLogger(name)


def configure_module_logging(level: str = 'INFO') -> logging.Logger:
    """
    Configure logging for a specific module (backward compatibility).
    
    Args:
        level: Log level for the module.
    
    Returns:
        Logger instance for the calling module.
    
    Note:
        This function is provided for backward compatibility with existing code.
        New code should use the centralized configuration via setup_application_logging.
    """
    logger = logging.getLogger()
    if not logger.handlers:
        # Only configure if no handlers exist (avoid duplicate configuration)
        LoggingConfig.configure_logging(enabled=True, level=level)
    
    return logger