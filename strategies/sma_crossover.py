"""
Stratégie de croisement de moyennes mobiles simples (SMA Crossover).
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy


class SMACrossoverStrategy(BaseStrategy):
    """
    Stratégie basée sur le croisement de deux moyennes mobiles simples.
    
    Signal d'achat: quand la SMA courte croise au-dessus de la SMA longue
    Signal de vente: quand la SMA courte croise en-dessous de la SMA longue
    """
    
    def __init__(self, short_window: int = 20, long_window: int = 50, **kwargs):
        """
        Initialise la stratégie SMA Crossover.
        
        Args:
            short_window: Période pour la moyenne mobile courte
            long_window: Période pour la moyenne mobile longue
            **kwargs: Paramètres supplémentaires
        """
        parameters = {
            'short_window': short_window,
            'long_window': long_window,
            **kwargs
        }
        super().__init__('SMA Crossover', parameters)
        
        # Validation des paramètres
        if short_window >= long_window:
            raise ValueError("La période courte doit être inférieure à la période longue")
        if short_window < 1 or long_window < 1:
            raise ValueError("Les périodes doivent être positives")
    
    def generate_signals(self, data: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """
        Génère les signaux d'achat et de vente basés sur le croisement des SMA.
        
        Args:
            data: DataFrame avec les données OHLCV
            
        Returns:
            Tuple contenant les signaux d'entrée et de sortie
        """
        if not self.validate_data(data):
            raise ValueError("Données invalides: colonnes OHLCV requises")
        
        short_window = self.parameters['short_window']
        long_window = self.parameters['long_window']
        
        # Calcul des moyennes mobiles
        sma_short = data['Close'].rolling(window=short_window).mean()
        sma_long = data['Close'].rolling(window=long_window).mean()
        
        # Signaux de croisement
        # Signal d'achat: SMA courte croise au-dessus de SMA longue
        buy_signals = (sma_short > sma_long) & (sma_short.shift(1) <= sma_long.shift(1))
        
        # Signal de vente: SMA courte croise en-dessous de SMA longue
        sell_signals = (sma_short < sma_long) & (sma_short.shift(1) >= sma_long.shift(1))
        
        # Stockage des indicateurs pour visualisation
        self.indicators = {
            'sma_short': sma_short,
            'sma_long': sma_long
        }
        
        return buy_signals, sell_signals
    
    def get_description(self) -> str:
        """
        Retourne une description de la stratégie.
        
        Returns:
            Description de la stratégie SMA Crossover
        """
        short_window = self.parameters['short_window']
        long_window = self.parameters['long_window']
        
        return (f"Stratégie de croisement de moyennes mobiles simples "
                f"(SMA {short_window} / SMA {long_window}).\n"
                f"Achat quand SMA{short_window} > SMA{long_window}, "
                f"vente quand SMA{short_window} < SMA{long_window}.")
    
    def get_indicators(self) -> Dict[str, pd.Series]:
        """
        Retourne les indicateurs calculés pour la visualisation.
        
        Returns:
            Dictionnaire des indicateurs techniques
        """
        return getattr(self, 'indicators', {})