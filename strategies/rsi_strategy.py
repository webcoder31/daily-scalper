"""
Stratégie RSI (Relative Strength Index) - Exemple d'extension.
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy


class RSIStrategy(BaseStrategy):
    """
    Stratégie basée sur l'indicateur RSI (Relative Strength Index).
    
    Signal d'achat: RSI < seuil_bas (survente)
    Signal de vente: RSI > seuil_haut (surachat)
    """
    
    def __init__(self, 
                 period: int = 14, 
                 oversold_threshold: float = 30, 
                 overbought_threshold: float = 70,
                 **kwargs):
        """
        Initialise la stratégie RSI.
        
        Args:
            period: Période pour le calcul du RSI
            oversold_threshold: Seuil de survente (signal d'achat)
            overbought_threshold: Seuil de surachat (signal de vente)
            **kwargs: Paramètres supplémentaires
        """
        parameters = {
            'period': period,
            'oversold_threshold': oversold_threshold,
            'overbought_threshold': overbought_threshold,
            **kwargs
        }
        super().__init__('RSI Strategy', parameters)
        
        # Validation des paramètres
        if not (0 < oversold_threshold < overbought_threshold < 100):
            raise ValueError("Les seuils doivent respecter: 0 < oversold < overbought < 100")
        if period < 2:
            raise ValueError("La période doit être supérieure à 1")
    
    def generate_signals(self, data: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """
        Génère les signaux d'achat et de vente basés sur le RSI.
        
        Args:
            data: DataFrame avec les données OHLCV
            
        Returns:
            Tuple contenant les signaux d'entrée et de sortie
        """
        if not self.validate_data(data):
            raise ValueError("Données invalides: colonnes OHLCV requises")
        
        period = self.parameters['period']
        oversold = self.parameters['oversold_threshold']
        overbought = self.parameters['overbought_threshold']
        
        # Calcul du RSI
        rsi = self._calculate_rsi(data['Close'], period)
        
        # Signaux basés sur les seuils
        # Signal d'achat: RSI passe en-dessous du seuil de survente
        buy_signals = (rsi < oversold) & (rsi.shift(1) >= oversold)
        
        # Signal de vente: RSI passe au-dessus du seuil de surachat
        sell_signals = (rsi > overbought) & (rsi.shift(1) <= overbought)
        
        # Stockage des indicateurs pour visualisation
        self.indicators = {
            'rsi': rsi,
            'oversold_line': pd.Series(oversold, index=data.index),
            'overbought_line': pd.Series(overbought, index=data.index)
        }
        
        return buy_signals, sell_signals
    
    def _calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """
        Calcule l'indicateur RSI.
        
        Args:
            prices: Série des prix de clôture
            period: Période pour le calcul
            
        Returns:
            Série du RSI
        """
        # Calcul des variations de prix
        delta = prices.diff()
        
        # Séparation des gains et pertes
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        
        # Moyennes mobiles exponentielles des gains et pertes
        avg_gains = gains.ewm(span=period, adjust=False).mean()
        avg_losses = losses.ewm(span=period, adjust=False).mean()
        
        # Calcul du RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def get_description(self) -> str:
        """
        Retourne une description de la stratégie.
        
        Returns:
            Description de la stratégie RSI
        """
        period = self.parameters['period']
        oversold = self.parameters['oversold_threshold']
        overbought = self.parameters['overbought_threshold']
        
        return (f"Stratégie RSI avec période {period}. "
                f"Achat quand RSI < {oversold} (survente), "
                f"vente quand RSI > {overbought} (surachat).")
    
    def get_indicators(self) -> Dict[str, pd.Series]:
        """
        Retourne les indicateurs calculés pour la visualisation.
        
        Returns:
            Dictionnaire des indicateurs techniques
        """
        return getattr(self, 'indicators', {})