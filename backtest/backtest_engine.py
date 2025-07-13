"""
Moteur de backtest utilisant vectorbt pour l'évaluation des stratégies.
"""

from typing import Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
import vectorbt as vbt
from datetime import datetime
import warnings

from strategies.base_strategy import BaseStrategy


class BacktestEngine:
    """
    Moteur de backtest pour évaluer les performances des stratégies de trading.
    """
    
    def __init__(self, 
                 initial_cash: float = 10000.0,
                 commission: float = 0.001,
                 slippage: float = 0.0001):
        """
        Initialise le moteur de backtest.
        
        Args:
            initial_cash: Capital initial en USD
            commission: Commission par transaction (0.001 = 0.1%)
            slippage: Slippage par transaction (0.0001 = 0.01%)
        """
        self.initial_cash = initial_cash
        self.commission = commission
        self.slippage = slippage
        self.results = None
        
    def run_backtest(self, 
                    strategy: BaseStrategy, 
                    data: pd.DataFrame,
                    start_date: Optional[str] = None,
                    end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Exécute un backtest pour une stratégie donnée.
        
        Args:
            strategy: Instance de la stratégie à tester
            data: DataFrame avec les données OHLCV
            start_date: Date de début (format 'YYYY-MM-DD')
            end_date: Date de fin (format 'YYYY-MM-DD')
            
        Returns:
            Dictionnaire contenant les résultats du backtest
        """
        # Filtrage des données par date si spécifié
        if start_date or end_date:
            data = self._filter_data_by_date(data, start_date, end_date)
        
        if len(data) < 100:
            warnings.warn("Données insuffisantes pour un backtest fiable (< 100 points)")
        
        # Génération des signaux
        try:
            buy_signals, sell_signals = strategy.generate_signals(data)
        except Exception as e:
            raise RuntimeError(f"Erreur lors de la génération des signaux: {e}")
        
        # Nettoyage des signaux (suppression des NaN)
        buy_signals = buy_signals.fillna(False)
        sell_signals = sell_signals.fillna(False)
        
        # Création du portfolio avec vectorbt
        portfolio = self._create_portfolio(data, buy_signals, sell_signals)
        
        # Calcul des métriques de performance
        metrics = self._calculate_metrics(portfolio, data)
        
        # Stockage des résultats
        self.results = {
            'strategy': strategy.to_dict(),
            'portfolio': portfolio,
            'metrics': metrics,
            'data': data,
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'backtest_period': {
                'start': data.index[0].strftime('%Y-%m-%d'),
                'end': data.index[-1].strftime('%Y-%m-%d'),
                'duration_days': (data.index[-1] - data.index[0]).days
            },
            'parameters': {
                'initial_cash': self.initial_cash,
                'commission': self.commission,
                'slippage': self.slippage
            }
        }
        
        return self.results
    
    def _filter_data_by_date(self, 
                           data: pd.DataFrame, 
                           start_date: Optional[str], 
                           end_date: Optional[str]) -> pd.DataFrame:
        """
        Filtre les données par plage de dates.
        
        Args:
            data: DataFrame à filtrer
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            DataFrame filtré
        """
        if start_date:
            data = data[data.index >= start_date]
        if end_date:
            data = data[data.index <= end_date]
        return data
    
    def _create_portfolio(self, 
                         data: pd.DataFrame, 
                         buy_signals: pd.Series, 
                         sell_signals: pd.Series) -> vbt.Portfolio:
        """
        Crée un portfolio vectorbt à partir des signaux.
        
        Args:
            data: Données de prix
            buy_signals: Signaux d'achat
            sell_signals: Signaux de vente
            
        Returns:
            Portfolio vectorbt
        """
        # Conversion des signaux booléens en entrées/sorties
        entries = buy_signals
        exits = sell_signals
        
        # Création du portfolio avec vectorbt
        portfolio = vbt.Portfolio.from_signals(
            close=data['Close'],
            entries=entries,
            exits=exits,
            init_cash=self.initial_cash,
            fees=self.commission,
            slippage=self.slippage,
            freq='1D'  # Fréquence journalière par défaut
        )
        
        return portfolio
    
    def _calculate_metrics(self, 
                          portfolio: vbt.Portfolio, 
                          data: pd.DataFrame) -> Dict[str, float]:
        """
        Calcule les métriques de performance du portfolio.
        
        Args:
            portfolio: Portfolio vectorbt
            data: Données originales
            
        Returns:
            Dictionnaire des métriques
        """
        try:
            # Métriques de base
            total_return = portfolio.total_return()
            sharpe_ratio = portfolio.sharpe_ratio()
            max_drawdown = portfolio.max_drawdown()
            win_rate = portfolio.trades.win_rate()
            
            # Métriques supplémentaires
            total_trades = portfolio.trades.count()
            avg_trade_duration = portfolio.trades.duration.mean() if total_trades > 0 else 0
            profit_factor = portfolio.trades.profit_factor() if total_trades > 0 else 0
            
            # Benchmark (Buy & Hold)
            buy_hold_return = (data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1
            
            return {
                'total_return': float(total_return) if not pd.isna(total_return) else 0.0,
                'sharpe_ratio': float(sharpe_ratio) if not pd.isna(sharpe_ratio) else 0.0,
                'max_drawdown': float(max_drawdown) if not pd.isna(max_drawdown) else 0.0,
                'win_rate': float(win_rate) if not pd.isna(win_rate) else 0.0,
                'total_trades': int(total_trades),
                'avg_trade_duration': float(avg_trade_duration) if not pd.isna(avg_trade_duration) else 0.0,
                'profit_factor': float(profit_factor) if not pd.isna(profit_factor) else 0.0,
                'buy_hold_return': float(buy_hold_return),
                'final_value': float(portfolio.value().iloc[-1]),
                'alpha': float(total_return - buy_hold_return) if not pd.isna(total_return) else 0.0
            }
        except Exception as e:
            print(f"Erreur lors du calcul des métriques: {e}")
            return {
                'total_return': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'win_rate': 0.0,
                'total_trades': 0,
                'avg_trade_duration': 0.0,
                'profit_factor': 0.0,
                'buy_hold_return': 0.0,
                'final_value': self.initial_cash,
                'alpha': 0.0
            }
    
    def get_last_results(self) -> Optional[Dict[str, Any]]:
        """
        Retourne les résultats du dernier backtest.
        
        Returns:
            Dictionnaire des résultats ou None
        """
        return self.results