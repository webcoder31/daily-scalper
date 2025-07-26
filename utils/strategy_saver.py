"""
Module for saving and loading high-performing strategies.
"""

import json
import pickle
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd


class StrategySaver:
    """
    Class for saving and managing high-performing strategies.
    """
    
    def __init__(self, results_dir: str = "results"):
        """
        Initializes the save manager.
        
        Args:
            results_dir: Directory for saving results
        """
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)
        
        # Subdirectories
        self.strategies_dir = os.path.join(results_dir, "strategies")
        self.reports_dir = os.path.join(results_dir, "reports")
        self.charts_dir = os.path.join(results_dir, "charts")
        
        for directory in [self.strategies_dir, self.reports_dir, self.charts_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def save_strategy_results(self, 
                            results: Dict[str, Any], 
                            save_charts: bool = True) -> str:
        """
        Saves the results of a strategy.
        
        Args:
            results: Backtest results
            save_charts: Save charts
            
        Returns:
            Unique save ID
        """
        # Generate a unique ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        strategy_name = results['strategy']['name'].replace(' ', '_').lower()
        save_id = f"{strategy_name}_{timestamp}"
        
        # Prepare data to save
        save_data = {
            'save_id': save_id,
            'timestamp': timestamp,
            'strategy': results['strategy'],
            'metrics': results['metrics'],
            'backtest_period': results['backtest_period'],
            'parameters': results['parameters']
        }
        
        # Save JSON (metadata)
        json_file = os.path.join(self.strategies_dir, f"{save_id}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False, default=str)
        
        # Save Pickle (full data)
        pickle_file = os.path.join(self.strategies_dir, f"{save_id}.pkl")
        with open(pickle_file, 'wb') as f:
            pickle.dump(results, f)
        
        # Save text report
        self._save_text_report(results, save_id)
        
        # Save charts
        if save_charts:
            self._save_charts(results, save_id)
        
        print(f"Strategy saved with ID: {save_id}")
        return save_id
    
    def _save_text_report(self, results: Dict[str, Any], save_id: str) -> None:
        """
        Saves a text report.
        
        Args:
            results: Backtest results
            save_id: Save ID
        """
        from backtest.performance_metrics import PerformanceMetrics
        
        report = PerformanceMetrics.generate_performance_report(results)
        
        report_file = os.path.join(self.reports_dir, f"{save_id}_report.txt")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
    
    def _save_charts(self, results: Dict[str, Any], save_id: str) -> None:
        """
        Saves the charts.
        
        Args:
            results: Backtest results
            save_id: Save ID
        """
        try:
            from utils.visualizer import Visualizer
            
            # Main chart
            main_chart = os.path.join(self.charts_dir, f"{save_id}_main.html")
            fig = Visualizer.plot_backtest_results(results, save_path=main_chart)
            
            # Metrics chart
            metrics_chart = os.path.join(self.charts_dir, f"{save_id}_metrics.html")
            metrics_fig = Visualizer.plot_performance_metrics(results)
            metrics_fig.write_html(metrics_chart)
            
            # Drawdown chart
            drawdown_chart = os.path.join(self.charts_dir, f"{save_id}_drawdown.html")
            drawdown_fig = Visualizer.plot_drawdown(results)
            drawdown_fig.write_html(drawdown_chart)
            
        except Exception as e:
            print(f"Error while saving charts: {e}")
    
    def load_strategy_results(self, save_id: str) -> Optional[Dict[str, Any]]:
        """
        Loads the results of a saved strategy.
        
        Args:
            save_id: Save ID
            
        Returns:
            Loaded results or None if not found
        """
        pickle_file = os.path.join(self.strategies_dir, f"{save_id}.pkl")
        
        if not os.path.exists(pickle_file):
            print(f"Strategy not found: {save_id}")
            return None
        
        try:
            with open(pickle_file, 'rb') as f:
                results = pickle.load(f)
            print(f"Strategy loaded: {save_id}")
            return results
        except Exception as e:
            print(f"Error while loading: {e}")
            return None
    
    def list_saved_strategies(self) -> List[Dict[str, Any]]:
        """
        Lists all saved strategies.
        
        Returns:
            List of strategy metadata
        """
        strategies = []
        
        for file in os.listdir(self.strategies_dir):
            if file.endswith('.json'):
                try:
                    with open(os.path.join(self.strategies_dir, file), 'r', encoding='utf-8') as f:
                        strategy_data = json.load(f)
                    strategies.append(strategy_data)
                except Exception as e:
                    print(f"Error while loading {file}: {e}")
        
        # Sort by timestamp (most recent first)
        strategies.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return strategies
    
    def get_best_strategies(self, 
                          top_n: int = 5, 
                          metric: str = 'total_return') -> List[Dict[str, Any]]:
        """
        Returns the best strategies according to a metric.
        
        Args:
            top_n: Number of strategies to return
            metric: Metric for ranking
            
        Returns:
            List of best strategies
        """
        strategies = self.list_saved_strategies()
        
        # Sort by metric
        strategies.sort(
            key=lambda x: x.get('metrics', {}).get(metric, 0), 
            reverse=True
        )
        
        return strategies[:top_n]
    
    def delete_strategy(self, save_id: str) -> bool:
        """
        Deletes a saved strategy.
        
        Args:
            save_id: ID of the strategy to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            # Files to delete
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
            
            print(f"Strategy {save_id} deleted ({deleted_count} files)")
            return True
            
        except Exception as e:
            print(f"Error while deleting: {e}")
            return False
    
    def export_strategy_summary(self, output_file: str = None) -> str:
        """
        Exports a summary of all strategies.
        
        Args:
            output_file: Output file (optional)
            
        Returns:
            Path of created file
        """
        if output_file is None:
            output_file = os.path.join(self.results_dir, "strategies_summary.csv")
        
        strategies = self.list_saved_strategies()
        
        # Prepare data for CSV
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
        
        # Save as CSV
        df = pd.DataFrame(summary_data)
        df.to_csv(output_file, index=False)
        
        print(f"Summary exported: {output_file}")
        return output_file