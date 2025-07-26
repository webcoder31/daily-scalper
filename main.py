#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily Scalper - Application de test de stratégies de trading crypto
Script principal pour exécuter les backtests et analyser les performances.
"""

import sys
import os
from typing import Dict, Any, Optional, List
import warnings

# Suppression des warnings non critiques
warnings.filterwarnings('ignore', category=FutureWarning)

# Ajout du répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Rich imports for elegant terminal formatting
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from strategies import SMACrossoverStrategy
from backtest import BacktestEngine, PerformanceMetrics
from utils import DataLoader, Visualizer, StrategySaver, PeriodTranslator

# Initialize rich console
console = Console(width=120)


class DailyScalper:
    """
    Classe principale pour l'application Daily Scalper.
    """
    
    def __init__(self):
        """Initialise l'application."""
        self.data_loader = DataLoader()
        self.backtest_engine = BacktestEngine()
        self.strategy_saver = StrategySaver()
        
        console.print()
        console.print(Panel(
            Text("Application initialisée avec succès !", justify="center"), 
            title="DAILY SCALPER - TESTEUR DE STRATEGIES DE TRADING",
            padding=(1, 1), 
            style="bold bright_green"
        ))
    
    def _display_results(self, results: Dict[str, Any]) -> None:
        """
        Affiche les résultats du backtest.
        
        Args:
            results: Résultats du backtest
        """
        metrics = results['metrics']
        strategy = results['strategy']
        period = results['backtest_period']
                
        # Create a header table with key information
        header_table = Table(
            box=box.DOUBLE_EDGE, 
            style="bright_magenta", 
            border_style="blue", 
            title="[bold bright_magenta]CONFIGURATION DU BACKTEST[/bold bright_magenta]", 
            width=120
        )
        header_table.add_column("PARAMETRE", style="bold bright_magenta", width=41)
        header_table.add_column("VALEUR", style="bold bright_white", width=79)
        
        # Add coin pair
        coin_pair = results.get('symbol', strategy.get('symbol', 'N/A'))
        header_table.add_row(
            "SYMBOLE",
            f"[bold bright_green]{coin_pair.upper()}[/bold bright_green]"
        )

        # Add initial capital
        initial_cash = results['parameters']['initial_cash']
        header_table.add_row(
            "CAPITAL INITIAL",
            f"[bold bright_green]${initial_cash:,.2f}[/bold bright_green]"
        )

        # Add period
        period_str = f"{period['start']} → {period['end']} ({period['duration_days']} JOURS)"
        header_table.add_row(
            "PÉRIODE",
            f"[bold bright_green]{period_str}[/bold bright_green]"
        )
        
        # Add strategy name
        strategy_name = strategy['name'].upper()
        header_table.add_row(
            "STRATÉGIE",
            f"[bold bright_yellow]{strategy_name}[/bold bright_yellow]"
        )
        
        # Add strategy parameters if available
        if 'parameters' in strategy:
            params = strategy['parameters']
            param_str = " | ".join([f"{k.upper()}: {v}" for k, v in params.items()])
            header_table.add_row(
                "PARAMÈTRES",
                f"[bold bright_yellow]{param_str}[/bold bright_yellow]"
            )
        
        console.print(header_table)
        console.print()
        
        # Table des métriques de performance
        perf_metric_table = Table(
            box=box.ROUNDED, 
            style="blue", 
            border_style="blue", 
            title="[bold bright_magenta]RESULTATS DU BACKTEST[/bold bright_magenta]", 
            width=120
        )
        perf_metric_table.add_column("Métrique de performance", style="bold bright_blue", width=40)
        perf_metric_table.add_column("Valeur", justify="right", style="bright_blue", width=20)
        perf_metric_table.add_column("Métrique de performance", style="bold bright_blue", width=40)
        perf_metric_table.add_column("Valeur", justify="right", style="bright_blue", width=20)
        
        perf_metric_table.add_row(
            "Capital initial", f"${results['parameters']['initial_cash']:,.2f}",
            "Valeur finale", f"${metrics['final_value']:,.2f}"
        )
        perf_metric_table.add_row(
            "Rendement total", f"{metrics['total_return']:.2%}",
            "Alpha vs Buy & Hold", f"{metrics['alpha']:.2%}"
        )
        perf_metric_table.add_row(
            "Ratio de Sharpe", f"{metrics['sharpe_ratio']:.2f}",
            "Drawdown maximum", f"{metrics['max_drawdown']:.2%}"
        )
        perf_metric_table.add_row(
            "Volatilité", f"{metrics.get('volatility', 0):.2%}",
            "VaR 95%", f"{metrics.get('var_95', 0):.2%}"
        )
        
        console.print(perf_metric_table)
        
        # Table des statistiques de trading
        trading_metric_table = Table(box=box.ROUNDED, style="blue", border_style="blue", width=120)
        trading_metric_table.add_column("Statistiques de trading", style="bold bright_blue", width=40)
        trading_metric_table.add_column("Valeur", justify="right", style="bright_blue", width=20)
        trading_metric_table.add_column("Statistiques de trading", style="bold bright_blue", width=40)
        trading_metric_table.add_column("Valeur", justify="right", style="bright_blue", width=20)
        
        trading_metric_table.add_row(
            "Nombre de trades", f"{metrics['total_trades']}",
            "Taux de réussite", f"{metrics['win_rate']:.2%}"
        )
        trading_metric_table.add_row(
            "Facteur de profit", f"{metrics['profit_factor']:.2f}",
            "Durée moyenne", f"{metrics['avg_trade_duration']:.1f} jours"
        )
        
        console.print(trading_metric_table)
        
        # Évaluation finale
        is_profitable = PerformanceMetrics.is_strategy_profitable(metrics)
        status_text =  "✅ STRATÉGIE PROFITABLE" if is_profitable else "❌ STRATÉGIE NON PROFITABLE"
        status_style = "bold green" if is_profitable else "bold red"

        console.print()
        console.print(Panel(
            Text(status_text, justify="center"), 
            title=f"ÉVALUATION FINALE",
            padding=(1, 1), 
            style=status_style
        ))
        console.print()

    def backtest_strategy(
            self, 
            symbol: str = "BTC-USD",
            period: str = "1y",
            short_window: int = 20,
            long_window: int = 50,
            show_plots: bool = True,
            save_if_profitable: bool = True
        ) -> Dict[str, Any]:
        """
        Exécute un backtest d'une stratégie SMA Crossover.
        
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

        console.print()
        console.print(Panel(
            Text(f"SMA Crossover {short_window}/{long_window}\nPaire : {symbol}, Période: {PeriodTranslator.get_period_description(period)}", justify="center"), 
            title=f"BACKTEST D'UNE STRATÉGIE",
            padding=(1, 1), 
            style="bold bright_magenta"
        ))
        console.print()
        
        try:
            # 1. Chargement des données
            console.print("Chargement des données...", style="blue")
            data = self.data_loader.load_crypto_data(symbol=symbol, period=period)
            console.print(f"✅ {len(data)} points de données chargés\n", style="green")
            
            # 2. Création de la stratégie
            console.print("Initialisation de la stratégie...", style="blue")
            strategy = SMACrossoverStrategy(
                short_window=short_window,
                long_window=long_window
            )
            console.print(f"✅ {strategy.get_description()}\n", style="green")
            
            # 3. Exécution du backtest
            console.print("Exécution du backtest...", style="blue")
            results = self.backtest_engine.run_backtest(strategy, data)
            
            # Ajout de l'instance de stratégie pour la visualisation
            results['strategy_instance'] = strategy
            
            # Ajout du symbole pour l'affichage
            results['symbol'] = symbol
            
            # 4. Calcul des métriques avancées
            console.print("Calcul des métriques avancées...", style="blue")
            results['metrics'] = PerformanceMetrics.calculate_advanced_metrics(results)
            console.print("✅ Backtest terminé!\n", style="green")
            
            # 5. Affichage des résultats
            self._display_results(results)
            
            # 6. Visualisation
            if show_plots:
                console.print("Génération des graphiques...", style="blue")
                Visualizer.show_all_plots(results)
            
            # 7. Sauvegarde si profitable
            if save_if_profitable and PerformanceMetrics.is_strategy_profitable(results['metrics']):
                console.print("Stratégie profitable détectée - Sauvegarde...", style="green")
                save_id = self.strategy_saver.save_strategy_results(results)
                results['save_id'] = save_id
                console.print(f"✅ Stratégie sauvegardée: {save_id}", style="green")
            elif save_if_profitable:
                console.print("❌ Stratégie non profitable - Pas de sauvegarde", style="yellow")
            
            return results
            
        except Exception as e:
            console.print(f"❌ Erreur lors de l'exécution: {e}", style="red")
            raise
    
    def compare_strategies(
            self, 
            symbol: str = "BTC-USD",
            period: str = "1y"
        ) -> None:
        """
        Compare différentes configurations de la stratégie SMA.
        
        Args:
            symbol: Symbole à analyser
            period: Période des données
        """

        console.print()
        console.print(Panel(
            Text(f"SMA Crossover\nPaire : {symbol}, Période: {PeriodTranslator.get_period_description(period)}", justify="center"), 
            title=f"COMPARAISON DE STRATÉGIES",
            padding=(1, 1), 
            style="bold bright_magenta"
        ))
        console.print()
        
        # Différentes configurations à tester
        configurations = [
            (10, 30),
            (20, 50),
            (30, 70),
            (50, 100),
            (20, 100)
        ]
        
        results_list = []
        
        # Table pour les résultats
        progress_table = Table(box=box.ROUNDED, style="blue", border_style="blue", width=120)
        progress_table.add_column("Test", style="bold bright_blue", width=8)
        progress_table.add_column("Configuration", style="bold bright_blue", width=20)
        progress_table.add_column("Rendement", justify="right", style="bright_blue", width=15)
        progress_table.add_column("Sharpe", justify="right", style="bright_blue", width=12)
        progress_table.add_column("Trades", justify="right", style="bright_blue", width=12)
        progress_table.add_column("Profit Factor", justify="right", style="bright_blue", width=15)
        progress_table.add_column("Statut", justify="center", style="bright_blue", width=12)
        
        for i, (short, long) in enumerate(configurations, 1):
            try:
                results = self.backtest_strategy(
                    symbol=symbol,
                    period=period,
                    short_window=short,
                    long_window=long,
                    show_plots=False,
                    save_if_profitable=False
                )
                results_list.append(results)
                
                metrics = results['metrics']
                status = "✅" if metrics['total_return'] > 0 else "❌"
                
                progress_table.add_row(
                    f"{i}/5",
                    f"SMA {short}/{long}",
                    f"{metrics['total_return']:.2%}",
                    f"{metrics['sharpe_ratio']:.2f}",
                    f"{metrics['total_trades']}",
                    f"{metrics['profit_factor']:.2f}",
                    status
                )
                
            except Exception as e:
                progress_table.add_row(
                    f"{i}/5",
                    f"SMA {short}/{long}",
                    "❌ Erreur",
                    "-",
                    "-",
                    "-",
                    "❌"
                )
        
        console.print("\nRÉSULTAS DES TESTS", style="bold bright_blue")
        console.print(progress_table)
        
        # Classement des stratégies
        if results_list:
            
            ranked_strategies = PerformanceMetrics.rank_strategies(results_list)
            
            ranking_table = Table(box=box.ROUNDED, style="blue", border_style="blue", width=120)
            ranking_table.add_column("Rang", style="bold bright_blue", width=10)
            ranking_table.add_column("Configuration", style="bold bright_blue", width=20)
            ranking_table.add_column("Rendement", justify="right", style="bright_blue", width=15)
            ranking_table.add_column("Sharpe", justify="right", style="bright_blue", width=12)
            ranking_table.add_column("Score", justify="right", style="bright_blue", width=12)
            ranking_table.add_column("Statut", style="bright_blue", width=20)
                        
            for i, result in enumerate(ranked_strategies, 1):
                strategy = result['strategy']
                metrics = result['metrics']
                params = strategy['parameters']
                
                is_profitable = PerformanceMetrics.is_strategy_profitable(metrics)
                status = "✅ Profitable" if is_profitable else "❌ Non profitable"
                
                ranking_table.add_row(
                    f"#{i}",
                    f"SMA {params['short_window']}/{params['long_window']}",
                    f"{metrics['total_return']:.2%}",
                    f"{metrics['sharpe_ratio']:.2f}",
                    f"{result['score']:.3f}",
                    status
                )
            
            console.print("\nCLASSEMENT DES STRATÉGIES", style="bold bright_blue")
            console.print(ranking_table)
        else:
            console.print("❌ Aucun résultat valide obtenu pour la comparaison.", style="red")
            
    def show_saved_strategies(self) -> None:
        """Affiche les stratégies sauvegardées avec un formatage simple."""

        status_text = "Aucune stratégie sauvegardée" if not self.strategy_saver.has_saved_strategies() else f"{len(strategies)} stratégie(s) sauvegardée(s)"

        console.print()
        console.print(Panel(
            Text(f"SMA Crossover\nPaire : {symbol}, Période: {PeriodTranslator.get_period_description(period)}", justify="center"), 
            title=f"STRATÉGIES SAUVEGARDÉES",
            padding=(1, 1), 
            style="bold bright_magenta"
        ))
        console.print()
        
        if not strategies:
            console.print("\nAucune stratégie sauvegardée.", style="blue")
            console.print("Exécutez des backtests profitables pour en créer.")
            return
        
        console.print(f"Liste des meilleures stratégie:", style="bold")
        
        # Table des stratégies sauvegardées
        saved_table = Table(box=box.ROUNDED, style="blue", border_style="blue", width=120)
        saved_table.add_column("ID", style="bold bright_blue", width=8)
        saved_table.add_column("Stratégie", style="bold bright_blue", width=18)
        saved_table.add_column("Rendement", justify="right", style="bright_blue", width=15)
        saved_table.add_column("Sharpe", justify="right", style="bright_blue", width=12)
        saved_table.add_column("Trades", justify="right", style="bright_blue", width=12)
        saved_table.add_column("Date", style="bright_blue", width=15)
        saved_table.add_column("Statut", style="bright_blue", width=15)
        
        for i, strategy in enumerate(strategies[:10], 1):
            metrics = strategy.get('metrics', {})
            strategy_info = strategy.get('strategy', {})
            
            is_profitable = metrics.get('total_return', 0) > 0
            status = "✅ Profitable" if is_profitable else "❌ Non profitable"
            
            saved_table.add_row(
                f"#{i}",
                strategy_info.get('name', 'N/A'),
                f"{metrics.get('total_return', 0):.2%}",
                f"{metrics.get('sharpe_ratio', 0):.2f}",
                f"{metrics.get('total_trades', 0)}",
                strategy.get('timestamp', 'N/A')[:10],  # Date only
                status
            )
        
        console.print(saved_table)
        
        if len(strategies) > 10:
            console.print(f"{len(strategies) - 10} stratégie(s) supplémentaire(s) disponible(s)...", style="dim")
        
        console.print("=" * 120, style="dim")


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
            console.print(f"❌ Erreur: Veuillez entrer une valeur valide ({input_type.__name__})", style="red")
        except KeyboardInterrupt:
            console.print("\n⏹️ Opération annulée", style="yellow")
            return None


def show_main_menu() -> None:
    """Affiche le menu principal."""
    console.print("\nMENU PRINCIPAL", style="bold bright_green")

    menu_table = Table(show_header=False, box=box.ROUNDED, style="bright_green", border_style="bright_green", width=120)
    menu_table.add_column("Option", style="bold bright_green", width=5)
    menu_table.add_column("Description", style="bright_green", width=115)
    
    menu_table.add_row("1", "Tester une stratégie")
    menu_table.add_row("2", "Comparer des stratégies")
    menu_table.add_row("3", "Voir les résultats sauvegardés")
    menu_table.add_row("4", "Configuration")
    menu_table.add_row("5", "Quitter")
    
    console.print(menu_table)


def backtest_strategy_menu(app: DailyScalper) -> None:
    """Menu pour tester une stratégie."""
    console.print("\nPARAMÉTRAGE DU BACKTEST DE STRATÉGIE\n", style="bright_green bold  underline")
    
    # Paramètres par défaut
    default_symbol = "BTC-USD"
    default_period = "1y"
    default_short = 20
    default_long = 50
    
    # Collecte des paramètres
    symbol = get_user_input(f"Symbole crypto [{default_symbol}]: ", str, default_symbol)
    if symbol is None:
        return
    
    console.print(f"Périodes disponibles: {PeriodTranslator.get_available_periods()}", style="dim")
    period = get_user_input(f"Période [{PeriodTranslator.get_period_description(default_period)}]: ", str, default_period)
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
    show_plots = show_plots_input.lower() in ['o', 'oui', 'y', 'yes', 'true']
    
    save_input = get_user_input("Sauvegarder si profitable? [O/n]: ", str, "o")
    if save_input is None:
        return
    save_if_profitable = save_input.lower() not in ['n', 'non', 'no', 'false']
    
    try:
        console.print("\nLancement du test...", style="bold blue")
        results = app.backtest_strategy(
            symbol=symbol,
            period=period,
            short_window=short_window,
            long_window=long_window,
            show_plots=show_plots,
            save_if_profitable=save_if_profitable
        )
        
        console.print("✅ Test terminé avec succès!", style="bold green")
        
    except Exception as e:
        console.print(f"❌ Erreur lors du test: {e}", style="red")
    
    input("\nAppuyez sur Entrée pour continuer...")


def compare_strategies_menu(app: DailyScalper) -> None:
    """Menu pour comparer des stratégies."""
    console.print("\nPARAMÉTRAGE DE LA COMPARAISON DE STRATÉGIES\n", style="bright_green bold underline")
    
    # Paramètres par défaut
    default_symbol = "BTC-USD"
    default_period = "1y"
    
    symbol = get_user_input(f"Symbole crypto [{default_symbol}]: ", str, default_symbol)
    if symbol is None:
        return
    
    console.print(f"Périodes disponibles: {PeriodTranslator.get_available_periods()}", style="dim")
    period = get_user_input(f"Période [{PeriodTranslator.get_period_description(default_period)}]: ", str, default_period)
    if period is None:
        return
    
    try:
        console.print("Lancement de la comparaison...", style="bold blue")
        app.compare_strategies(symbol=symbol, period=period)
        console.print("✅ Comparaison terminée!", style="bold green")
        
    except Exception as e:
        console.print(f"❌ Erreur lors de la comparaison: {e}", style="red")
    
    input("\nAppuyez sur Entrée pour continuer...")


def view_saved_results_menu(app: DailyScalper) -> None:
    """Menu pour voir les résultats sauvegardés."""
    try:
        app.show_saved_strategies()
        
    except Exception as e:
        console.print(f"❌ Erreur lors de l'affichage: {e}", style="red")
    
    input("\nAppuyez sur Entrée pour continuer...")


def view_configuration_menu() -> None:
    """Menu de configuration."""

    console.print()
    console.print(Panel(
        Text(f"Configuration actuelle définie dans config.py", justify="center"), 
        title=f"CONFIGURATION",
        padding=(1, 1), 
        style="bold bright_magenta"
    ))
    console.print()
    
    try:
        # Import des paramètres de configuration
        from config import (
            DEFAULT_BACKTEST_CONFIG, 
            DEFAULT_DATA_CONFIG, 
            PROFITABILITY_CRITERIA, 
            VISUALIZATION_CONFIG,
            POPULAR_CRYPTO_SYMBOLS
        )
        
        # Table de configuration backtest
        backtest_table = Table(box=box.ROUNDED, style="blue", border_style="blue", width=120)
        backtest_table.add_column("Paramètre Backtest", style="bold bright_blue", width=50)
        backtest_table.add_column("Valeur", justify="right", style="bright_blue", width=50)
        
        backtest_table.add_row("Capital initial", f"{DEFAULT_BACKTEST_CONFIG['initial_cash']:,.2f} USD")
        backtest_table.add_row("Commission", f"{DEFAULT_BACKTEST_CONFIG['commission']:.3f} ({DEFAULT_BACKTEST_CONFIG['commission']*100:.1f}%)")
        backtest_table.add_row("Slippage", f"{DEFAULT_BACKTEST_CONFIG['slippage']:.4f} ({DEFAULT_BACKTEST_CONFIG['slippage']*100:.2f}%)")
        
        console.print("\nParamètres de Backtest")
        console.print(backtest_table)
        
        # Table de configuration données
        data_table = Table(box=box.ROUNDED, style="blue", border_style="blue", width=120)
        data_table.add_column("Paramètre Données", style="bold bright_blue", width=50)
        data_table.add_column("Valeur", justify="right", style="bright_blue", width=50)
        
        data_table.add_row("Symbole par défaut", DEFAULT_DATA_CONFIG['default_symbol'])
        data_table.add_row("Période par défaut", PeriodTranslator.get_period_description(DEFAULT_DATA_CONFIG['default_period']))
        data_table.add_row("Cache activé", 'Oui' if DEFAULT_DATA_CONFIG['cache_enabled'] else 'Non')
        data_table.add_row("Durée du cache", f"{DEFAULT_DATA_CONFIG['cache_max_age_hours']} heures")
        
        console.print("\nConfiguration des Données")
        console.print(data_table)
        
        # Table critères de profitabilité
        profit_table = Table(box=box.ROUNDED, style="blue", border_style="blue", width=120)
        profit_table.add_column("Critère Profitabilité", style="bold bright_blue", width=50)
        profit_table.add_column("Valeur", justify="right", style="bright_blue", width=50)
        
        profit_table.add_row("Rendement minimum", f"{PROFITABILITY_CRITERIA['min_return']:.1%}")
        profit_table.add_row("Ratio Sharpe minimum", f"{PROFITABILITY_CRITERIA['min_sharpe']:.1f}")
        profit_table.add_row("Drawdown maximum", f"{PROFITABILITY_CRITERIA['max_drawdown']:.1%}")
        profit_table.add_row("Trades minimum", f"{PROFITABILITY_CRITERIA['min_trades']}")
        
        console.print("\nCritères de Profitabilité")
        console.print(profit_table)
        
        # Symboles populaires
        symbols_text = ", ".join(POPULAR_CRYPTO_SYMBOLS[:10])
        if len(POPULAR_CRYPTO_SYMBOLS) > 10:
            symbols_text += f"\n... et {len(POPULAR_CRYPTO_SYMBOLS) - 10} autres"
        
        console.print(f"\nSymboles crypto populaires ({len(POPULAR_CRYPTO_SYMBOLS)} disponibles):")
        console.print(symbols_text, style="blue")
        
        # Instructions de modification
        console.print("\nPour modifier la configuration:", style="blue")
        console.print("1. Éditez le fichier 'config.py'")
        console.print("2. Redémarrez l'application")
        console.print("3. Les nouveaux paramètres seront appliqués")
        
    except Exception as e:
        console.print(f"❌ Erreur lors de la lecture de la configuration: {e}", style="red")
    
    input("\nAppuyez sur Entrée pour continuer...")


def main():
    """Fonction principale avec menu interactif."""

    # Initialisation de l'application
    app = DailyScalper()
    
    while True:
        try:
            show_main_menu()
            
            choice = get_user_input("Choisissez une option (1-5): ", str)
            
            if choice is None:  # Ctrl+C
                break
            elif choice == "1":
                backtest_strategy_menu(app)
            elif choice == "2":
                compare_strategies_menu(app)
            elif choice == "3":
                view_saved_results_menu(app)
            elif choice == "4":
                view_configuration_menu()
            elif choice == "5":
                console.print("👋 Au revoir !", style="bold green")
                break
            else:
                console.print("❌ Option invalide. Veuillez choisir entre 1 et 5.", style="red")
                input("Appuyez sur Entrée pour continuer...")
                
        except KeyboardInterrupt:
            console.print("\n\nArrêt demandé par l'utilisateur", style="yellow")
            break
        except Exception as e:
            console.print(f"❌ Erreur inattendue: {e}", style="red")
            input("Appuyez sur Entrée pour continuer...")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())