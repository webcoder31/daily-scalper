"""
Module pour sauvegarder et charger les stratégies performantes.
"""

import json
import pickle
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd


class StrategySaver:
    """
    Classe pour sauvegarder et gérer les stratégies performantes.
    """
    
    def __init__(self, results_dir: str = "results"):
        """
        Initialise le gestionnaire de sauvegarde.
        
        Args:
            results_dir: Répertoire pour sauvegarder les résultats
        """
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)
        
        # Sous-dossiers
        self.strategies_dir = os.path.join(results_dir, "strategies")
        self.reports_dir = os.path.join(results_dir, "reports")
        self.charts_dir = os.path.join(results_dir, "charts")
        
        for directory in [self.strategies_dir, self.reports_dir, self.charts_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def save_strategy_results(self, 
                            results: Dict[str, Any], 
                            save_charts: bool = True) -> str:
        """
        Sauvegarde les résultats d'une stratégie.
        
        Args:
            results: Résultats du backtest
            save_charts: Sauvegarder les graphiques
            
        Returns:
            ID unique de la sauvegarde
        """
        # Génération d'un ID unique
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        strategy_name = results['strategy']['name'].replace(' ', '_').lower()
        save_id = f"{strategy_name}_{timestamp}"
        
        # Préparation des données à sauvegarder
        save_data = {
            'save_id': save_id,
            'timestamp': timestamp,
            'strategy': results['strategy'],
            'metrics': results['metrics'],
            'backtest_period': results['backtest_period'],
            'parameters': results['parameters']
        }
        
        # Sauvegarde JSON (métadonnées)
        json_file = os.path.join(self.strategies_dir, f"{save_id}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False, default=str)
        
        # Sauvegarde Pickle (données complètes)
        pickle_file = os.path.join(self.strategies_dir, f"{save_id}.pkl")
        with open(pickle_file, 'wb') as f:
            pickle.dump(results, f)
        
        # Sauvegarde du rapport textuel
        self._save_text_report(results, save_id)
        
        # Sauvegarde des graphiques
        if save_charts:
            self._save_charts(results, save_id)
        
        print(f"Stratégie sauvegardée avec l'ID: {save_id}")
        return save_id
    
    def _save_text_report(self, results: Dict[str, Any], save_id: str) -> None:
        """
        Sauvegarde un rapport textuel.
        
        Args:
            results: Résultats du backtest
            save_id: ID de sauvegarde
        """
        from backtest.performance_metrics import PerformanceMetrics
        
        report = PerformanceMetrics.generate_performance_report(results)
        
        report_file = os.path.join(self.reports_dir, f"{save_id}_report.txt")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
    
    def _save_charts(self, results: Dict[str, Any], save_id: str) -> None:
        """
        Sauvegarde les graphiques.
        
        Args:
            results: Résultats du backtest
            save_id: ID de sauvegarde
        """
        try:
            from utils.visualizer import Visualizer
            
            # Graphique principal
            main_chart = os.path.join(self.charts_dir, f"{save_id}_main.html")
            fig = Visualizer.plot_backtest_results(results, save_path=main_chart)
            
            # Graphique des métriques
            metrics_chart = os.path.join(self.charts_dir, f"{save_id}_metrics.html")
            metrics_fig = Visualizer.plot_performance_metrics(results)
            metrics_fig.write_html(metrics_chart)
            
            # Graphique du drawdown
            drawdown_chart = os.path.join(self.charts_dir, f"{save_id}_drawdown.html")
            drawdown_fig = Visualizer.plot_drawdown(results)
            drawdown_fig.write_html(drawdown_chart)
            
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des graphiques: {e}")
    
    def load_strategy_results(self, save_id: str) -> Optional[Dict[str, Any]]:
        """
        Charge les résultats d'une stratégie sauvegardée.
        
        Args:
            save_id: ID de la sauvegarde
            
        Returns:
            Résultats chargés ou None si non trouvé
        """
        pickle_file = os.path.join(self.strategies_dir, f"{save_id}.pkl")
        
        if not os.path.exists(pickle_file):
            print(f"Stratégie non trouvée: {save_id}")
            return None
        
        try:
            with open(pickle_file, 'rb') as f:
                results = pickle.load(f)
            print(f"Stratégie chargée: {save_id}")
            return results
        except Exception as e:
            print(f"Erreur lors du chargement: {e}")
            return None
    
    def list_saved_strategies(self) -> List[Dict[str, Any]]:
        """
        Liste toutes les stratégies sauvegardées.
        
        Returns:
            Liste des métadonnées des stratégies
        """
        strategies = []
        
        for file in os.listdir(self.strategies_dir):
            if file.endswith('.json'):
                try:
                    with open(os.path.join(self.strategies_dir, file), 'r', encoding='utf-8') as f:
                        strategy_data = json.load(f)
                    strategies.append(strategy_data)
                except Exception as e:
                    print(f"Erreur lors du chargement de {file}: {e}")
        
        # Tri par timestamp (plus récent en premier)
        strategies.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return strategies
    
    def get_best_strategies(self, 
                          top_n: int = 5, 
                          metric: str = 'total_return') -> List[Dict[str, Any]]:
        """
        Retourne les meilleures stratégies selon une métrique.
        
        Args:
            top_n: Nombre de stratégies à retourner
            metric: Métrique pour le classement
            
        Returns:
            Liste des meilleures stratégies
        """
        strategies = self.list_saved_strategies()
        
        # Tri par métrique
        strategies.sort(
            key=lambda x: x.get('metrics', {}).get(metric, 0), 
            reverse=True
        )
        
        return strategies[:top_n]
    
    def delete_strategy(self, save_id: str) -> bool:
        """
        Supprime une stratégie sauvegardée.
        
        Args:
            save_id: ID de la stratégie à supprimer
            
        Returns:
            True si supprimé avec succès, False sinon
        """
        try:
            # Fichiers à supprimer
            files_to_delete = [
                os.path.join(self.strategies_dir, f"{save_id}.json"),
                os.path.join(self.strategies_dir, f"{save_id}.pkl"),
                os.path.join(self.reports_dir, f"{save_id}_report.txt"),
                os.path.join(self.charts_dir, f"{save_id}_main.html"),
                os.path.join(self.charts_dir, f"{save_id}_metrics.html"),
                os.path.join(self.charts_dir, f"{save_id}_drawdown.html")
            ]
            
            deleted_count = 0
            for file_path in files_to_delete:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    deleted_count += 1
            
            print(f"Stratégie {save_id} supprimée ({deleted_count} fichiers)")
            return True
            
        except Exception as e:
            print(f"Erreur lors de la suppression: {e}")
            return False
    
    def export_strategy_summary(self, output_file: str = None) -> str:
        """
        Exporte un résumé de toutes les stratégies.
        
        Args:
            output_file: Fichier de sortie (optionnel)
            
        Returns:
            Chemin du fichier créé
        """
        if output_file is None:
            output_file = os.path.join(self.results_dir, "strategies_summary.csv")
        
        strategies = self.list_saved_strategies()
        
        # Préparation des données pour le CSV
        summary_data = []
        for strategy in strategies:
            row = {
                'save_id': strategy.get('save_id', ''),
                'timestamp': strategy.get('timestamp', ''),
                'strategy_name': strategy.get('strategy', {}).get('name', ''),
                'total_return': strategy.get('metrics', {}).get('total_return', 0),
                'sharpe_ratio': strategy.get('metrics', {}).get('sharpe_ratio', 0),
                'max_drawdown': strategy.get('metrics', {}).get('max_drawdown', 0),
                'win_rate': strategy.get('metrics', {}).get('win_rate', 0),
                'total_trades': strategy.get('metrics', {}).get('total_trades', 0),
                'final_value': strategy.get('metrics', {}).get('final_value', 0)
            }
            summary_data.append(row)
        
        # Sauvegarde en CSV
        df = pd.DataFrame(summary_data)
        df.to_csv(output_file, index=False)
        
        print(f"Résumé exporté: {output_file}")
        return output_file