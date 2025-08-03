"""
Strategy results persistence and management module.

This module provides the StrategySaver class for saving, loading, and managing
high-performing trading strategy results. It includes comprehensive file handling,
data serialization, and result management capabilities with robust error handling.

Classes:
    StrategySaver: Main class for strategy results persistence
    StrategySaveError: Custom exception for strategy saving errors
    StrategyLoadError: Custom exception for strategy loading errors
    StrategyFileError: Custom exception for file operation errors

Example:
    >>> from utils.strategy_saver import StrategySaver
    >>> saver = StrategySaver(results_dir="results")
    >>> save_id = saver.save_strategy_results(backtest_results)
    >>> loaded_results = saver.load_strategy_results(save_id)
"""

import json
import os
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path
from datetime import datetime
import pandas as pd
import logging

# Configure logging
logger = logging.getLogger(__name__)


class StrategySaveError(Exception):
    """Exception raised when strategy saving fails."""
    

    def __init__(self, message: str, save_id: Optional[str] = None, cause: Optional[Exception] = None) -> None:
        """
        Initialize StrategySaveError.
        
        Args:
            message: Error message describing the issue.
            save_id: The save ID that caused the error (optional).
            cause: The underlying exception that caused this error (optional).
        """
        self.save_id = save_id
        self.cause = cause
        super().__init__(message)


class StrategyLoadError(Exception):
    """Exception raised when strategy loading fails."""
    

    def __init__(self, message: str, save_id: Optional[str] = None, cause: Optional[Exception] = None) -> None:
        """
        Initialize StrategyLoadError.
        
        Args:
            message: Error message describing the issue.
            save_id: The save ID that caused the error (optional).
            cause: The underlying exception that caused this error (optional).
        """
        self.save_id = save_id
        self.cause = cause
        super().__init__(message)


class StrategyFileError(Exception):
    """Exception raised when file operations fail."""
    

    def __init__(self, message: str, file_path: Optional[str] = None, cause: Optional[Exception] = None) -> None:
        """
        Initialize StrategyFileError.
        
        Args:
            message: Error message describing the issue.
            file_path: The file path that caused the error (optional).
            cause: The underlying exception that caused this error (optional).
        """
        self.file_path = file_path
        self.cause = cause
        super().__init__(message)


class StrategySaver:
    """
    Class for saving and managing high-performing trading strategy results.
    
    This class provides comprehensive functionality for persisting strategy backtest
    results, including JSON serialization, text reports, chart generation, and
    result management. It handles data conversion, file operations, and provides
    methods for loading, listing, and analyzing saved strategies.
    
    Attributes:
        results_dir: Main directory for storing all strategy results.
        strategies_dir: Subdirectory for JSON strategy data files.
        reports_dir: Subdirectory for text reports.
        charts_dir: Subdirectory for HTML chart files.
        
    Example:
        >>> saver = StrategySaver(results_dir="results")
        >>> save_id = saver.save_strategy_results(backtest_results)
        >>> strategies = saver.list_saved_strategies()
        >>> best = saver.get_best_strategies(top_n=5)
    """
    
    # Required fields in strategy results
    REQUIRED_RESULT_FIELDS: List[str] = [
        'strategy', 'strategy_label', 'metrics', 'backtest_period', 
        'parameters', 'symbol'
    ]
    
    # File extensions for different result types
    FILE_EXTENSIONS: Dict[str, str] = {
        'json': '.json',
        'report': '_report.txt',
        'main_chart': '_main.html',
        'metrics_chart': '_metrics.html',
        'drawdown_chart': '_drawdown.html'
    }
    

    def __init__(self, results_dir: str = "results") -> None:
        """
        Initialize the StrategySaver with directory structure.
        
        Args:
            results_dir: Main directory for storing strategy results.
            
        Raises:
            StrategyFileError: If directory creation fails.
        """
        self.results_dir = Path(results_dir)
        
        # Define subdirectories
        self.strategies_dir = self.results_dir / "strategies"
        self.reports_dir = self.results_dir / "reports"
        self.charts_dir = self.results_dir / "charts"
        
        # Create directory structure
        self._create_directory_structure()
        
        logger.info(f"StrategySaver initialized with results directory: {self.results_dir}")
    

    def _create_directory_structure(self) -> None:
        """
        Create the required directory structure for storing results.
        
        Raises:
            StrategyFileError: If directory creation fails.
        """
        directories = [self.results_dir, self.strategies_dir, self.reports_dir, self.charts_dir]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Created directory: {directory}")
            except OSError as e:
                raise StrategyFileError(
                    f"Failed to create directory: {directory}",
                    file_path=str(directory),
                    cause=e
                ) from e
    

    def save_strategy_results(
        self,
        results: Dict[str, Any],
        save_charts: bool = True,
        overwrite: bool = False
    ) -> str:
        """
        Save comprehensive strategy backtest results to disk.
        
        Args:
            results: Dictionary containing backtest results with required fields.
            save_charts: Whether to generate and save HTML charts.
            overwrite: Whether to overwrite existing files with same save_id.
            
        Returns:
            Unique save ID for the saved strategy.
            
        Raises:
            StrategySaveError: If saving fails or required fields are missing.
            ValueError: If results dictionary is invalid.
            
        Example:
            >>> save_id = saver.save_strategy_results(backtest_results, save_charts=True)
            >>> print(f"Strategy saved with ID: {save_id}")
        """
        # Validate input results
        self._validate_results_structure(results)
        
        # Generate unique save ID
        save_id = self._generate_save_id(results)
        
        # Check for existing files if overwrite is False
        if not overwrite and self._save_id_exists(save_id):
            raise StrategySaveError(
                f"Strategy with save_id '{save_id}' already exists. Use overwrite=True to replace.",
                save_id=save_id
            )
        
        try:
            # Prepare serializable data
            save_data = self._prepare_save_data(results, save_id)
            
            # Save JSON data
            self._save_json_data(save_data, save_id)
            
            # Save text report
            self._save_text_report(results, save_id)
            
            # Save charts if requested
            if save_charts:
                self._save_charts(results, save_id)
            
            logger.info(f"Strategy results saved successfully with ID: {save_id}")
            return save_id
            
        except Exception as e:
            if isinstance(e, StrategySaveError):
                raise
            raise StrategySaveError(
                f"Unexpected error saving strategy results: {str(e)}",
                save_id=save_id,
                cause=e
            ) from e
    

    def _validate_results_structure(self, results: Dict[str, Any]) -> None:
        """
        Validate that results dictionary has required structure.
        
        Args:
            results: Results dictionary to validate.
            
        Raises:
            ValueError: If results structure is invalid.
        """
        if not isinstance(results, dict):
            raise ValueError("Results must be a dictionary")
        
        # Check for required fields
        missing_fields = [field for field in self.REQUIRED_RESULT_FIELDS if field not in results]
        if missing_fields:
            raise ValueError(f"Missing required fields in results: {missing_fields}")
        
        # Validate specific field types
        if not isinstance(results.get('strategy'), dict):
            raise ValueError("'strategy' field must be a dictionary")
        
        if not isinstance(results.get('metrics'), dict):
            raise ValueError("'metrics' field must be a dictionary")
        
        if not isinstance(results.get('parameters'), dict):
            raise ValueError("'parameters' field must be a dictionary")
        
        # Validate strategy has required 'name' field
        if 'name' not in results['strategy']:
            raise ValueError("Strategy dictionary must contain 'name' field")
    

    def _generate_save_id(self, results: Dict[str, Any]) -> str:
        """
        Generate a unique save ID for the strategy results.
        
        Args:
            results: Results dictionary containing strategy information.
            
        Returns:
            Unique save ID string.
        """
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d-%H%M%S")
        strategy_name = results['strategy']['name'].replace(' ', '-').replace('_', '-')
        symbol = results['symbol'].replace('-', '').replace('_', '')
        
        # Create safe filename components
        safe_strategy_name = ''.join(c for c in strategy_name if c.isalnum() or c in '-').lower()
        safe_symbol = ''.join(c for c in symbol if c.isalnum()).lower()
        
        save_id = f"{timestamp}--{safe_strategy_name}--{safe_symbol}"
        logger.debug(f"Generated save_id: {save_id}")
        return save_id
    

    def _save_id_exists(self, save_id: str) -> bool:
        """
        Check if a save_id already exists.
        
        Args:
            save_id: Save ID to check.
            
        Returns:
            True if save_id exists, False otherwise.
        """
        json_file = self.strategies_dir / f"{save_id}{self.FILE_EXTENSIONS['json']}"
        return json_file.exists()
    

    def _prepare_save_data(self, results: Dict[str, Any], save_id: str) -> Dict[str, Any]:
        """
        Prepare results data for JSON serialization.
        
        Args:
            results: Original results dictionary.
            save_id: Generated save ID.
            
        Returns:
            Dictionary ready for JSON serialization.
        """
        now = datetime.now()
        
        # Convert DataFrame to serializable format
        data_dict = None
        if 'data' in results and isinstance(results['data'], pd.DataFrame):
            data_dict = self._dataframe_to_dict(results['data'])
        
        # Convert Series to serializable format
        buy_signals_dict = None
        sell_signals_dict = None
        
        if 'buy_signals' in results and isinstance(results['buy_signals'], pd.Series):
            buy_signals_dict = self._series_to_dict(results['buy_signals'])
        
        if 'sell_signals' in results and isinstance(results['sell_signals'], pd.Series):
            sell_signals_dict = self._series_to_dict(results['sell_signals'])
        
        # Prepare complete save data
        save_data = {
            'save_id': save_id,
            'timestamp': now.strftime("%Y%m%d-%H%M%S"),
            'test_date': now.isoformat(),
            'strategy': results['strategy'],
            'strategy_label': results['strategy_label'],
            'metrics': results['metrics'],
            'backtest_period': results['backtest_period'],
            'parameters': results['parameters'],
            'symbol': results['symbol'],
            'data': data_dict,
            'buy_signals': buy_signals_dict,
            'sell_signals': sell_signals_dict,
            'metadata': {
                'saved_by': 'StrategySaver',
                'version': '1.0.0',
                'python_version': f"{pd.__version__}",  # Using pandas version as proxy
                'save_timestamp': now.isoformat()
            }
        }
        
        return save_data
    

    def _dataframe_to_dict(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Convert DataFrame to JSON-serializable dictionary.
        
        Args:
            df: DataFrame to convert.
            
        Returns:
            Dictionary with datetime index converted to strings.
        """
        return {
            col: {
                k.strftime('%Y-%m-%d %H:%M:%S') if hasattr(k, 'strftime') else str(k): v
                for k, v in df[col].items()
            }
            for col in df.columns
        }
    

    def _series_to_dict(self, series: pd.Series) -> Dict[str, Any]:
        """
        Convert Series to JSON-serializable dictionary.
        
        Args:
            series: Series to convert.
            
        Returns:
            Dictionary with datetime index converted to strings.
        """
        return {
            k.strftime('%Y-%m-%d %H:%M:%S') if hasattr(k, 'strftime') else str(k): v
            for k, v in series.items()
        }
    

    def _save_json_data(self, save_data: Dict[str, Any], save_id: str) -> None:
        """
        Save strategy data as JSON file.
        
        Args:
            save_data: Data to save.
            save_id: Save ID for filename.
            
        Raises:
            StrategyFileError: If JSON saving fails.
        """
        json_file = self.strategies_dir / f"{save_id}{self.FILE_EXTENSIONS['json']}"
        
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False, default=str)
            logger.debug(f"JSON data saved: {json_file}")
        except Exception as e:
            raise StrategyFileError(
                f"Failed to save JSON data: {json_file}",
                file_path=str(json_file),
                cause=e
            ) from e
    

    def _save_text_report(self, results: Dict[str, Any], save_id: str) -> None:
        """
        Save strategy results as text report.
        
        Args:
            results: Strategy results.
            save_id: Save ID for filename.
            
        Raises:
            StrategyFileError: If report saving fails.
        """
        report_file = self.reports_dir / f"{save_id}{self.FILE_EXTENSIONS['report']}"
        
        try:
            # Import here to avoid circular imports
            from backtest.performance_metrics import PerformanceMetrics
            
            report = PerformanceMetrics.generate_performance_report(results)
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.debug(f"Text report saved: {report_file}")
            
        except Exception as e:
            logger.warning(f"Failed to save text report: {e}")
            # Don't raise exception for report saving failure
    

    def _save_charts(self, results: Dict[str, Any], save_id: str) -> None:
        """
        Save strategy charts as HTML files.
        
        Args:
            results: Strategy results.
            save_id: Save ID for filenames.
        """
        try:
            # Import here to avoid circular imports
            from utils.visualizer import Visualizer
            
            # Save main chart
            main_chart_path = self.charts_dir / f"{save_id}{self.FILE_EXTENSIONS['main_chart']}"
            main_fig = Visualizer.plot_backtest_results(results)
            main_fig.write_html(str(main_chart_path))
            logger.debug(f"Main chart saved: {main_chart_path}")
            
            # Save metrics chart
            metrics_chart_path = self.charts_dir / f"{save_id}{self.FILE_EXTENSIONS['metrics_chart']}"
            metrics_fig = Visualizer.plot_performance_metrics(results)
            metrics_fig.write_html(str(metrics_chart_path))
            logger.debug(f"Metrics chart saved: {metrics_chart_path}")
            
            # Save drawdown chart
            drawdown_chart_path = self.charts_dir / f"{save_id}{self.FILE_EXTENSIONS['drawdown_chart']}"
            drawdown_fig = Visualizer.plot_drawdown(results)
            drawdown_fig.write_html(str(drawdown_chart_path))
            logger.debug(f"Drawdown chart saved: {drawdown_chart_path}")
            
        except Exception as e:
            logger.warning(f"Failed to save charts for {save_id}: {e}")
            # Don't raise exception for chart saving failure
    

    def load_strategy_results(self, save_id: str) -> Optional[Dict[str, Any]]:
        """
        Load saved strategy results from disk.
        
        Args:
            save_id: Unique identifier of the strategy to load.
            
        Returns:
            Dictionary containing the loaded strategy results, or None if not found.
            
        Raises:
            StrategyLoadError: If loading fails.
            
        Example:
            >>> results = saver.load_strategy_results("20240101-120000--sma-crossover--btcusd")
            >>> if results:
            ...     print(f"Loaded strategy: {results['strategy']['name']}")
        """
        json_file = self.strategies_dir / f"{save_id}{self.FILE_EXTENSIONS['json']}"
        
        if not json_file.exists():
            logger.warning(f"Strategy file not found: {save_id}")
            return None
        
        try:
            # Load JSON data
            with open(json_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            # Convert serialized data back to pandas objects
            results = self._deserialize_results(results)
            
            logger.info(f"Strategy loaded successfully: {save_id}")
            return results
            
        except Exception as e:
            raise StrategyLoadError(
                f"Failed to load strategy results: {save_id}",
                save_id=save_id,
                cause=e
            ) from e
    

    def _deserialize_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert serialized data back to pandas objects.
        
        Args:
            results: Serialized results dictionary.
            
        Returns:
            Results with pandas objects restored.
        """
        # Convert data dictionary back to DataFrame
        if results.get('data'):
            data_dict = results['data']
            df = pd.DataFrame()
            for col in data_dict:
                df[col] = pd.Series({
                    pd.Timestamp(k): v for k, v in data_dict[col].items()
                })
            results['data'] = df
        
        # Convert signals back to Series
        if results.get('buy_signals'):
            results['buy_signals'] = pd.Series({
                pd.Timestamp(k): v for k, v in results['buy_signals'].items()
            })
        
        if results.get('sell_signals'):
            results['sell_signals'] = pd.Series({
                pd.Timestamp(k): v for k, v in results['sell_signals'].items()
            })
        
        return results
    

    def list_saved_strategies(self, sort_by: str = 'timestamp') -> List[Dict[str, Any]]:
        """
        List all saved strategies with their metadata.
        
        Args:
            sort_by: Field to sort by ('timestamp', 'total_return', 'sharpe_ratio', etc.).
            
        Returns:
            List of strategy metadata dictionaries sorted by specified field.
            
        Raises:
            StrategyFileError: If listing fails.
            
        Example:
            >>> strategies = saver.list_saved_strategies(sort_by='total_return')
            >>> for strategy in strategies[:5]:  # Top 5
            ...     print(f"{strategy['strategy_name']}: {strategy['total_return']:.2%}")
        """
        strategies = []
        
        try:
            json_files = list(self.strategies_dir.glob(f"*{self.FILE_EXTENSIONS['json']}"))
            
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        strategy_data = json.load(f)
                    strategies.append(strategy_data)
                except Exception as e:
                    logger.warning(f"Error loading strategy file {json_file}: {e}")
                    continue
            
            # Sort strategies
            reverse_sort = sort_by in ['total_return', 'sharpe_ratio', 'win_rate', 'profit_factor']
            
            if sort_by == 'timestamp':
                strategies.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            elif sort_by in ['total_return', 'sharpe_ratio', 'win_rate', 'profit_factor', 'max_drawdown']:
                strategies.sort(
                    key=lambda x: x.get('metrics', {}).get(sort_by, 0),
                    reverse=reverse_sort
                )
            else:
                # Default to timestamp if unknown sort field
                strategies.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            logger.info(f"Listed {len(strategies)} saved strategies")
            return strategies
            
        except Exception as e:
            raise StrategyFileError(
                f"Failed to list saved strategies: {str(e)}",
                file_path=str(self.strategies_dir),
                cause=e
            ) from e
    

    def get_best_strategies(
        self,
        top_n: int = 5,
        metric: str = 'total_return',
        min_trades: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Get the best performing strategies based on a specific metric.
        
        Args:
            top_n: Number of top strategies to return.
            metric: Performance metric to rank by ('total_return', 'sharpe_ratio', etc.).
            min_trades: Minimum number of trades required for inclusion.
            
        Returns:
            List of top performing strategies.
            
        Raises:
            ValueError: If invalid parameters are provided.
            
        Example:
            >>> best = saver.get_best_strategies(top_n=3, metric='sharpe_ratio', min_trades=5)
            >>> for strategy in best:
            ...     print(f"{strategy['strategy_name']}: {strategy['metrics']['sharpe_ratio']:.2f}")
        """
        if top_n <= 0:
            raise ValueError("top_n must be positive")
        
        if min_trades < 0:
            raise ValueError("min_trades must be non-negative")
        
        strategies = self.list_saved_strategies()
        
        # Filter by minimum trades
        if min_trades > 0:
            strategies = [
                s for s in strategies
                if s.get('metrics', {}).get('total_trades', 0) >= min_trades
            ]
        
        # Sort by specified metric
        reverse_sort = metric not in ['max_drawdown']  # Most metrics are better when higher
        
        strategies.sort(
            key=lambda x: x.get('metrics', {}).get(metric, 0),
            reverse=reverse_sort
        )
        
        return strategies[:top_n]
    

    def delete_strategy(self, save_id: str, confirm: bool = False) -> bool:
        """
        Delete a saved strategy and all associated files.
        
        Args:
            save_id: ID of the strategy to delete.
            confirm: Confirmation flag to prevent accidental deletion.
            
        Returns:
            True if deletion was successful, False otherwise.
            
        Raises:
            StrategyFileError: If deletion fails.
            ValueError: If confirmation is not provided.
            
        Example:
            >>> success = saver.delete_strategy("20240101-120000--sma--btcusd", confirm=True)
            >>> if success:
            ...     print("Strategy deleted successfully")
        """
        if not confirm:
            raise ValueError("Must set confirm=True to delete strategy")
        
        # Define all possible files for this save_id
        files_to_delete = [
            self.strategies_dir / f"{save_id}{self.FILE_EXTENSIONS['json']}",
            self.reports_dir / f"{save_id}{self.FILE_EXTENSIONS['report']}",
            self.charts_dir / f"{save_id}{self.FILE_EXTENSIONS['main_chart']}",
            self.charts_dir / f"{save_id}{self.FILE_EXTENSIONS['metrics_chart']}",
            self.charts_dir / f"{save_id}{self.FILE_EXTENSIONS['drawdown_chart']}"
        ]
        
        deleted_count = 0
        errors = []
        
        for file_path in files_to_delete:
            if file_path.exists():
                try:
                    file_path.unlink()
                    deleted_count += 1
                    logger.debug(f"Deleted file: {file_path}")
                except Exception as e:
                    error_msg = f"Failed to delete {file_path}: {e}"
                    errors.append(error_msg)
                    logger.error(error_msg)
        
        if errors:
            raise StrategyFileError(
                f"Partial deletion failure for {save_id}. Errors: {'; '.join(errors)}"
            )
        
        if deleted_count == 0:
            logger.warning(f"No files found to delete for save_id: {save_id}")
            return False
        
        logger.info(f"Strategy {save_id} deleted successfully ({deleted_count} files)")
        return True
    

    def export_strategy_summary(self, output_file: Optional[str] = None) -> str:
        """
        Export a CSV summary of all saved strategies.
        
        Args:
            output_file: Path for the output CSV file. If None, uses default location.
            
        Returns:
            Path to the created CSV file.
            
        Raises:
            StrategyFileError: If export fails.
            
        Example:
            >>> csv_path = saver.export_strategy_summary("strategy_summary.csv")
            >>> print(f"Summary exported to: {csv_path}")
        """
        if output_file is None:
            output_file = str(self.results_dir / "strategies_summary.csv")
        
        try:
            strategies = self.list_saved_strategies()
            
            # Prepare data for CSV
            summary_data = []
            for strategy in strategies:
                metrics = strategy.get('metrics', {})
                row = {
                    'save_id': strategy.get('save_id', ''),
                    'timestamp': strategy.get('timestamp', ''),
                    'test_date': strategy.get('test_date', ''),
                    'strategy_name': strategy.get('strategy', {}).get('name', ''),
                    'symbol': strategy.get('symbol', ''),
                    'total_return': metrics.get('total_return', 0),
                    'sharpe_ratio': metrics.get('sharpe_ratio', 0),
                    'max_drawdown': metrics.get('max_drawdown', 0),
                    'win_rate': metrics.get('win_rate', 0),
                    'total_trades': metrics.get('total_trades', 0),
                    'final_value': metrics.get('final_value', 0),
                    'profit_factor': metrics.get('profit_factor', 0),
                    'alpha': metrics.get('alpha', 0),
                    'beta': metrics.get('beta', 0)
                }
                summary_data.append(row)
            
            # Save as CSV
            df = pd.DataFrame(summary_data)
            df.to_csv(output_file, index=False)
            
            logger.info(f"Strategy summary exported: {output_file} ({len(summary_data)} strategies)")
            return output_file
            
        except Exception as e:
            raise StrategyFileError(
                f"Failed to export strategy summary: {str(e)}",
                file_path=output_file,
                cause=e
            ) from e
    
    
    def get_storage_info(self) -> Dict[str, Any]:
        """
        Get information about storage usage and file counts.
        
        Returns:
            Dictionary with storage information.
        """
        try:
            info = {
                'results_dir': str(self.results_dir),
                'total_strategies': 0,
                'total_size_bytes': 0,
                'directories': {}
            }
            
            # Analyze each subdirectory
            for dir_name, dir_path in [
                ('strategies', self.strategies_dir),
                ('reports', self.reports_dir),
                ('charts', self.charts_dir)
            ]:
                if dir_path.exists():
                    files = list(dir_path.iterdir())
                    total_size = sum(f.stat().st_size for f in files if f.is_file())
                    
                    info['directories'][dir_name] = {
                        'path': str(dir_path),
                        'file_count': len([f for f in files if f.is_file()]),
                        'size_bytes': total_size,
                        'size_mb': round(total_size / (1024 * 1024), 2)
                    }
                    
                    info['total_size_bytes'] += total_size
                    
                    if dir_name == 'strategies':
                        info['total_strategies'] = info['directories'][dir_name]['file_count']
            
            info['total_size_mb'] = round(info['total_size_bytes'] / (1024 * 1024), 2)
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting storage info: {e}")
            return {
                'results_dir': str(self.results_dir),
                'error': str(e)
            }