#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitaire de traduction des abréviations de période de temps.
Convertit les abréviations pour l'affichage.
"""

from typing import Dict, List


class PeriodTranslator:
    """
    Classe pour traduire les abréviations de période de temps.
    """
    
    # Mapping des abréviations de périodes
    PERIOD_TRANSLATIONS: Dict[str, str] = {
        '1d': '1 jour',
        '5d': '5 jours', 
        '1mo': '1 mois',
        '3mo': '3 mois',
        '6mo': '6 mois',
        '1y': '1 an',
        '2y': '2 ans',
        '5y': '5 ans',
        '10y': '10 ans',
        'ytd': 'depuis début d\'année',
        'max': 'maximum'
    }
    
    @classmethod
    def translate_period(cls, period: str) -> str:
        """
        Traduit une abréviation de période.
        
        Args:
            period: Abréviation de période (ex: "1y", "1mo")
            
        Returns:
            Période traduite (ex: "1 an", "1 mois")
        """
        return cls.PERIOD_TRANSLATIONS.get(period.lower(), period)
    
    @classmethod
    def translate_period_list(cls, periods: List[str]) -> List[str]:
        """
        Traduit une liste d'abréviations de périodes.
        
        Args:
            periods: Liste d'abréviations de périodes
            
        Returns:
            Liste des abréviations de période traduites
        """
        return [cls.translate_period(period) for period in periods]
    
    @classmethod
    def get_available_periods(cls) -> str:
        """
        Retourne la liste des périodes disponibles.
        
        Returns:
            Chaîne formatée des périodes disponibles
        """
        period_codes = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
        period_translations = cls.translate_period_list(period_codes)
        
        # Créer une chaîne avec les traductions
        period_pairs = []
        for eng, fr in zip(period_codes, period_translations):
            period_pairs.append(f"{eng} ({fr})")
        
        return ", ".join(period_pairs)
    
    @classmethod
    def get_period_description(cls, period: str) -> str:
        """
        Retourne une description complète de la période.
        
        Args:
            period: Abréviation de période en anglais
            
        Returns:
            Description de la période avec abréviation et traduction
        """
        translation = cls.translate_period(period)
        if translation != period:
            return f"{period} ({translation})"
        return period