#!/usr/bin/env python3
"""
Daily Scalper - Application de test de stratégies de trading crypto
Script principal pour exécuter les backtests et analyser les performances.
"""

import sys
import os
from typing import Dict, Any, Optional
import warnings

# Suppression des warnings non critiques
warnings.filterwarnings('ignore', category=FutureWarning)

# Ajout du répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from strategies import SMACrossoverStrategy
from backtest import BacktestEngine, PerformanceMetrics
from utils import DataLoader, Visualizer, StrategySaver


class DailyScalper:
    """
    Classe principale pour l'application Daily Scalper.
    """
    
    def __init__(self):
        """Initialise l'application."""
        self.data_loader = DataLoader()
        self.backtest_engine = BacktestEngine()
        self.strategy_saver = StrategySaver()
        
        print("=== DAILY SCALPER - CRYPTO TRADING STRATEGY TESTER ===")
        print("Application initialisée avec succès!\n")
    
    def run_sma_example(self, 
                       symbol: str = "BTC-USD",
                       period: str = "1y",
                       short_window: int = 20,
                       long_window: int = 50,
                       show_plots: bool = True,
                       save_if_profitable: bool = True) -> Dict[str, Any]:
        """
        Exécute un exemple complet avec la stratégie SMA Crossover.
        
        Args:
            symbol: Symbole crypto à analyser
            period: Période des données
            short_window: Période SMA courte
            long_window: Période SMA longue
            show_plots: Afficher les graphiques
            save_if_profitable: Sauvegarder si profitable
            
        Returns:
            Résultats du backtest
        """
        print(f"🚀 Démarrage du backtest pour {symbol}")
        print(f"📊 Stratégie: SMA Crossover ({short_window}/{long_window})")
        print(f"📅 Période: {period}\n")
        
        try:
            # 1. Chargement des données
            print("📥 Chargement des données...")
            data = self.data_loader.load_crypto_data(symbol=symbol, period=period)
            print(f"✅ {len(data)} points de données chargés\n")
            
            # 2. Création de la stratégie
            print("🎯 Initialisation de la stratégie...")
            strategy = SMACrossoverStrategy(
                short_window=short_window,
                long_window=long_window
            )
            print(f"✅ {strategy.get_description()}\n")
            
            # 3. Exécution du backtest
            print("⚡ Exécution du backtest...")
            results = self.backtest_engine.run_backtest(strategy, data)
            
            # Ajout de l'instance de stratégie pour la visualisation
            results['strategy_instance'] = strategy
            
            # 4. Calcul des métriques avancées
            print("📈 Calcul des métriques avancées...")
            results['metrics'] = PerformanceMetrics.calculate_advanced_metrics(results)
            print("✅ Backtest terminé!\n")
            
            # 5. Affichage des résultats
            self._display_results(results)
            
            # 6. Visualisation
            if show_plots:
                print("📊 Génération des graphiques...")
                Visualizer.show_all_plots(results)
            
            # 7. Sauvegarde si profitable
            if save_if_profitable and PerformanceMetrics.is_strategy_profitable(results['metrics']):
                print("💾 Stratégie profitable détectée - Sauvegarde...")
                save_id = self.strategy_saver.save_strategy_results(results)
                results['save_id'] = save_id
                print(f"✅ Stratégie sauvegardée: {save_id}")
            elif save_if_profitable:
                print("⚠️  Stratégie non profitable - Pas de sauvegarde")
            
            return results
            
        except Exception as e:
            print(f"❌ Erreur lors de l'exécution: {e}")
            raise
    
    def _display_results(self, results: Dict[str, Any]) -> None:
        """
        Affiche les résultats du backtest de manière formatée.
        
        Args:
            results: Résultats du backtest
        """
        metrics = results['metrics']
        strategy = results['strategy']
        period = results['backtest_period']
        
        print("=" * 60)
        print("📊 RÉSULTATS DU BACKTEST")
        print("=" * 60)
        
        print(f"Stratégie: {strategy['name']}")
        print(f"Période: {period['start']} → {period['end']} ({period['duration_days']} jours)")
        print()
        
        print("💰 PERFORMANCE FINANCIÈRE:")
        print(f"  Capital initial: ${results['parameters']['initial_cash']:,.2f}")
        print(f"  Valeur finale: ${metrics['final_value']:,.2f}")
        print(f"  Rendement total: {metrics['total_return']:.2%}")
        print(f"  Alpha vs Buy & Hold: {metrics['alpha']:.2%}")
        print()
        
        print("📈 MÉTRIQUES DE RISQUE:")
        print(f"  Ratio de Sharpe: {metrics['sharpe_ratio']:.2f}")
        print(f"  Drawdown maximum: {metrics['max_drawdown']:.2%}")
        print(f"  Volatilité: {metrics.get('volatility', 0):.2%}")
        print(f"  VaR 95%: {metrics.get('var_95', 0):.2%}")
        print()
        
        print("🎯 STATISTIQUES DE TRADING:")
        print(f"  Nombre de trades: {metrics['total_trades']}")
        print(f"  Taux de réussite: {metrics['win_rate']:.2%}")
        print(f"  Facteur de profit: {metrics['profit_factor']:.2f}")
        print(f"  Durée moyenne: {metrics['avg_trade_duration']:.1f} jours")
        print()
        
        # Évaluation
        is_profitable = PerformanceMetrics.is_strategy_profitable(metrics)
        status = "✅ PROFITABLE" if is_profitable else "❌ NON PROFITABLE"
        print(f"🏆 ÉVALUATION: {status}")
        print("=" * 60)
        print()
    
    def compare_strategies(self, 
                          symbol: str = "BTC-USD",
                          period: str = "1y") -> None:
        """
        Compare différentes configurations de la stratégie SMA.
        
        Args:
            symbol: Symbole à analyser
            period: Période des données
        """
        print("🔄 COMPARAISON DE STRATÉGIES SMA")
        print("=" * 50)
        
        # Différentes configurations à tester
        configurations = [
            (10, 30),
            (20, 50),
            (30, 70),
            (50, 100),
            (20, 100)
        ]
        
        results_list = []
        
        for short, long in configurations:
            print(f"\n🧪 Test SMA {short}/{long}...")
            try:
                results = self.run_sma_example(
                    symbol=symbol,
                    period=period,
                    short_window=short,
                    long_window=long,
                    show_plots=False,
                    save_if_profitable=False
                )
                results_list.append(results)
                
                # Affichage rapide
                metrics = results['metrics']
                print(f"   Rendement: {metrics['total_return']:.2%}")
                print(f"   Sharpe: {metrics['sharpe_ratio']:.2f}")
                print(f"   Trades: {metrics['total_trades']}")
                
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
        
        # Classement des stratégies
        if results_list:
            print("\n🏆 CLASSEMENT DES STRATÉGIES:")
            print("-" * 40)
            
            ranked_strategies = PerformanceMetrics.rank_strategies(results_list)
            
            for i, result in enumerate(ranked_strategies[:3], 1):
                strategy = result['strategy']
                metrics = result['metrics']
                params = strategy['parameters']
                
                print(f"{i}. SMA {params['short_window']}/{params['long_window']}")
                print(f"   Rendement: {metrics['total_return']:.2%}")
                print(f"   Sharpe: {metrics['sharpe_ratio']:.2f}")
                print(f"   Score: {result['score']:.3f}")
                print()
    
    def show_saved_strategies(self) -> None:
        """Affiche les stratégies sauvegardées."""
        print("📚 STRATÉGIES SAUVEGARDÉES")
        print("=" * 40)
        
        strategies = self.strategy_saver.list_saved_strategies()
        
        if not strategies:
            print("Aucune stratégie sauvegardée.")
            return
        
        for i, strategy in enumerate(strategies[:10], 1):  # Top 10
            metrics = strategy.get('metrics', {})
            print(f"{i}. {strategy.get('save_id', 'N/A')}")
            print(f"   Stratégie: {strategy.get('strategy', {}).get('name', 'N/A')}")
            print(f"   Rendement: {metrics.get('total_return', 0):.2%}")
            print(f"   Sharpe: {metrics.get('sharpe_ratio', 0):.2f}")
            print(f"   Date: {strategy.get('timestamp', 'N/A')}")
            print()


def main():
    """Fonction principale."""
    # Initialisation de l'application
    app = DailyScalper()
    
    try:
        # Exemple principal avec BTC
        print("🎯 EXEMPLE PRINCIPAL - BTC-USD")
        results = app.run_sma_example(
            symbol="BTC-USD",
            period="1y",
            short_window=20,
            long_window=50,
            show_plots=True,
            save_if_profitable=True
        )
        
        print("\n" + "="*60)
        
        # Comparaison de stratégies
        print("\n🔬 ANALYSE COMPARATIVE")
        app.compare_strategies(symbol="BTC-USD", period="6mo")
        
        print("\n" + "="*60)
        
        # Affichage des stratégies sauvegardées
        print("\n📋 HISTORIQUE")
        app.show_saved_strategies()
        
        print("\n✅ Analyse terminée avec succès!")
        print("\n💡 Conseils:")
        print("   - Modifiez les paramètres dans main() pour tester d'autres configurations")
        print("   - Consultez le dossier 'results/' pour les rapports détaillés")
        print("   - Les graphiques interactifs s'ouvrent dans votre navigateur")
        
    except KeyboardInterrupt:
        print("\n⏹️  Arrêt demandé par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())