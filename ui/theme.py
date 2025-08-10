"""
UI theme configuration and styling module for Rich terminal interface.

This module provides comprehensive theme configuration for the Trading Strategy Backtester
application's Rich-based terminal user interface. It includes color schemes,
style definitions, validation, and theme management functionality.

Classes:
    ThemeManager: Main class for theme management and validation
    ThemeValidationError: Custom exception for theme validation errors

Constants:
    THEME: Default theme configuration dictionary
    VALID_RICH_COLORS: List of valid Rich color names
    THEME_CATEGORIES: Theme category definitions

Example:
    >>> from ui.theme import THEME, ThemeManager
    >>> manager = ThemeManager()
    >>> validated_theme = manager.validate_theme(THEME)
    >>> custom_color = manager.get_color("primary")
"""

from typing import Dict, List, Optional, Any, Set
from enum import Enum

# Configure logging
from logger.logging_manager import get_logger
logger = get_logger(__name__)


class ThemeValidationError(Exception):
    """Exception raised when theme validation fails."""
    

    def __init__(self, message: str, theme_key: Optional[str] = None, cause: Optional[Exception] = None) -> None:
        """
        Initialize ThemeValidationError.
        
        Args:
            message: Error message describing the validation issue.
            theme_key: The theme key that caused the error (optional).
            cause: The underlying exception that caused this error (optional).
        """
        self.theme_key = theme_key
        self.cause = cause
        super().__init__(message)


class ThemeCategory(Enum):
    """Enumeration of theme categories for organization."""
    
    CORE = "core"
    STATUS = "status"
    TABLE = "table"
    PANEL = "panel"
    PROMPT = "prompt"
    TEXT = "text"


class ThemeManager:
    """
    Manager class for theme configuration, validation, and customization.
    
    This class provides methods to validate theme configurations, manage color
    schemes, and ensure consistency across the application's UI components.
    It supports theme validation, color accessibility checks, and dynamic
    theme modifications.
    
    Attributes:
        VALID_RICH_COLORS: Set of valid Rich library color names.
        VALID_RICH_STYLES: Set of valid Rich library style modifiers.
        
    Example:
        >>> manager = ThemeManager()
        >>> is_valid = manager.validate_color("bright_cyan")
        >>> theme_info = manager.get_theme_info(THEME)
    """
    
    # Valid Rich color names (comprehensive list)
    VALID_RICH_COLORS: Set[str] = {
        # Basic colors
        "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white",
        
        # Bright colors
        "bright_black", "bright_red", "bright_green", "bright_yellow",
        "bright_blue", "bright_magenta", "bright_cyan", "bright_white",
        
        # Extended colors
        "grey0", "grey3", "grey7", "grey11", "grey15", "grey19", "grey23",
        "grey27", "grey30", "grey35", "grey37", "grey39", "grey42", "grey46",
        "grey50", "grey53", "grey54", "grey58", "grey62", "grey63", "grey66",
        "grey69", "grey70", "grey74", "grey78", "grey82", "grey84", "grey85",
        "grey89", "grey93", "grey100",
        
        # Color names
        "default", "none"
    }
    
    # Valid Rich style modifiers
    VALID_RICH_STYLES: Set[str] = {
        "bold", "dim", "italic", "underline", "blink", "blink2", "reverse",
        "conceal", "strike", "underline2", "frame", "encircle", "overline"
    }
    
    # Theme category mappings
    THEME_CATEGORIES: Dict[str, List[str]] = {
        ThemeCategory.CORE.value: ["primary", "secondary", "accent"],
        ThemeCategory.STATUS.value: ["success", "error", "warning", "info"],
        ThemeCategory.TABLE.value: ["table_border", "table_style", "table_title", "table_title_secondary", "table_header"],
        ThemeCategory.PANEL.value: ["panel_border", "selected"],
        ThemeCategory.PROMPT.value: ["prompt", "title", "subtitle", "status"],
        ThemeCategory.TEXT.value: ["dim", "highlight"]
    }
    

    def __init__(self) -> None:
        """Initialize the ThemeManager."""
        logger.debug("ThemeManager initialized")
    

    def validate_theme(self, theme: Dict[str, str]) -> Dict[str, str]:
        """
        Validate a complete theme configuration.
        
        Args:
            theme: Theme dictionary to validate.
            
        Returns:
            Validated theme dictionary.
            
        Raises:
            ThemeValidationError: If theme validation fails.
            ValueError: If theme is not a dictionary.
            
        Example:
            >>> manager = ThemeManager()
            >>> validated = manager.validate_theme(THEME)
        """
        if not isinstance(theme, dict):
            raise ValueError("Theme must be a dictionary")
        
        if not theme:
            raise ThemeValidationError("Theme dictionary cannot be empty")
        
        validated_theme = {}
        validation_errors = []
        
        for key, value in theme.items():
            try:
                validated_value = self.validate_style_string(value)
                validated_theme[key] = validated_value
                logger.debug(f"Validated theme key '{key}': '{value}'")
            except ThemeValidationError as e:
                validation_errors.append(f"Key '{key}': {str(e)}")
        
        if validation_errors:
            raise ThemeValidationError(
                f"Theme validation failed: {'; '.join(validation_errors)}"
            )
        
        logger.info(f"Theme validation successful: {len(validated_theme)} keys validated")
        return validated_theme
    

    def validate_style_string(self, style: str) -> str:
        """
        Validate a Rich style string (color and modifiers).
        
        Args:
            style: Style string to validate (e.g., "bold bright_cyan").
            
        Returns:
            Validated style string.
            
        Raises:
            ThemeValidationError: If style string is invalid.
            ValueError: If style is not a string.
            
        Example:
            >>> manager = ThemeManager()
            >>> validated = manager.validate_style_string("bold bright_cyan")
        """
        if not isinstance(style, str):
            raise ValueError("Style must be a string")
        
        if not style.strip():
            raise ThemeValidationError("Style string cannot be empty")
        
        # Split style into components
        components = style.strip().split()
        
        if not components:
            raise ThemeValidationError("Style string must contain at least one component")
        
        validated_components = []
        color_found = False
        
        for component in components:
            component = component.lower().strip()
            
            if not component:
                continue
            
            # Check if it's a valid color
            if self.validate_color(component):
                if color_found:
                    raise ThemeValidationError(
                        f"Multiple colors found in style string: '{style}'"
                    )
                color_found = True
                validated_components.append(component)
            
            # Check if it's a valid style modifier
            elif component in self.VALID_RICH_STYLES:
                validated_components.append(component)
            
            # Check for hex colors (basic validation)
            elif component.startswith('#') and len(component) in [4, 7]:
                if color_found:
                    raise ThemeValidationError(
                        f"Multiple colors found in style string: '{style}'"
                    )
                color_found = True
                validated_components.append(component)
            
            # Check for RGB colors
            elif component.startswith('rgb(') and component.endswith(')'):
                if color_found:
                    raise ThemeValidationError(
                        f"Multiple colors found in style string: '{style}'"
                    )
                color_found = True
                validated_components.append(component)
            
            else:
                raise ThemeValidationError(
                    f"Invalid style component: '{component}' in style '{style}'"
                )
        
        validated_style = ' '.join(validated_components)
        logger.debug(f"Validated style string: '{style}' -> '{validated_style}'")
        return validated_style
    

    def validate_color(self, color: str) -> bool:
        """
        Validate if a color name is supported by Rich.
        
        Args:
            color: Color name to validate.
            
        Returns:
            True if color is valid, False otherwise.
            
        Example:
            >>> manager = ThemeManager()
            >>> is_valid = manager.validate_color("bright_cyan")  # True
            >>> is_invalid = manager.validate_color("invalid_color")  # False
        """
        if not isinstance(color, str):
            return False
        
        color_lower = color.lower().strip()
        
        # Check basic and extended colors
        if color_lower in self.VALID_RICH_COLORS:
            return True
        
        # Check for color numbers (color0-color255)
        if color_lower.startswith('color') and color_lower[5:].isdigit():
            color_num = int(color_lower[5:])
            return 0 <= color_num <= 255
        
        # Check for hex colors
        if color_lower.startswith('#'):
            hex_part = color_lower[1:]
            if len(hex_part) in [3, 6] and all(c in '0123456789abcdef' for c in hex_part):
                return True
        
        # Check for RGB colors (basic format validation)
        if color_lower.startswith('rgb(') and color_lower.endswith(')'):
            rgb_content = color_lower[4:-1]
            try:
                rgb_values = [int(x.strip()) for x in rgb_content.split(',')]
                return len(rgb_values) == 3 and all(0 <= v <= 255 for v in rgb_values)
            except (ValueError, TypeError):
                return False
        
        return False
    

    def get_color(self, theme_key: str, theme: Optional[Dict[str, str]] = None) -> str:
        """
        Extract the color component from a theme style string.
        
        Args:
            theme_key: Key in the theme dictionary.
            theme: Theme dictionary to use (defaults to THEME).
            
        Returns:
            Color component of the style string.
            
        Raises:
            ThemeValidationError: If theme key is not found or invalid.
            
        Example:
            >>> manager = ThemeManager()
            >>> color = manager.get_color("primary")  # Returns "bright_cyan"
        """
        if theme is None:
            theme = THEME
        
        if theme_key not in theme:
            raise ThemeValidationError(f"Theme key '{theme_key}' not found")
        
        style = theme[theme_key]
        components = style.split()
        
        # Find the color component
        for component in components:
            if self.validate_color(component):
                return component
        
        # If no color found, return the first component
        return components[0] if components else ""
    

    def get_theme_info(self, theme: Dict[str, str]) -> Dict[str, Any]:
        """
        Get comprehensive information about a theme configuration.
        
        Args:
            theme: Theme dictionary to analyze.
            
        Returns:
            Dictionary with theme analysis information.
            
        Example:
            >>> manager = ThemeManager()
            >>> info = manager.get_theme_info(THEME)
            >>> print(f"Theme has {info['total_keys']} style definitions")
        """
        try:
            info = {
                'total_keys': len(theme),
                'categories': {},
                'colors_used': set(),
                'styles_used': set(),
                'validation_status': 'unknown',
                'validation_errors': []
            }
            
            # Analyze by category
            for category, keys in self.THEME_CATEGORIES.items():
                category_info = {
                    'keys': [],
                    'missing_keys': []
                }
                
                for key in keys:
                    if key in theme:
                        category_info['keys'].append(key)
                    else:
                        category_info['missing_keys'].append(key)
                
                info['categories'][category] = category_info
            
            # Analyze colors and styles used
            for key, style in theme.items():
                try:
                    components = style.split()
                    for component in components:
                        if self.validate_color(component):
                            info['colors_used'].add(component)
                        elif component in self.VALID_RICH_STYLES:
                            info['styles_used'].add(component)
                except Exception:
                    pass
            
            # Convert sets to lists for JSON serialization
            info['colors_used'] = list(info['colors_used'])
            info['styles_used'] = list(info['styles_used'])
            
            # Validate theme
            try:
                self.validate_theme(theme)
                info['validation_status'] = 'valid'
            except ThemeValidationError as e:
                info['validation_status'] = 'invalid'
                info['validation_errors'] = [str(e)]
            
            return info
            
        except Exception as e:
            logger.error(f"Error analyzing theme: {e}")
            return {
                'total_keys': len(theme) if isinstance(theme, dict) else 0,
                'error': str(e)
            }
    
    
    def create_custom_theme(
        self,
        base_theme: Optional[Dict[str, str]] = None,
        overrides: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        Create a custom theme by overriding base theme values.
        
        Args:
            base_theme: Base theme to start with (defaults to THEME).
            overrides: Dictionary of style overrides.
            
        Returns:
            New custom theme dictionary.
            
        Raises:
            ThemeValidationError: If custom theme validation fails.
            
        Example:
            >>> manager = ThemeManager()
            >>> custom = manager.create_custom_theme(
            ...     overrides={"primary": "bold red", "success": "green"}
            ... )
        """
        if base_theme is None:
            base_theme = THEME.copy()
        else:
            base_theme = base_theme.copy()
        
        if overrides:
            # Validate overrides first
            validated_overrides = self.validate_theme(overrides)
            base_theme.update(validated_overrides)
        
        # Validate the complete custom theme
        custom_theme = self.validate_theme(base_theme)
        
        logger.info(f"Created custom theme with {len(custom_theme)} style definitions")
        return custom_theme


from dataclasses import dataclass

@dataclass
class Theme:
    # Core colors - primary application colors
    primary: str = "bold bright_cyan"
    secondary: str = "white"
    accent: str = "bold bright_blue"
    
    # Status colors - for success, error, warning, and info messages
    success: str = "bold green"
    error: str = "bold red"
    warning: str = "bold yellow"
    info: str = "dim"
    
    # Text styling
    dim: str = "dim"
    highlight: str = "bold bright_magenta"
    
    # Table and border styles - for Rich table components
    table_border: str = "grey37"
    table_style: str = "white"
    table_title: str = "bold bright_blue"
    table_title_secondary: str = "bold bright_magenta"
    table_header: str = "grey37 bold"
    
    # Panel and selection styles
    selected: str = "bold bright_cyan"
    panel_border: str = "grey37"
    
    # Status and prompt styles - for user interaction
    status: str = "bold bright_cyan"
    prompt: str = "bold bright_cyan underline"
    title: str = "bold bright_cyan underline"
    subtitle: str = "bold bright_blue"

THEME = Theme()


# Valid Rich color names for reference and validation
VALID_RICH_COLORS: List[str] = [
    # Basic colors
    "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white",
    
    # Bright colors
    "bright_black", "bright_red", "bright_green", "bright_yellow",
    "bright_blue", "bright_magenta", "bright_cyan", "bright_white",
    
    # Common grey shades
    "grey0", "grey23", "grey27", "grey30", "grey35", "grey37", "grey39",
    "grey42", "grey46", "grey50", "grey53", "grey54", "grey58", "grey62",
    "grey63", "grey66", "grey69", "grey70", "grey74", "grey78", "grey82",
    "grey84", "grey85", "grey89", "grey93", "grey100",
    
    # Special colors
    "default", "none"
]


# Theme category definitions for organization
THEME_CATEGORIES: Dict[str, List[str]] = {
    "core": ["primary", "secondary", "accent"],
    "status": ["success", "error", "warning", "info"],
    "table": ["table_border", "table_style", "table_title", "table_title_secondary", "table_header"],
    "panel": ["panel_border", "selected"],
    "prompt": ["prompt", "title", "subtitle", "status"],
    "text": ["dim", "highlight"]
}


def validate_theme_on_import() -> bool:
    """
    Validate the default theme on module import.
    
    Returns:
        True if theme is valid, False otherwise.
    """
    try:
        manager = ThemeManager()
        manager.validate_theme(THEME)
        logger.info("Default theme validation successful")
        return True
    except Exception as e:
        logger.error(f"Default theme validation failed: {e}")
        return False


# Validate the default theme on import
_theme_valid = validate_theme_on_import()

if not _theme_valid:
    logger.warning("Default theme validation failed - some UI components may not display correctly")