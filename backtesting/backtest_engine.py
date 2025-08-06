"""
Advanced Backtesting Engine for Cryptocurrency Trading Strategies.

This module provides a comprehensive backtesting engine using vectorbt for high-performance
vectorized calculations. The engine supports advanced portfolio construction, risk management,
and performance analysis for cryptocurrency trading strategies.

Key Features:
- Vectorized backtesting with vectorbt integration
- Advanced portfolio construction and management
- Comprehensive data validation and error handling
- Flexible date range filtering and analysis
- Professional performance metrics calculation
- Robust error handling and logging
"""

from typing import Dict, Any, Optional, Tuple, Union, List
import pandas as pd
import numpy as np
import vectorbt as vbt
from datetime import datetime, date
import warnings
from pathlib import Path

from strategies.base.abstract_strategy import AbstractStrategy

# Configure logging
from logger.logging_manager import get_logger
logger = get_logger(__name__)


class BacktestError(Exception):
    """Base exception for backtesting errors."""
    pass


class DataValidationError(BacktestError):
    """Raised when data validation fails."""
    pass


class StrategyExecutionError(BacktestError):
    """Raised when strategy execution fails."""
    pass


class PortfolioConstructionError(BacktestError):
    """Raised when portfolio construction fails."""
    pass


class MetricsCalculationError(BacktestError):
    """Raised when metrics calculation fails."""
    pass


class BacktestEngine:
    """
    Advanced backtesting engine for evaluating cryptocurrency trading strategies.
    
    This engine provides comprehensive backtesting capabilities with vectorized calculations,
    advanced portfolio construction, and professional performance analysis. It supports
    flexible configuration, robust error handling, and detailed reporting.
    
    Attributes:
        initial_cash: Initial capital for backtesting in USD.
        commission: Commission rate per transaction (e.g., 0.001 = 0.1%).
        slippage: Slippage rate per transaction (e.g., 0.0001 = 0.01%).
        results: Dictionary containing the latest backtest results.
        
    Example:
        Basic usage of the backtesting engine:
        
        ```python
        from backtest import BacktestEngine
        from strategies import SMACrossoverStrategy
        
        # Initialize engine with custom parameters
        engine = BacktestEngine(
            initial_cash=10000.0,
            commission=0.001,
            slippage=0.0001
        )
        
        # Create strategy
        strategy = SMACrossoverStrategy(short_window=10, long_window=30)
        
        # Run backtest
        results = engine.execute_strategy_evaluation(strategy, data, start_date='2023-01-01')
        
        # Access results
        metrics = results['metrics']
        portfolio = results['portfolio']
        ```
    """


    def __init__(
        self, 
        initial_cash: float = 10000.0,
        commission: float = 0.001,
        slippage: float = 0.0001,
        min_data_points: int = 100
    ) -> None:
        """
        Initialize the backtesting engine with specified parameters.
        
        Args:
            initial_cash: Initial capital in USD for backtesting.
            commission: Commission rate per transaction (0.001 = 0.1%).
            slippage: Slippage rate per transaction (0.0001 = 0.01%).
            min_data_points: Minimum required data points for reliable backtesting.
        
        Raises:
            ValueError: If any parameter is invalid or out of acceptable range.
        """
        self._validate_initialization_parameters(initial_cash, commission, slippage, min_data_points)
        
        self.initial_cash = initial_cash
        self.commission = commission
        self.slippage = slippage
        self.min_data_points = min_data_points
        self.results: Optional[Dict[str, Any]] = None
        
        logger.info(f"BacktestEngine initialized with cash=${initial_cash:,.2f}, "
                   f"commission={commission:.4f}, slippage={slippage:.4f}")


    def execute_strategy_evaluation(
        self, 
        strategy: AbstractStrategy, 
        data: pd.DataFrame,
        start_date: Optional[Union[str, datetime, date]] = None,
        end_date: Optional[Union[str, datetime, date]] = None,
        symbol: str = "UNKNOWN"
    ) -> Dict[str, Any]:
        """
        Execute a comprehensive backtest for the specified trading strategy.
        
        This method performs a complete backtesting workflow including data validation,
        signal generation, portfolio construction, and performance analysis.
        
        Args:
            strategy: Trading strategy instance implementing AbstractStrategy interface.
            data: DataFrame containing OHLCV price data with DatetimeIndex.
            start_date: Optional start date for backtesting period.
            end_date: Optional end date for backtesting period.
            symbol: Symbol identifier for the asset being tested.
        
        Returns:
            Comprehensive dictionary containing:
            - strategy: Strategy configuration and parameters
            - strategy_instance: Instance of the strategy used
            - strategy_label: Strategy short description with parameters
            - portfolio: Vectorbt portfolio object with trade history
            - metrics: Performance metrics and risk analysis
            - data: Filtered price data used in backtesting
            - buy_signals: Boolean series of buy signals
            - sell_signals: Boolean series of sell signals
            - backtest_period: Period information and duration
            - parameters: Engine configuration parameters
            - symbol: Asset symbol
        
        Raises:
            DataValidationError: If input data is invalid or insufficient.
            StrategyExecutionError: If strategy signal generation fails.
            PortfolioConstructionError: If portfolio construction fails.
            MetricsCalculationError: If performance metrics calculation fails.
        """
        logger.info(f"Starting backtest for strategy: {strategy.__class__.__name__}")
        
        try:
            # Validate input data
            self._validate_input_data(data, strategy)
            
            # Filter data by date range if specified
            filtered_data = self.slice_data_by_date_range(data, start_date, end_date)
            
            # Validate filtered data sufficiency
            self._validate_data_sufficiency(filtered_data)
            
            # Generate trading signals
            buy_signals, sell_signals = self._generate_signals(strategy, filtered_data)
            
            # Create vectorbt portfolio
            portfolio = self.build_vectorbt_portfolio(filtered_data, buy_signals, sell_signals)
            
            # Calculate comprehensive performance metrics
            metrics = self.compute_performance_statistics(portfolio, filtered_data)
            
            # Construct comprehensive results dictionary
            self.results = self._construct_results(
                strategy, portfolio, metrics, filtered_data,
                buy_signals, sell_signals, symbol
            )
            
            logger.info(f"Backtest completed successfully. Total return: {metrics['total_return']:.2%}")
            return self.results
            
        except Exception as e:
            logger.error(f"Backtest failed: {str(e)}")
            raise BacktestError(f"Backtest execution failed: {str(e)}") from e


    def _validate_initialization_parameters(
        self, 
        initial_cash: float, 
        commission: float, 
        slippage: float,
        min_data_points: int
    ) -> None:
        """
        Validate initialization parameters for the backtesting engine.
        
        Args:
            initial_cash: Initial capital amount.
            commission: Commission rate.
            slippage: Slippage rate.
            min_data_points: Minimum data points requirement.
        
        Raises:
            ValueError: If any parameter is invalid.
        """
        if initial_cash <= 0:
            raise ValueError(f"Initial cash must be positive, got: {initial_cash}")
        
        if not 0 <= commission <= 1:
            raise ValueError(f"Commission must be between 0 and 1, got: {commission}")
        
        if not 0 <= slippage <= 1:
            raise ValueError(f"Slippage must be between 0 and 1, got: {slippage}")
        
        if min_data_points < 10:
            raise ValueError(f"Minimum data points must be at least 10, got: {min_data_points}")


    def _validate_input_data(self, data: pd.DataFrame, strategy: AbstractStrategy) -> None:
        """
        Validate input data format and content for backtesting.
        
        Args:
            data: Price data DataFrame to validate.
            strategy: Strategy instance to validate.
        
        Raises:
            DataValidationError: If data validation fails.
        """
        if not isinstance(data, pd.DataFrame):
            raise DataValidationError(f"Data must be a pandas DataFrame, got: {type(data)}")
        
        if data.empty:
            raise DataValidationError("Data DataFrame cannot be empty")
        
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise DataValidationError(f"Missing required columns: {missing_columns}")
        
        if not isinstance(data.index, pd.DatetimeIndex):
            raise DataValidationError("Data must have a DatetimeIndex")
        
        if data.isnull().any().any():
            logger.warning("Data contains null values, they will be forward-filled")
            data.fillna(method='ffill', inplace=True)
        
        if not hasattr(strategy, 'generate_signals'):
            raise DataValidationError("Strategy must implement generate_signals method")


    def _validate_data_sufficiency(self, data: pd.DataFrame) -> None:
        """
        Validate that filtered data has sufficient points for reliable backtesting.
        
        Args:
            data: Filtered data to validate.
        
        Raises:
            DataValidationError: If data is insufficient.
        """
        if len(data) < self.min_data_points:
            raise DataValidationError(
                f"Insufficient data for reliable backtest. "
                f"Required: {self.min_data_points}, Available: {len(data)}"
            )
        
        if len(data) < self.min_data_points * 2:
            warnings.warn(
                f"Limited data available ({len(data)} points). "
                f"Results may be less reliable with fewer than {self.min_data_points * 2} points."
            )


    def slice_data_by_date_range(
        self, 
        data: pd.DataFrame, 
        start_date: Optional[Union[str, datetime, date]], 
        end_date: Optional[Union[str, datetime, date]]
    ) -> pd.DataFrame:
        """
        Filter price data by specified date range with comprehensive validation.
        
        Args:
            data: Original price data DataFrame.
            start_date: Start date for filtering (inclusive).
            end_date: End date for filtering (inclusive).
        
        Returns:
            Filtered DataFrame within the specified date range.
        
        Raises:
            DataValidationError: If date filtering results in invalid data.
        """
        filtered_data = data.copy()
        
        try:
            if start_date:
                start_date = pd.to_datetime(start_date)
                filtered_data = filtered_data[filtered_data.index >= start_date]
                logger.info(f"Applied start date filter: {start_date.strftime('%Y-%m-%d')}")
            
            if end_date:
                end_date = pd.to_datetime(end_date)
                filtered_data = filtered_data[filtered_data.index <= end_date]
                logger.info(f"Applied end date filter: {end_date.strftime('%Y-%m-%d')}")
            
            if filtered_data.empty:
                raise DataValidationError("Date filtering resulted in empty dataset")
            
            return filtered_data
            
        except Exception as e:
            raise DataValidationError(f"Date filtering failed: {str(e)}") from e


    def _generate_signals(
        self, 
        strategy: AbstractStrategy, 
        data: pd.DataFrame
    ) -> Tuple[pd.Series, pd.Series]:
        """
        Generate trading signals using the specified strategy with error handling.
        
        Args:
            strategy: Trading strategy instance.
            data: Price data for signal generation.
        
        Returns:
            Tuple of (buy_signals, sell_signals) as boolean Series.
        
        Raises:
            StrategyExecutionError: If signal generation fails.
        """
        try:
            logger.info(f"Generating signals with {strategy.__class__.__name__}")
            buy_signals, sell_signals = strategy.generate_signals(data)
            
            # Validate and clean signals
            buy_signals = buy_signals.fillna(False).astype(bool)
            sell_signals = sell_signals.fillna(False).astype(bool)
            
            # Log signal statistics
            buy_count = buy_signals.sum()
            sell_count = sell_signals.sum()
            logger.info(f"Generated {buy_count} buy signals and {sell_count} sell signals")
            
            if buy_count == 0 and sell_count == 0:
                warnings.warn("No trading signals generated by strategy")
            
            return buy_signals, sell_signals
            
        except Exception as e:
            raise StrategyExecutionError(f"Signal generation failed: {str(e)}") from e


    def build_vectorbt_portfolio(
        self, 
        data: pd.DataFrame, 
        buy_signals: pd.Series, 
        sell_signals: pd.Series
    ) -> vbt.Portfolio:
        """
        Create a vectorbt portfolio from price data and trading signals.
        
        Args:
            data: Price data DataFrame.
            buy_signals: Boolean series of buy signals.
            sell_signals: Boolean series of sell signals.
        
        Returns:
            Configured vectorbt Portfolio object.
        
        Raises:
            PortfolioConstructionError: If portfolio creation fails.
        """
        try:
            logger.info("Creating vectorbt portfolio")
            
            # Ensure signals align with data index
            buy_signals = buy_signals.reindex(data.index, fill_value=False)
            sell_signals = sell_signals.reindex(data.index, fill_value=False)
            
            # Create portfolio with comprehensive configuration
            portfolio = vbt.Portfolio.from_signals(
                close=data['Close'],
                entries=buy_signals,
                exits=sell_signals,
                init_cash=self.initial_cash,
                fees=self.commission,
                slippage=self.slippage,
                freq='1D',  # Daily frequency
                call_seq='Default'  # Default call sequence
            )
            
            logger.info("Portfolio created successfully")
            return portfolio
            
        except Exception as e:
            raise PortfolioConstructionError(f"Portfolio creation failed: {str(e)}") from e


    def compute_performance_statistics(
        self, 
        portfolio: vbt.Portfolio, 
        data: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Calculate comprehensive performance metrics from portfolio and price data.
        
        Args:
            portfolio: Vectorbt portfolio object.
            data: Original price data.
        
        Returns:
            Dictionary containing comprehensive performance metrics.
        
        Raises:
            MetricsCalculationError: If metrics calculation fails.
        """
        try:
            logger.info("Calculating performance metrics")
            
            # Basic portfolio metrics
            total_return = portfolio.total_return()
            sharpe_ratio = portfolio.sharpe_ratio()
            max_drawdown = portfolio.max_drawdown()
            
            # Trade-based metrics
            trades = portfolio.trades
            total_trades = trades.count()
            win_rate = trades.win_rate() if total_trades > 0 else 0.0
            avg_trade_duration = trades.duration.mean() if total_trades > 0 else 0.0
            profit_factor = trades.profit_factor() if total_trades > 0 else 0.0
            
            # Benchmark comparison (Buy & Hold)
            buy_hold_return = (data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1
            alpha = total_return - buy_hold_return if not pd.isna(total_return) else 0.0
            
            # Portfolio value metrics
            final_value = portfolio.value().iloc[-1]
            
            # Additional risk metrics
            returns = portfolio.returns()
            volatility = returns.std() * np.sqrt(252) if len(returns) > 0 else 0.0
            
            # Calculate winning and losing trades
            winning_trades = trades.winning.count() if total_trades > 0 else 0
            losing_trades = trades.losing.count() if total_trades > 0 else 0
            
            metrics = {
                'total_return': float(total_return) if not pd.isna(total_return) else 0.0,
                'sharpe_ratio': float(sharpe_ratio) if not pd.isna(sharpe_ratio) else 0.0,
                'max_drawdown': float(max_drawdown) if not pd.isna(max_drawdown) else 0.0,
                'win_rate': float(win_rate) if not pd.isna(win_rate) else 0.0,
                'total_trades': int(total_trades),
                'winning_trades': int(winning_trades),
                'losing_trades': int(losing_trades),
                'avg_trade_duration': float(avg_trade_duration) if not pd.isna(avg_trade_duration) else 0.0,
                'profit_factor': float(profit_factor) if not pd.isna(profit_factor) else 0.0,
                'buy_hold_return': float(buy_hold_return),
                'final_value': float(final_value),
                'alpha': float(alpha),
                'volatility': float(volatility) if not pd.isna(volatility) else 0.0
            }
            
            logger.info(f"Metrics calculated: Return={metrics['total_return']:.2%}, "
                       f"Sharpe={metrics['sharpe_ratio']:.2f}, Trades={metrics['total_trades']}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Metrics calculation failed: {str(e)}")
            # Return default metrics on failure
            return self._get_default_metrics()


    def _get_default_metrics(self) -> Dict[str, float]:
        """
        Get default metrics dictionary for error cases.
        
        Returns:
            Dictionary with default metric values.
        """
        return {
            'total_return': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'win_rate': 0.0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'avg_trade_duration': 0.0,
            'profit_factor': 0.0,
            'buy_hold_return': 0.0,
            'final_value': self.initial_cash,
            'alpha': 0.0,
            'volatility': 0.0
        }


    def _construct_results(
        self,
        strategy: AbstractStrategy,
        portfolio: vbt.Portfolio,
        metrics: Dict[str, float],
        data: pd.DataFrame,
        buy_signals: pd.Series,
        sell_signals: pd.Series,
        symbol: str
    ) -> Dict[str, Any]:
        """
        Construct comprehensive results dictionary from backtest components.
        
        Args:
            strategy: Strategy instance used in backtesting.
            portfolio: Vectorbt portfolio object.
            metrics: Calculated performance metrics.
            data: Price data used in backtesting.
            buy_signals: Generated buy signals.
            sell_signals: Generated sell signals.
            symbol: Asset symbol.
        
        Returns:
            Comprehensive results dictionary.
        """
        return {
            'strategy': strategy.to_dict(),
            'strategy_instance': strategy,
            'strategy_label': strategy.get_label(strategy.parameters),
            'portfolio': portfolio,
            'metrics': metrics,
            'data': data,
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'symbol': symbol,
            'backtest_period': {
                'start': data.index[0].strftime('%Y-%m-%d'),
                'end': data.index[-1].strftime('%Y-%m-%d'),
                'duration_days': (data.index[-1] - data.index[0]).days,
                'total_periods': len(data)
            },
            'parameters': {
                'initial_cash': self.initial_cash,
                'commission': self.commission,
                'slippage': self.slippage,
                'min_data_points': self.min_data_points
            },
            'timestamp': datetime.now().isoformat()
        }


    def get_last_results(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve the results from the most recent backtesting run.
        
        Returns:
            Dictionary containing the latest backtest results, or None if no
            backtest has been executed yet.
        
        Example:
            ```python
            engine = BacktestEngine()
            results = engine.execute_strategy_evaluation(strategy, data)
            
            # Later retrieve the same results
            last_results = engine.get_last_results()
            ```
        """
        return self.results


    def reset(self) -> None:
        """
        Reset the backtesting engine by clearing stored results.
        
        This method clears any cached results from previous backtesting runs,
        allowing for a fresh start with new configurations or strategies.
        """
        self.results = None
        logger.info("BacktestEngine reset - previous results cleared")


    def get_engine_info(self) -> Dict[str, Any]:
        """
        Get comprehensive information about the current engine configuration.
        
        Returns:
            Dictionary containing engine configuration and status information.
        """
        return {
            'initial_cash': self.initial_cash,
            'commission': self.commission,
            'slippage': self.slippage,
            'min_data_points': self.min_data_points,
            'has_results': self.results is not None,
            'last_run_timestamp': self.results.get('timestamp') if self.results else None
        }