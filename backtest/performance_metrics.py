"""
Classe pour calculer et analyser les métriques de performance.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np
from datetime import datetime


class PerformanceMetrics:
    """
    Classe pour analyser et comparer les performances des stratégies.
    """
    
    @staticmethod
    def calculate_advanced_metrics(results: Dict[str, Any]) -> Dict[str, float]:
        """
        Calcule des métriques avancées à partir des résultats de backtest.
        
        Args:
            results: Résultats du backtest
            
        Returns:
            Dictionnaire des métriques avancées
        """
        portfolio = results['portfolio']
        metrics = results['metrics'].copy()
        
        try:
            # Calculs supplémentaires
            returns = portfolio.returns()
            
            # Volatilité annualisée
            volatility = returns.std() * np.sqrt(252)
            
            # Ratio de Calmar (rendement annualisé / max drawdown)
            calmar_ratio = (metrics['total_return'] * 252 / len(returns)) / abs(metrics['max_drawdown']) if metrics['max_drawdown'] != 0 else 0
            
            # Ratio de Sortino
            downside_returns = returns[returns < 0]
            downside_deviation = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
            sortino_ratio = (metrics['total_return'] * 252 / len(returns)) / downside_deviation if downside_deviation != 0 else 0
            
            # VaR (Value at Risk) à 95%
            var_95 = np.percentile(returns, 5) if len(returns) > 0 else 0
            
            metrics.update({
                'volatility': float(volatility) if not pd.isna(volatility) else 0.0,
                'calmar_ratio': float(calmar_ratio) if not pd.isna(calmar_ratio) else 0.0,
                'sortino_ratio': float(sortino_ratio) if not pd.isna(sortino_ratio) else 0.0,
                'var_95': float(var_95) if not pd.isna(var_95) else 0.0,
            })
            
        except Exception as e:
            print(f"Erreur lors du calcul des métriques avancées: {e}")
        
        return metrics
    
    @staticmethod
    def is_strategy_profitable(metrics: Dict[str, float], 
                             min_return: float = 0.1,
                             min_sharpe: float = 1.0,
                             max_drawdown: float = 0.2) -> bool:
        """
        Détermine si une stratégie est considérée comme profitable.
        
        Args:
            metrics: Métriques de performance
            min_return: Rendement minimum requis
            min_sharpe: Ratio de Sharpe minimum
            max_drawdown: Drawdown maximum acceptable
            
        Returns:
            True si la stratégie est profitable, False sinon
        """
        return (
            metrics.get('total_return', 0) >= min_return and
            metrics.get('sharpe_ratio', 0) >= min_sharpe and
            abs(metrics.get('max_drawdown', 1)) <= max_drawdown and
            metrics.get('total_trades', 0) >= 5  # Minimum de trades pour la fiabilité
        )
    
    @staticmethod
    def rank_strategies(strategies_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Classe les stratégies par performance.
        
        Args:
            strategies_results: Liste des résultats de stratégies
            
        Returns:
            Liste triée par performance (meilleure en premier)
        """
        def calculate_score(metrics: Dict[str, float]) -> float:
            """Calcule un score composite pour le classement."""
            return (
                metrics.get('total_return', 0) * 0.3 +
                metrics.get('sharpe_ratio', 0) * 0.3 +
                (1 - abs(metrics.get('max_drawdown', 1))) * 0.2 +
                metrics.get('win_rate', 0) * 0.2
            )
        
        # Ajout du score à chaque stratégie
        for result in strategies_results:
            result['score'] = calculate_score(result['metrics'])
        
        # Tri par score décroissant
        return sorted(strategies_results, key=lambda x: x['score'], reverse=True)
    
    @staticmethod
    def generate_performance_report(results: Dict[str, Any]) -> str:
        """
        Génère un rapport de performance textuel.
        
        Args:
            results: Résultats du backtest
            
        Returns:
            Rapport formaté en texte
        """
        strategy = results['strategy']
        metrics = results['metrics']
        period = results['backtest_period']
        
        report = f"""
=== RAPPORT DE PERFORMANCE ===

Stratégie: {strategy['name']}
Description: {strategy['description']}
Période: {period['start']} à {period['end']} ({period['duration_days']} jours)

--- RÉSULTATS FINANCIERS ---
Capital initial: ${results['parameters']['initial_cash']:,.2f}
Valeur finale: ${metrics['final_value']:,.2f}
Rendement total: {metrics['total_return']:.2%}
Alpha vs Buy & Hold: {metrics['alpha']:.2%}

--- MÉTRIQUES DE RISQUE ---
Ratio de Sharpe: {metrics['sharpe_ratio']:.2f}
Drawdown maximum: {metrics['max_drawdown']:.2%}
Volatilité: {metrics.get('volatility', 0):.2%}

--- STATISTIQUES DE TRADING ---
Nombre total de trades: {metrics['total_trades']}
Taux de réussite: {metrics['win_rate']:.2%}
Durée moyenne des trades: {metrics['avg_trade_duration']:.1f} jours
Facteur de profit: {metrics['profit_factor']:.2f}

--- PARAMÈTRES ---
"""
        
        for key, value in strategy['parameters'].items():
            report += f"{key}: {value}\n"
        
        # Évaluation de la performance
        is_profitable = PerformanceMetrics.is_strategy_profitable(metrics)
        report += f"\n--- ÉVALUATION ---\n"
        report += f"Stratégie profitable: {'✅ OUI' if is_profitable else '❌ NON'}\n"
        
        return report