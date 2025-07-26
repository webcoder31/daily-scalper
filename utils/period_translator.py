#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Time period abbreviation translation utility.
Converts abbreviations for display.
"""

from typing import Dict, List


class PeriodTranslator:
    """
    Class for translating time period abbreviations.
    """
    
    # Mapping of period abbreviations
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
        'max': 'maximum'
    }
    
    @classmethod
    def translate_period(cls, period: str) -> str:
        """
        Translates a period abbreviation.
        
        Args:
            period: Period abbreviation (e.g.: "1y", "1mo")
            
        Returns:
            Translated period (e.g.: "1 year", "1 month")
        """
        return cls.PERIOD_TRANSLATIONS.get(period.lower(), period)
    
    @classmethod
    def translate_period_list(cls, periods: List[str]) -> List[str]:
        """
        Translates a list of period abbreviations.
        
        Args:
            periods: List of period abbreviations
            
        Returns:
            List of translated period abbreviations
        """
        return [cls.translate_period(period) for period in periods]
    
    @classmethod
    def get_available_periods(cls) -> str:
        """
        Returns the list of available periods.
        
        Returns:
            Formatted string of available periods
        """
        period_codes = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
        period_translations = cls.translate_period_list(period_codes)
        
        # Create a string with translations
        period_pairs = []
        for eng, fr in zip(period_codes, period_translations):
            period_pairs.append(f"{eng} ({fr})")
        
        return ", ".join(period_pairs)
    
    @classmethod
    def get_period_description(cls, period: str) -> str:
        """
        Returns a complete description of the period.
        
        Args:
            period: English period abbreviation
            
        Returns:
            Period description with abbreviation and translation
        """
        translation = cls.translate_period(period)
        if translation != period:
            return f"{period} ({translation})"
        return period