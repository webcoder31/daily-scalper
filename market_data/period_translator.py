"""
Time period abbreviation translation utilities for market data periods.

This module provides the PeriodTranslator class for translating time period
abbreviations used by financial data providers (like Yahoo Finance) into
human-readable descriptions. It includes validation and comprehensive
error handling.

Classes:
    PeriodTranslator: Main class for period translation and validation
    PeriodValidationError: Custom exception for period validation errors

Example:
    >>> from utils.period_translator import PeriodTranslator
    >>> translator = PeriodTranslator()
    >>> description = translator.translate_period("1y")
    >>> print(description)  # "1 year"
    >>> periods = translator.get_available_periods()
"""

from typing import Dict, List, Optional, Union, Tuple
import logging

# Configure logging
from logging.logging_manager import get_logger
logger = get_logger(__name__)


class PeriodValidationError(Exception):
    """Exception raised when period validation fails."""
    

    def __init__(self, message: str, period: Optional[str] = None, valid_periods: Optional[List[str]] = None) -> None:
        """
        Initialize PeriodValidationError.
        
        Args:
            message: Error message describing the validation issue.
            period: The invalid period that caused the error (optional).
            valid_periods: List of valid periods for reference (optional).
        """
        self.period = period
        self.valid_periods = valid_periods or []
        super().__init__(message)


class PeriodTranslator:
    """
    Class for translating time period abbreviations to human-readable descriptions.
    
    This class provides methods to translate period abbreviations used by financial
    data providers into descriptive text, validate period strings, and provide
    information about available periods.
    
    The class supports all standard Yahoo Finance period abbreviations and provides
    comprehensive validation and error handling.
    
    Attributes:
        PERIOD_TRANSLATIONS: Dictionary mapping period abbreviations to descriptions.
        
    Example:
        >>> translator = PeriodTranslator()
        >>> print(translator.translate_period("1mo"))  # "1 month"
        >>> print(translator.is_valid_period("5y"))    # True
        >>> periods = translator.get_available_periods_list()
    """
    
    # Comprehensive mapping of period abbreviations to human-readable descriptions
    PERIOD_TRANSLATIONS: Dict[str, str] = {
        '1d': '1 day',
        '5d': '5 days',
        '1mo': '1 month',
        '3mo': '3 months',
        '6mo': '6 months',
        '1y': '1 year',
        '2y': '2 years',
        '5y': '5 years',
        '10y': '10 years',
        'ytd': 'year to date',
        'max': 'maximum available'
    }
    
    # Alternative period formats that should be normalized
    PERIOD_ALIASES: Dict[str, str] = {
        '1day': '1d',
        '5days': '5d',
        '1month': '1mo',
        '3months': '3mo',
        '6months': '6mo',
        '1year': '1y',
        '2years': '2y',
        '5years': '5y',
        '10years': '10y',
        'year_to_date': 'ytd',
        'maximum': 'max'
    }
    

    @classmethod
    def translate_period(cls, period: str, validate: bool = True) -> str:
        """
        Translate a period abbreviation to human-readable description.
        
        Args:
            period: Period abbreviation (e.g., "1y", "1mo", "5d").
            validate: Whether to validate the period before translation.
            
        Returns:
            Human-readable period description (e.g., "1 year", "1 month", "5 days").
            
        Raises:
            PeriodValidationError: If period is invalid and validate=True.
            ValueError: If period is not a string.
            
        Example:
            >>> PeriodTranslator.translate_period("1y")
            '1 year'
            >>> PeriodTranslator.translate_period("invalid", validate=False)
            'invalid'
        """
        if not isinstance(period, str):
            raise ValueError("Period must be a string")
        
        # Normalize the period (handle case and aliases)
        normalized_period = cls._normalize_period(period)
        
        # Validate if requested
        if validate and not cls.is_valid_period(normalized_period):
            raise PeriodValidationError(
                f"Invalid period '{period}'. Valid periods: {', '.join(cls.get_available_periods_list())}",
                period=period,
                valid_periods=cls.get_available_periods_list()
            )
        
        # Return translation or original if not found
        translation = cls.PERIOD_TRANSLATIONS.get(normalized_period, period)
        logger.debug(f"Translated period '{period}' -> '{translation}'")
        return translation
    

    @classmethod
    def translate_period_list(cls, periods: List[str], validate: bool = True) -> List[str]:
        """
        Translate a list of period abbreviations to human-readable descriptions.
        
        Args:
            periods: List of period abbreviations to translate.
            validate: Whether to validate each period before translation.
            
        Returns:
            List of translated period descriptions.
            
        Raises:
            PeriodValidationError: If any period is invalid and validate=True.
            ValueError: If periods is not a list or contains non-strings.
            
        Example:
            >>> PeriodTranslator.translate_period_list(["1d", "1mo", "1y"])
            ['1 day', '1 month', '1 year']
        """
        if not isinstance(periods, list):
            raise ValueError("Periods must be a list")
        
        if not all(isinstance(p, str) for p in periods):
            raise ValueError("All periods must be strings")
        
        return [cls.translate_period(period, validate=validate) for period in periods]
    

    @classmethod
    def is_valid_period(cls, period: str) -> bool:
        """
        Check if a period abbreviation is valid.
        
        Args:
            period: Period abbreviation to validate.
            
        Returns:
            True if the period is valid, False otherwise.
            
        Example:
            >>> PeriodTranslator.is_valid_period("1y")
            True
            >>> PeriodTranslator.is_valid_period("invalid")
            False
        """
        if not isinstance(period, str):
            return False
        
        normalized_period = cls._normalize_period(period)
        return normalized_period in cls.PERIOD_TRANSLATIONS
    

    @classmethod
    def validate_period(cls, period: str) -> str:
        """
        Validate and normalize a period abbreviation.
        
        Args:
            period: Period abbreviation to validate and normalize.
            
        Returns:
            Normalized period abbreviation.
            
        Raises:
            PeriodValidationError: If the period is invalid.
            ValueError: If period is not a string.
            
        Example:
            >>> PeriodTranslator.validate_period("1YEAR")
            '1y'
        """
        if not isinstance(period, str):
            raise ValueError("Period must be a string")
        
        normalized_period = cls._normalize_period(period)
        
        if not cls.is_valid_period(normalized_period):
            raise PeriodValidationError(
                f"Invalid period '{period}'. Valid periods: {', '.join(cls.get_available_periods_list())}",
                period=period,
                valid_periods=cls.get_available_periods_list()
            )
        
        return normalized_period
    

    @classmethod
    def _normalize_period(cls, period: str) -> str:
        """
        Normalize a period string by handling case and aliases.
        
        Args:
            period: Period string to normalize.
            
        Returns:
            Normalized period string.
        """
        # Convert to lowercase and strip whitespace
        normalized = period.lower().strip()
        
        # Check for aliases
        if normalized in cls.PERIOD_ALIASES:
            normalized = cls.PERIOD_ALIASES[normalized]
        
        return normalized
    

    @classmethod
    def get_available_periods_list(cls) -> List[str]:
        """
        Get a list of all available period abbreviations.
        
        Returns:
            List of valid period abbreviations sorted by typical usage.
            
        Example:
            >>> periods = PeriodTranslator.get_available_periods_list()
            >>> print(periods)
            ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
        """
        # Return periods in logical order (shortest to longest, then special cases)
        return ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
    

    @classmethod
    def get_available_periods(cls) -> str:
        """
        Get a formatted string of all available periods with their descriptions.
        
        Returns:
            Formatted string showing period codes and their descriptions.
            
        Example:
            >>> periods_str = PeriodTranslator.get_available_periods()
            >>> print(periods_str)
            '1d (1 day), 5d (5 days), 1mo (1 month), ...'
        """
        period_codes = cls.get_available_periods_list()
        period_translations = cls.translate_period_list(period_codes, validate=False)
        
        # Create formatted pairs
        period_pairs = [
            f"{code} ({translation})" 
            for code, translation in zip(period_codes, period_translations)
        ]
        
        return ", ".join(period_pairs)
    

    @classmethod
    def get_period_description(cls, period: str, validate: bool = True) -> str:
        """
        Get a complete description of a period with both code and translation.
        
        Args:
            period: Period abbreviation to describe.
            validate: Whether to validate the period.
            
        Returns:
            Complete period description in format "code (description)".
            
        Raises:
            PeriodValidationError: If period is invalid and validate=True.
            ValueError: If period is not a string.
            
        Example:
            >>> PeriodTranslator.get_period_description("1y")
            '1y (1 year)'
        """
        if not isinstance(period, str):
            raise ValueError("Period must be a string")
        
        normalized_period = cls._normalize_period(period)
        translation = cls.translate_period(normalized_period, validate=validate)
        
        # If translation is different from the normalized period, show both
        if translation != normalized_period:
            return f"{normalized_period} ({translation})"
        
        # If they're the same, just return the period (likely invalid)
        return normalized_period
    

    @classmethod
    def get_period_info(cls, period: str) -> Dict[str, Union[str, bool, List[str]]]:
        """
        Get comprehensive information about a period.
        
        Args:
            period: Period abbreviation to get information about.
            
        Returns:
            Dictionary with period information including validity, translation, etc.
            
        Example:
            >>> info = PeriodTranslator.get_period_info("1y")
            >>> print(info)
            {
                'original': '1y',
                'normalized': '1y',
                'is_valid': True,
                'translation': '1 year',
                'description': '1y (1 year)'
            }
        """
        try:
            normalized = cls._normalize_period(period) if isinstance(period, str) else period
            is_valid = cls.is_valid_period(period) if isinstance(period, str) else False
            
            return {
                'original': period,
                'normalized': normalized,
                'is_valid': is_valid,
                'translation': cls.translate_period(period, validate=False) if isinstance(period, str) else 'N/A',
                'description': cls.get_period_description(period, validate=False) if isinstance(period, str) else 'N/A',
                'valid_periods': cls.get_available_periods_list()
            }
        except Exception as e:
            return {
                'original': period,
                'normalized': 'N/A',
                'is_valid': False,
                'translation': 'N/A',
                'description': 'N/A',
                'error': str(e),
                'valid_periods': cls.get_available_periods_list()
            }
    
    
    @classmethod
    def suggest_similar_periods(cls, invalid_period: str, max_suggestions: int = 3) -> List[Tuple[str, str]]:
        """
        Suggest similar valid periods for an invalid period input.
        
        Args:
            invalid_period: The invalid period string.
            max_suggestions: Maximum number of suggestions to return.
            
        Returns:
            List of tuples (period_code, description) for similar valid periods.
            
        Example:
            >>> suggestions = PeriodTranslator.suggest_similar_periods("1yr")
            >>> print(suggestions)
            [('1y', '1 year'), ('2y', '2 years')]
        """
        if not isinstance(invalid_period, str):
            return []
        
        invalid_lower = invalid_period.lower().strip()
        suggestions = []
        
        # Look for partial matches in period codes
        for period_code in cls.get_available_periods_list():
            if (invalid_lower in period_code or 
                period_code in invalid_lower or
                any(char in period_code for char in invalid_lower if char.isalnum())):
                
                translation = cls.translate_period(period_code, validate=False)
                suggestions.append((period_code, translation))
        
        # Look for partial matches in translations
        if len(suggestions) < max_suggestions:
            for period_code, translation in cls.PERIOD_TRANSLATIONS.items():
                if period_code not in [s[0] for s in suggestions]:
                    if (invalid_lower in translation.lower() or 
                        any(word in translation.lower() for word in invalid_lower.split())):
                        suggestions.append((period_code, translation))
        
        return suggestions[:max_suggestions]