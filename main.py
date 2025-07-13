#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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


def get_user_input(prompt: str, input_type: type = str, default: Any = None) -> Any:
    """
    Fonction utilitaire pour obtenir une entrée utilisateur avec validation.
    
    Args:
        prompt: Message à afficher
        input_type: Type attendu (str, int, float)
        default: Valeur par défaut
        
    Returns:
        Valeur saisie par l'utilisateur
    """
    while True:
        try:
            user_input = input(prompt).strip()
            
            if not user_input and default is not None:
                return default
            
            if input_type == str:
                return user_input
            elif input_type == int:
                return int(user_input)
            elif input_type == float:
                return float(user_input)
            else:
                return user_input
                
        except ValueError:
            print(f"❌ Erreur: Veuillez entrer une valeur valide ({input_type.__name__})")
        except KeyboardInterrupt:
            print("\n⏹️  Opération annulée")
            return None


def show_menu() -> None:
    """Affiche le menu principal."""
    print("\n" + "="*60)
    print("🚀 DAILY SCALPER - MENU PRINCIPAL")
    print("="*60)
    print("1. 🧪 Tester une stratégie")
    print("2. 🔄 Comparer des stratégies")
    print("3. 📚 Voir les résultats sauvegardés")
    print("4. ⚙️  Configuration")
    print("5. 🚪 Quitter")
    print("="*60)


def test_strategy_menu(app: DailyScalper) -> None:
    """Menu pour tester une stratégie."""
    print("\n🧪 TEST DE STRATÉGIE")
    print("-" * 40)
    
    # Paramètres par défaut
    default_symbol = "BTC-USD"
    default_period = "1y"
    default_short = 20
    default_long = 50
    
    # Collecte des paramètres
    symbol = get_user_input(f"Symbole crypto [{default_symbol}]: ", str, default_symbol)
    if symbol is None:
        return
    
    print("\nPériodes disponibles: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max")
    period = get_user_input(f"Période [{default_period}]: ", str, default_period)
    if period is None:
        return
    
    short_window = get_user_input(f"SMA courte [{default_short}]: ", int, default_short)
    if short_window is None:
        return
    
    long_window = get_user_input(f"SMA longue [{default_long}]: ", int, default_long)
    if long_window is None:
        return
    
    show_plots_input = get_user_input("Afficher les graphiques? [o/N]: ", str, "n")
    if show_plots_input is None:
        return
    show_plots = show_plots_input.lower() in ['o', 'oui', 'y', 'yes']
    
    save_input = get_user_input("Sauvegarder si profitable? [O/n]: ", str, "o")
    if save_input is None:
        return
    save_if_profitable = save_input.lower() not in ['n', 'non', 'no']
    
    try:
        print(f"\n🚀 Lancement du test...")
        results = app.run_sma_example(
            symbol=symbol,
            period=period,
            short_window=short_window,
            long_window=long_window,
            show_plots=show_plots,
            save_if_profitable=save_if_profitable
        )
        
        print("\n✅ Test terminé avec succès!")
        
    except Exception as e:
        print(f"\n❌ Erreur lors du test: {e}")
    
    input("\nAppuyez sur Entrée pour continuer...")


def compare_strategies_menu(app: DailyScalper) -> None:
    """Menu pour comparer des stratégies."""
    print("\n🔄 COMPARAISON DE STRATÉGIES")
    print("-" * 40)
    
    # Paramètres par défaut
    default_symbol = "BTC-USD"
    default_period = "1y"
    
    symbol = get_user_input(f"Symbole crypto [{default_symbol}]: ", str, default_symbol)
    if symbol is None:
        return
    
    print("\nPériodes disponibles: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max")
    period = get_user_input(f"Période [{default_period}]: ", str, default_period)
    if period is None:
        return
    
    try:
        print(f"\n🔬 Lancement de la comparaison...")
        app.compare_strategies(symbol=symbol, period=period)
        print("\n✅ Comparaison terminée!")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la comparaison: {e}")
    
    input("\nAppuyez sur Entrée pour continuer...")


def view_saved_results_menu(app: DailyScalper) -> None:
    """Menu pour voir les résultats sauvegardés."""
    print("\n📚 RÉSULTATS SAUVEGARDÉS")
    print("-" * 40)
    
    try:
        app.show_saved_strategies()
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'affichage: {e}")
    
    input("\nAppuyez sur Entrée pour continuer...")


def configuration_menu() -> None:
    """Menu de configuration."""
    print("\n⚙️  CONFIGURATION")
    print("-" * 40)
    print("Configuration actuelle dans config.py:")
    print()
    
    try:
        # Import des paramètres de configuration
        from config import (
            DEFAULT_BACKTEST_CONFIG, 
            DEFAULT_DATA_CONFIG, 
            PROFITABILITY_CRITERIA, 
            VISUALIZATION_CONFIG,
            POPULAR_CRYPTO_SYMBOLS
        )
        
        # Affichage des paramètres de backtest
        print("📊 Paramètres de backtest:")
        print(f"   - Capital initial: {DEFAULT_BACKTEST_CONFIG['initial_cash']:,.2f} USD")
        print(f"   - Commission: {DEFAULT_BACKTEST_CONFIG['commission']:.3f} ({DEFAULT_BACKTEST_CONFIG['commission']*100:.1f}%)")
        print(f"   - Slippage: {DEFAULT_BACKTEST_CONFIG['slippage']:.4f} ({DEFAULT_BACKTEST_CONFIG['slippage']*100:.2f}%)")
        
        # Affichage des paramètres de données
        print("\n📈 Configuration des données:")
        print(f"   - Symbole par défaut: {DEFAULT_DATA_CONFIG['default_symbol']}")
        print(f"   - Période par défaut: {DEFAULT_DATA_CONFIG['default_period']}")
        print(f"   - Cache activé: {'Oui' if DEFAULT_DATA_CONFIG['cache_enabled'] else 'Non'}")
        print(f"   - Durée du cache: {DEFAULT_DATA_CONFIG['cache_max_age_hours']} heures")
        
        # Affichage des critères de profitabilité
        print("\n💰 Critères de profitabilité:")
        print(f"   - Rendement minimum: {PROFITABILITY_CRITERIA['min_return']:.1%}")
        print(f"   - Ratio de Sharpe minimum: {PROFITABILITY_CRITERIA['min_sharpe']:.1f}")
        print(f"   - Drawdown maximum: {PROFITABILITY_CRITERIA['max_drawdown']:.1%}")
        print(f"   - Nombre minimum de trades: {PROFITABILITY_CRITERIA['min_trades']}")
        
        # Affichage des paramètres de visualisation
        print("\n📊 Configuration de visualisation:")
        print(f"   - Hauteur par défaut: {VISUALIZATION_CONFIG['default_height']} pixels")
        print(f"   - Afficher le volume: {'Oui' if VISUALIZATION_CONFIG['show_volume'] else 'Non'}")
        print(f"   - Afficher les signaux: {'Oui' if VISUALIZATION_CONFIG['show_signals'] else 'Non'}")
        print(f"   - Afficher les indicateurs: {'Oui' if VISUALIZATION_CONFIG['show_indicators'] else 'Non'}")
        
        # Affichage des symboles populaires
        print(f"\n🪙 Symboles crypto populaires ({len(POPULAR_CRYPTO_SYMBOLS)} disponibles):")
        print("   ", ", ".join(POPULAR_CRYPTO_SYMBOLS[:10]))
        if len(POPULAR_CRYPTO_SYMBOLS) > 10:
            print("   ", f"... et {len(POPULAR_CRYPTO_SYMBOLS) - 10} autres")
        
        print("\n🔧 Pour modifier la configuration:")
        print("   1. Éditez le fichier 'config.py'")
        print("   2. Redémarrez l'application")
        print("   3. Les nouveaux paramètres seront appliqués")
        
    except Exception as e:
        print(f"❌ Erreur lors de la lecture de la configuration: {e}")
    
    input("\nAppuyez sur Entrée pour continuer...")


def main():
    """Fonction principale avec menu interactif."""
    # Initialisation de l'application
    app = DailyScalper()
    
    while True:
        try:
            show_menu()
            
            choice = get_user_input("Choisissez une option (1-5): ", str)
            
            if choice is None:  # Ctrl+C
                break
            elif choice == "1":
                test_strategy_menu(app)
            elif choice == "2":
                compare_strategies_menu(app)
            elif choice == "3":
                view_saved_results_menu(app)
            elif choice == "4":
                configuration_menu()
            elif choice == "5":
                print("\n👋 Au revoir!")
                break
            else:
                print("\n❌ Option invalide. Veuillez choisir entre 1 et 5.")
                input("Appuyez sur Entrée pour continuer...")
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Arrêt demandé par l'utilisateur")
            break
        except Exception as e:
            print(f"\n❌ Erreur inattendue: {e}")
            input("Appuyez sur Entrée pour continuer...")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())