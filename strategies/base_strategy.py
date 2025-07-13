"""
Classe de base pour toutes les stratégies de trading.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np


class BaseStrategy(ABC):
    """
    Classe abstraite de base pour toutes les stratégies de trading.
    
    Toutes les stratégies doivent hériter de cette classe et implémenter
    les méthodes abstraites requises.
    """
    
    def __init__(self, name: str, parameters: Dict[str, Any] = None):
        """
        Initialise la stratégie de base.
        
        Args:
            name: Nom de la stratégie
            parameters: Paramètres de configuration de la stratégie
        """
        self.name = name
        self.parameters = parameters or {}
        self.results = None
        
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """
        Génère les signaux d'achat et de vente basés sur les données.
        
        Args:
            data: DataFrame avec les données OHLCV
            
        Returns:
            Tuple contenant les signaux d'entrée et de sortie (buy_signals, sell_signals)
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Retourne une description de la stratégie.
        
        Returns:
            Description textuelle de la stratégie
        """
        pass
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Valide que les données contiennent les colonnes requises.
        
        Args:
            data: DataFrame à valider
            
        Returns:
            True si les données sont valides, False sinon
        """
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        return all(col in data.columns for col in required_columns)
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Retourne les paramètres de la stratégie.
        
        Returns:
            Dictionnaire des paramètres
        """
        return self.parameters.copy()
    
    def set_parameters(self, parameters: Dict[str, Any]) -> None:
        """
        Met à jour les paramètres de la stratégie.
        
        Args:
            parameters: Nouveaux paramètres
        """
        self.parameters.update(parameters)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit la stratégie en dictionnaire pour la sauvegarde.
        
        Returns:
            Dictionnaire représentant la stratégie
        """
        return {
            'name': self.name,
            'class': self.__class__.__name__,
            'parameters': self.parameters,
            'description': self.get_description()
        }