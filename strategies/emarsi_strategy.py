"""
EMA + RSI Filter Strategy
"""

from typing import Dict, Any, Tuple, List
from itertools import product
import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy
from .strategy_registry import register_strategy


@register_strategy
class EMARSIStrategy(BaseStrategy):
    """
    Strategy combining EMA crossover with RSI filter.
    
    Buy signal: EMA fast crosses above EMA slow AND RSI > threshold
    Sell signal: EMA fast crosses below EMA slow OR RSI < exit threshold
    """
    
    @classmethod
    def get_parameter_definitions(cls) -> Dict[str, Dict[str, Any]]:
        return {
            'ema_fast': {
                'type': int,
                'default': 10,
                'range': (5, 50),
                'description': 'Period for fast EMA'
            },
            'ema_slow': {
                'type': int,
                'default': 30,
                'range': (10, 200),
                'description': 'Period for slow EMA'
            },
            'rsi_period': {
                'type': int,
                'default': 14,
                'range': (5, 50),
                'description': 'Period for RSI calculation'
            },
            'rsi_entry': {
                'type': float,
                'default': 50,
                'range': (40, 60),
                'description': 'Minimum RSI to allow buy signal'
            },
            'rsi_exit': {
                'type': float,
                'default': 40,
                'range': (30, 50),
                'description': 'Maximum RSI before forcing sell signal'
            }
        }
    
    def __init__(self, ema_fast=10, ema_slow=30, rsi_period=14, rsi_entry=50.0, rsi_exit=40.0, **kwargs):
        parameters = {
            'ema_fast': ema_fast,
            'ema_slow': ema_slow,
            'rsi_period': rsi_period,
            'rsi_entry': rsi_entry,
            'rsi_exit': rsi_exit,
            **kwargs
        }
        super().__init__(self.get_label(), parameters)
        
        if ema_fast >= ema_slow:
            raise ValueError("Fast EMA must be shorter than slow EMA.")
    
    def generate_signals(self, data: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        if not self.validate_data(data):
            raise ValueError("Invalid data: OHLCV columns required")
        
        p = self.parameters
        close = data['Close']
        
        ema_fast = close.ewm(span=p['ema_fast'], adjust=False).mean()
        ema_slow = close.ewm(span=p['ema_slow'], adjust=False).mean()
        
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(p['rsi_period']).mean()
        avg_loss = loss.rolling(p['rsi_period']).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        crossover_up = (ema_fast > ema_slow) & (ema_fast.shift(1) <= ema_slow.shift(1))
        crossover_down = (ema_fast < ema_slow) & (ema_fast.shift(1) >= ema_slow.shift(1))
        
        buy_signals = crossover_up & (rsi > p['rsi_entry'])
        sell_signals = crossover_down | (rsi < p['rsi_exit'])
        
        self.indicators = {
            'ema_fast': ema_fast,
            'ema_slow': ema_slow,
            'rsi': rsi
        }
        
        return buy_signals, sell_signals

    def get_explanation(self) -> str:
        p = self.parameters
        return (
            f"EMA+RSI Strategy:\n"
            f"- Buy: EMA{p['ema_fast']} crosses above EMA{p['ema_slow']} and RSI > {p['rsi_entry']}\n"
            f"- Sell: EMA{p['ema_fast']} crosses below EMA{p['ema_slow']} or RSI < {p['rsi_exit']}"
        )
    
    @classmethod
    def get_label(cls) -> str:
        return "EMA + RSI Strategy"

    @classmethod
    def get_short_label(cls) -> str:
        return "EMA+RSI"

    @classmethod
    def get_short_description(cls, config: Dict[str, Any] = None) -> str:
        if config:
            return (
                f"EMA{config['ema_fast']}/{config['ema_slow']} + RSI({config['rsi_period']}), "
                f"entry>{config['rsi_entry']}, exit<{config['rsi_exit']}"
            )
        return cls.get_short_label()

    # @classmethod
    # def get_predefined_configurations(cls) -> List[Dict[str, Any]]:
    #     return [
    #         {'ema_fast': 10, 'ema_slow': 30, 'rsi_period': 14, 'rsi_entry': 50, 'rsi_exit': 40},
    #         {'ema_fast': 20, 'ema_slow': 50, 'rsi_period': 14, 'rsi_entry': 55, 'rsi_exit': 45},
    #         {'ema_fast': 8, 'ema_slow': 21, 'rsi_period': 10, 'rsi_entry': 52, 'rsi_exit': 42}
    #     ]

    @classmethod
    def get_predefined_configurations(cls) -> List[Dict[str, Any]]:
        # Définir la grille autour de la config optimale trouvée
        ema_fast_range = [8, 10, 12]
        ema_slow_range = [25, 30, 35]
        rsi_period_range = [14]  # On peut l’élargir à [12, 14, 16] si tu veux
        rsi_entry_range = [40, 42, 44]
        rsi_exit_range = [28, 30, 32]

        # Produit cartésien de tous les paramètres
        grid = product(
            ema_fast_range,
            ema_slow_range,
            rsi_period_range,
            rsi_entry_range,
            rsi_exit_range,
        )

        # Générer toutes les combinaisons en dictionnaire
        return [
            {
                'ema_fast': ema_fast,
                'ema_slow': ema_slow,
                'rsi_period': rsi_period,
                'rsi_entry': rsi_entry,
                'rsi_exit': rsi_exit
            }
            for ema_fast, ema_slow, rsi_period, rsi_entry, rsi_exit in grid
            if ema_fast < ema_slow and rsi_exit < rsi_entry  # Filtrer les configs incohérentes
        ]

    def get_indicators(self) -> Dict[str, pd.Series]:
        return getattr(self, 'indicators', {})
