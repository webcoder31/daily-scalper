"""
Advanced Performance Metrics and Analysis for Trading Strategy Backtesting.

This module provides comprehensive performance analysis capabilities for cryptocurrency
trading strategies, including advanced risk metrics, portfolio analysis, strategy
comparison, and professional reporting tools.

Key Features:
- Advanced performance metrics calculation (Sharpe, Sortino, Calmar ratios)
- Risk analysis with VaR, volatility, and drawdown metrics
- Strategy comparison and ranking algorithms
- Professional performance reporting
- Comprehensive error handling and validation
- Statistical analysis and significance testing
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import vectorbt as vbt
from dataclasses import dataclass

# Configure logging
from logger.logging_manager import get_logger
logger = get_logger(__name__)


class PerformanceMetricsError(Exception):
    """Base exception for performance metrics errors."""
    pass


class MetricsCalculationError(PerformanceMetricsError):
    """Raised when metrics calculation fails."""
    pass


class DataValidationError(PerformanceMetricsError):
    """Raised when input data validation fails."""
    pass


class ReportGenerationError(PerformanceMetricsError):
    """Raised when report generation fails."""
    pass


class StrategyComparisonError(PerformanceMetricsError):
    """Raised when strategy comparison fails."""
    pass


@dataclass
class ProfitabilityCriteria:
    """
    Configuration class for strategy profitability evaluation criteria.
    
    Attributes:
        min_return: Minimum required total return (e.g., 0.1 = 10%).
        min_sharpe: Minimum required Sharpe ratio.
        max_drawdown: Maximum acceptable drawdown (e.g., 0.2 = 20%).
        min_trades: Minimum number of trades for statistical significance.
        min_win_rate: Minimum required win rate (e.g., 0.4 = 40%).
    """
    min_return: float = 0.1
    min_sharpe: float = 1.0
    max_drawdown: float = 0.2
    min_trades: int = 5
    min_win_rate: float = 0.3


class PerformanceAnalyzer:
    """
    Advanced performance metrics calculator for trading strategy analysis.
    
    This class provides comprehensive performance analysis capabilities including
    advanced risk metrics, statistical analysis, strategy comparison, and
    professional reporting tools for cryptocurrency trading strategies.
    
    Example:
        Basic usage of performance metrics:
        
        ```python
        from backtest import PerformanceAnalyzer
        
        # Calculate advanced metrics
        advanced_metrics = PerformanceAnalyzer.compute_extended_performance_stats(results)
        
        # Check profitability
        is_profitable = PerformanceAnalyzer.meets_profitability_criteria(advanced_metrics)
        
        # Generate report
        report = PerformanceAnalyzer.create_detailed_analysis_report(results)
        
        # Compare strategies
        ranked_strategies = PerformanceAnalyzer.sort_strategies_by_performance(strategy_results)
        ```
    """


    @staticmethod
    def compute_extended_performance_stats(results: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate comprehensive advanced performance metrics from backtest results.
        
        This method computes a wide range of performance and risk metrics including
        volatility, risk-adjusted returns, drawdown analysis, and statistical measures.
        
        Args:
            results: Dictionary containing backtest results with portfolio and metrics.
        
        Returns:
            Dictionary containing all basic and advanced performance metrics.
        
        Raises:
            MetricsCalculationError: If metrics calculation fails.
            DataValidationError: If input data is invalid.
        """
        try:
            logger.info("Calculating advanced performance metrics")
            
            # Validate input data
            PerformanceAnalyzer._validate_results_data(results)
            
            portfolio = results['portfolio']
            metrics = results['metrics'].copy()
            
            # Get portfolio returns for advanced calculations
            returns = portfolio.returns()
            
            if len(returns) == 0:
                logger.warning("No returns data available for advanced metrics")
                return metrics
            
            # Calculate advanced risk metrics
            advanced_metrics = PerformanceAnalyzer._calculate_risk_metrics(returns, metrics)
            
            # Calculate additional portfolio metrics
            portfolio_metrics = PerformanceAnalyzer._calculate_portfolio_metrics(portfolio, returns)
            
            # Calculate benchmark comparison metrics
            benchmark_metrics = PerformanceAnalyzer._calculate_benchmark_metrics(
                results.get('data'), returns, metrics
            )
            
            # Combine all metrics
            metrics.update(advanced_metrics)
            metrics.update(portfolio_metrics)
            metrics.update(benchmark_metrics)
            
            logger.info(f"Advanced metrics calculated successfully. "
                       f"Volatility: {metrics.get('volatility', 0):.2%}, "
                       f"Sortino: {metrics.get('sortino_ratio', 0):.2f}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Advanced metrics calculation failed: {str(e)}")
            raise MetricsCalculationError(f"Failed to calculate advanced metrics: {str(e)}") from e


    @staticmethod
    def _validate_results_data(results: Dict[str, Any]) -> None:
        """
        Validate backtest results data structure and content.
        
        Args:
            results: Backtest results dictionary to validate.
        
        Raises:
            DataValidationError: If validation fails.
        """
        required_keys = ['portfolio', 'metrics']
        missing_keys = [key for key in required_keys if key not in results]
        if missing_keys:
            raise DataValidationError(f"Missing required keys in results: {missing_keys}")
        
        if not hasattr(results['portfolio'], 'returns'):
            raise DataValidationError("Portfolio object must have returns method")
        
        if not isinstance(results['metrics'], dict):
            raise DataValidationError("Metrics must be a dictionary")


    @staticmethod
    def _calculate_risk_metrics(returns: pd.Series, base_metrics: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate advanced risk metrics from returns series.
        
        Args:
            returns: Portfolio returns series.
            base_metrics: Base metrics dictionary.
        
        Returns:
            Dictionary of advanced risk metrics.
        """
        risk_metrics = {}
        
        try:
            # Annualized volatility
            volatility = returns.std() * np.sqrt(252)
            risk_metrics['volatility'] = float(volatility) if not pd.isna(volatility) else 0.0
            
            # Calmar ratio (annualized return / max drawdown)
            annualized_return = base_metrics.get('total_return', 0) * 252 / len(returns) if len(returns) > 0 else 0
            max_dd = abs(base_metrics.get('max_drawdown', 0))
            calmar_ratio = annualized_return / max_dd if max_dd > 0 else 0.0
            risk_metrics['calmar_ratio'] = float(calmar_ratio)
            
            # Sortino ratio (downside deviation)
            downside_returns = returns[returns < 0]
            if len(downside_returns) > 0:
                downside_deviation = downside_returns.std() * np.sqrt(252)
                sortino_ratio = annualized_return / downside_deviation if downside_deviation > 0 else 0.0
            else:
                sortino_ratio = 0.0
            risk_metrics['sortino_ratio'] = float(sortino_ratio)
            
            # Value at Risk (VaR) at different confidence levels
            if len(returns) > 0:
                risk_metrics['var_95'] = float(np.percentile(returns, 5))
                risk_metrics['var_99'] = float(np.percentile(returns, 1))
                risk_metrics['cvar_95'] = float(returns[returns <= np.percentile(returns, 5)].mean())
            else:
                risk_metrics.update({'var_95': 0.0, 'var_99': 0.0, 'cvar_95': 0.0})
            
            # Skewness and Kurtosis
            if len(returns) > 3:
                risk_metrics['skewness'] = float(returns.skew())
                risk_metrics['kurtosis'] = float(returns.kurtosis())
            else:
                risk_metrics.update({'skewness': 0.0, 'kurtosis': 0.0})
            
        except Exception as e:
            logger.warning(f"Some risk metrics calculation failed: {str(e)}")
            # Fill with default values for failed calculations
            default_risk_metrics = {
                'volatility': 0.0, 'calmar_ratio': 0.0, 'sortino_ratio': 0.0,
                'var_95': 0.0, 'var_99': 0.0, 'cvar_95': 0.0,
                'skewness': 0.0, 'kurtosis': 0.0
            }
            risk_metrics.update({k: v for k, v in default_risk_metrics.items() if k not in risk_metrics})
        
        return risk_metrics


    @staticmethod
    def _calculate_portfolio_metrics(portfolio: vbt.Portfolio, returns: pd.Series) -> Dict[str, float]:
        """
        Calculate additional portfolio-specific metrics.
        
        Args:
            portfolio: Vectorbt portfolio object.
            returns: Portfolio returns series.
        
        Returns:
            Dictionary of portfolio metrics.
        """
        portfolio_metrics = {}
        
        try:
            # Trade analysis
            trades = portfolio.trades
            if trades.count() > 0:
                portfolio_metrics['avg_win'] = float(trades.winning.pnl.mean()) if trades.winning.count() > 0 else 0.0
                portfolio_metrics['avg_loss'] = float(trades.losing.pnl.mean()) if trades.losing.count() > 0 else 0.0
                portfolio_metrics['largest_win'] = float(trades.winning.pnl.max()) if trades.winning.count() > 0 else 0.0
                portfolio_metrics['largest_loss'] = float(trades.losing.pnl.min()) if trades.losing.count() > 0 else 0.0
                portfolio_metrics['win_loss_ratio'] = float(
                    abs(portfolio_metrics['avg_win'] / portfolio_metrics['avg_loss'])
                    if portfolio_metrics['avg_loss'] != 0 else 0.0
                )
            else:
                portfolio_metrics.update({
                    'avg_win': 0.0, 'avg_loss': 0.0, 'largest_win': 0.0,
                    'largest_loss': 0.0, 'win_loss_ratio': 0.0
                })
            
            # Exposure and utilization metrics
            portfolio_metrics['market_exposure'] = float(
                portfolio.positions.coverage() if hasattr(portfolio.positions, 'coverage') else 0.0
            )
            
            # Drawdown analysis
            drawdowns = portfolio.drawdowns
            if drawdowns.count() > 0:
                portfolio_metrics['avg_drawdown'] = float(drawdowns.drawdown.mean())
                portfolio_metrics['max_drawdown_duration'] = float(drawdowns.duration.max())
                portfolio_metrics['recovery_factor'] = float(
                    portfolio.total_return() / abs(portfolio.max_drawdown())
                    if portfolio.max_drawdown() != 0 else 0.0
                )
            else:
                portfolio_metrics.update({
                    'avg_drawdown': 0.0, 'max_drawdown_duration': 0.0, 'recovery_factor': 0.0
                })
            
        except Exception as e:
            logger.warning(f"Portfolio metrics calculation failed: {str(e)}")
            # Provide default values
            default_portfolio_metrics = {
                'avg_win': 0.0, 'avg_loss': 0.0, 'largest_win': 0.0, 'largest_loss': 0.0,
                'win_loss_ratio': 0.0, 'market_exposure': 0.0, 'avg_drawdown': 0.0,
                'max_drawdown_duration': 0.0, 'recovery_factor': 0.0
            }
            portfolio_metrics.update({k: v for k, v in default_portfolio_metrics.items() if k not in portfolio_metrics})
        
        return portfolio_metrics


    @staticmethod
    def _calculate_benchmark_metrics(
        data: Optional[pd.DataFrame], 
        returns: pd.Series, 
        base_metrics: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate benchmark comparison metrics.
        
        Args:
            data: Price data DataFrame.
            returns: Portfolio returns series.
            base_metrics: Base metrics dictionary.
        
        Returns:
            Dictionary of benchmark comparison metrics.
        """
        benchmark_metrics = {}
        
        try:
            if data is not None and 'Close' in data.columns and len(data) > 1:
                # Calculate benchmark (buy & hold) metrics
                benchmark_return = (data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1
                benchmark_metrics['benchmark_return'] = float(benchmark_return)
                
                # Information ratio (excess return / tracking error)
                excess_returns = returns - (benchmark_return / len(returns))
                tracking_error = excess_returns.std() * np.sqrt(252)
                information_ratio = (
                    (base_metrics.get('total_return', 0) - benchmark_return) / tracking_error
                    if tracking_error > 0 else 0.0
                )
                benchmark_metrics['information_ratio'] = float(information_ratio)
                
                # Beta calculation (simplified)
                benchmark_returns = data['Close'].pct_change().dropna()
                if len(benchmark_returns) > 1 and len(returns) > 1:
                    # Align returns for correlation calculation
                    aligned_returns = returns.reindex(benchmark_returns.index).dropna()
                    aligned_benchmark = benchmark_returns.reindex(aligned_returns.index).dropna()
                    
                    if len(aligned_returns) > 1 and len(aligned_benchmark) > 1:
                        covariance = np.cov(aligned_returns, aligned_benchmark)[0, 1]
                        benchmark_variance = np.var(aligned_benchmark)
                        beta = covariance / benchmark_variance if benchmark_variance > 0 else 0.0
                        benchmark_metrics['beta'] = float(beta)
                    else:
                        benchmark_metrics['beta'] = 0.0
                else:
                    benchmark_metrics['beta'] = 0.0
            else:
                benchmark_metrics.update({
                    'benchmark_return': 0.0, 'information_ratio': 0.0, 'beta': 0.0
                })
                
        except Exception as e:
            logger.warning(f"Benchmark metrics calculation failed: {str(e)}")
            benchmark_metrics.update({
                'benchmark_return': 0.0, 'information_ratio': 0.0, 'beta': 0.0
            })
        
        return benchmark_metrics


    @staticmethod
    def meets_profitability_criteria(
        metrics: Dict[str, float], 
        criteria: Optional[ProfitabilityCriteria] = None,
        min_return: Optional[float] = None,
        min_sharpe: Optional[float] = None,
        max_drawdown: Optional[float] = None,
        min_trades: Optional[int] = None
    ) -> bool:
        """
        Determine if a trading strategy meets profitability criteria.
        
        This method evaluates strategy performance against configurable criteria
        including return thresholds, risk metrics, and statistical significance.
        
        Args:
            metrics: Dictionary containing strategy performance metrics.
            criteria: ProfitabilityCriteria object with evaluation thresholds.
            min_return: Minimum required total return (overrides criteria).
            min_sharpe: Minimum required Sharpe ratio (overrides criteria).
            max_drawdown: Maximum acceptable drawdown (overrides criteria).
            min_trades: Minimum required trades (overrides criteria).
        
        Returns:
            True if strategy meets all profitability criteria, False otherwise.
        
        Raises:
            DataValidationError: If metrics data is invalid.
        """
        try:
            # Use provided criteria or create default
            if criteria is None:
                criteria = ProfitabilityCriteria()
            
            # Override criteria with individual parameters if provided
            min_return = min_return if min_return is not None else criteria.min_return
            min_sharpe = min_sharpe if min_sharpe is not None else criteria.min_sharpe
            max_drawdown = max_drawdown if max_drawdown is not None else criteria.max_drawdown
            min_trades = min_trades if min_trades is not None else criteria.min_trades
            
            # Validate metrics
            if not isinstance(metrics, dict):
                raise DataValidationError("Metrics must be a dictionary")
            
            # Evaluate profitability criteria
            return_check = metrics.get('total_return', 0) >= min_return
            sharpe_check = metrics.get('sharpe_ratio', 0) >= min_sharpe
            drawdown_check = abs(metrics.get('max_drawdown', 1)) <= max_drawdown
            trades_check = metrics.get('total_trades', 0) >= min_trades
            
            # Additional quality checks
            win_rate_check = metrics.get('win_rate', 0) >= criteria.min_win_rate
            
            is_profitable = all([
                return_check, sharpe_check, drawdown_check, trades_check, win_rate_check
            ])
            
            logger.info(f"Profitability evaluation: Return={return_check}, "
                       f"Sharpe={sharpe_check}, Drawdown={drawdown_check}, "
                       f"Trades={trades_check}, WinRate={win_rate_check}, "
                       f"Overall={'PROFITABLE' if is_profitable else 'NOT PROFITABLE'}")
            
            return is_profitable
            
        except Exception as e:
            logger.error(f"Profitability evaluation failed: {str(e)}")
            raise DataValidationError(f"Failed to evaluate profitability: {str(e)}") from e


    @staticmethod
    def sort_strategies_by_performance(
        strategies_results: List[Dict[str, Any]], 
        ranking_weights: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Rank multiple trading strategies by comprehensive performance scoring.
        
        This method ranks strategies using a weighted scoring system that considers
        multiple performance dimensions including returns, risk-adjusted metrics,
        and trading statistics.
        
        Args:
            strategies_results: List of strategy backtest results dictionaries.
            ranking_weights: Optional custom weights for ranking criteria.
        
        Returns:
            List of strategy results sorted by performance score (best first).
        
        Raises:
            StrategyComparisonError: If strategy comparison fails.
            DataValidationError: If input data is invalid.
        """
        try:
            logger.info(f"Ranking {len(strategies_results)} strategies")
            
            if not strategies_results:
                return []
            
            # Validate input data
            for i, result in enumerate(strategies_results):
                if not isinstance(result, dict) or 'metrics' not in result:
                    raise DataValidationError(f"Invalid strategy result at index {i}")
            
            # Default ranking weights
            default_weights = {
                'total_return': 0.3,
                'sharpe_ratio': 0.25,
                'max_drawdown': 0.2,
                'win_rate': 0.15,
                'profit_factor': 0.1
            }
            
            weights = ranking_weights if ranking_weights is not None else default_weights
            
            # Calculate composite scores
            scored_strategies = []
            for result in strategies_results:
                score = PerformanceAnalyzer._calculate_strategy_score(result['metrics'], weights)
                result_copy = result.copy()
                result_copy['ranking_score'] = score
                scored_strategies.append(result_copy)
            
            # Sort by score (descending)
            ranked_strategies = sorted(scored_strategies, key=lambda x: x['ranking_score'], reverse=True)
            
            # Add ranking positions
            for i, strategy in enumerate(ranked_strategies):
                strategy['rank'] = i + 1
            
            logger.info(f"Strategies ranked successfully. "
                       f"Best score: {ranked_strategies[0]['ranking_score']:.3f}")
            
            return ranked_strategies
            
        except Exception as e:
            logger.error(f"Strategy ranking failed: {str(e)}")
            raise StrategyComparisonError(f"Failed to rank strategies: {str(e)}") from e


    @staticmethod
    def _calculate_strategy_score(metrics: Dict[str, float], weights: Dict[str, float]) -> float:
        """
        Calculate composite performance score for strategy ranking.
        
        Args:
            metrics: Strategy performance metrics.
            weights: Weights for different metrics.
        
        Returns:
            Composite performance score.
        """
        score = 0.0
        
        try:
            # Normalize and weight each metric
            score += metrics.get('total_return', 0) * weights.get('total_return', 0)
            score += metrics.get('sharpe_ratio', 0) * weights.get('sharpe_ratio', 0)
            score += (1 - abs(metrics.get('max_drawdown', 1))) * weights.get('max_drawdown', 0)
            score += metrics.get('win_rate', 0) * weights.get('win_rate', 0)
            score += min(metrics.get('profit_factor', 0), 5) / 5 * weights.get('profit_factor', 0)
            
            # Additional quality adjustments
            if metrics.get('total_trades', 0) < 5:
                score *= 0.5  # Penalize strategies with too few trades
            
            if metrics.get('volatility', 0) > 1.0:  # Very high volatility
                score *= 0.8  # Penalize high volatility strategies
            
        except Exception as e:
            logger.warning(f"Score calculation failed for metrics: {str(e)}")
            score = 0.0
        
        return max(score, 0.0)  # Ensure non-negative score


    @staticmethod
    def create_detailed_analysis_report(
        results: Dict[str, Any], 
        include_advanced: bool = True,
        include_trades: bool = True
    ) -> str:
        """
        Generate a comprehensive textual performance report for a trading strategy.
        
        This method creates a detailed, formatted report including strategy details,
        financial performance, risk metrics, trading statistics, and evaluation.
        
        Args:
            results: Complete backtest results dictionary.
            include_advanced: Whether to include advanced metrics in the report.
            include_trades: Whether to include detailed trade statistics.
        
        Returns:
            Formatted string containing the comprehensive performance report.
        
        Raises:
            ReportGenerationError: If report generation fails.
            DataValidationError: If input data is invalid.
        """
        try:
            logger.info("Generating performance report")
            
            # Validate input data
            PerformanceAnalyzer._validate_results_data(results)
            
            strategy = results['strategy']
            metrics = results['metrics']
            period = results['backtest_period']
            symbol = results.get('symbol', 'UNKNOWN')
            
            # Calculate advanced metrics if requested
            if include_advanced:
                try:
                    metrics = PerformanceAnalyzer.compute_extended_performance_stats(results)
                except Exception as e:
                    logger.warning(f"Advanced metrics calculation failed in report: {str(e)}")
            
            # Build report sections
            report_sections = []
            
            # Header section
            report_sections.append(PerformanceAnalyzer._generate_header_section(
                strategy, symbol, period
            ))
            
            # Financial results section
            report_sections.append(PerformanceAnalyzer._generate_financial_section(
                metrics, results.get('parameters', {})
            ))
            
            # Risk metrics section
            report_sections.append(PerformanceAnalyzer._generate_risk_section(metrics))
            
            # Trading statistics section
            if include_trades:
                report_sections.append(PerformanceAnalyzer._generate_trading_section(metrics))
            
            # Advanced metrics section
            if include_advanced:
                report_sections.append(PerformanceAnalyzer._generate_advanced_section(metrics))
            
            # Strategy parameters section
            report_sections.append(PerformanceAnalyzer._generate_parameters_section(strategy))
            
            # Evaluation section
            report_sections.append(PerformanceAnalyzer._generate_evaluation_section(metrics))
            
            # Combine all sections
            full_report = '\n'.join(report_sections)
            
            logger.info("Performance report generated successfully")
            return full_report
            
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            raise ReportGenerationError(f"Failed to generate performance report: {str(e)}") from e


    @staticmethod
    def _generate_header_section(strategy: Dict[str, Any], symbol: str, period: Dict[str, Any]) -> str:
        """Generate report header section."""
        return f"""
=== COMPREHENSIVE PERFORMANCE REPORT ===

Strategy: {strategy.get('name', 'Unknown Strategy')}
Asset: {symbol}
Description: {strategy.get('description', 'No description available')}
Period: {period['start']} to {period['end']} ({period['duration_days']} days)
Total Periods: {period.get('total_periods', 'N/A')}
"""


    @staticmethod
    def _generate_financial_section(metrics: Dict[str, float], parameters: Dict[str, Any]) -> str:
        """Generate financial results section."""
        initial_cash = parameters.get('initial_cash', 10000)
        return f"""
--- FINANCIAL PERFORMANCE ---
Initial Capital: ${initial_cash:,.2f}
Final Value: ${metrics.get('final_value', initial_cash):,.2f}
Total Return: {metrics.get('total_return', 0):.2%}
Alpha vs Buy & Hold: {metrics.get('alpha', 0):.2%}
Benchmark Return: {metrics.get('benchmark_return', 0):.2%}
"""


    @staticmethod
    def _generate_risk_section(metrics: Dict[str, float]) -> str:
        """Generate risk metrics section."""
        return f"""
--- RISK ANALYSIS ---
Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}
Sortino Ratio: {metrics.get('sortino_ratio', 0):.2f}
Calmar Ratio: {metrics.get('calmar_ratio', 0):.2f}
Maximum Drawdown: {metrics.get('max_drawdown', 0):.2%}
Volatility (Annualized): {metrics.get('volatility', 0):.2%}
Value at Risk (95%): {metrics.get('var_95', 0):.2%}
"""


    @staticmethod
    def _generate_trading_section(metrics: Dict[str, float]) -> str:
        """Generate trading statistics section."""
        return f"""
--- TRADING STATISTICS ---
Total Trades: {metrics.get('total_trades', 0)}
Win Rate: {metrics.get('win_rate', 0):.2%}
Average Trade Duration: {metrics.get('avg_trade_duration', 0):.1f} days
Profit Factor: {metrics.get('profit_factor', 0):.2f}
Average Win: ${metrics.get('avg_win', 0):.2f}
Average Loss: ${metrics.get('avg_loss', 0):.2f}
Win/Loss Ratio: {metrics.get('win_loss_ratio', 0):.2f}
Largest Win: ${metrics.get('largest_win', 0):.2f}
Largest Loss: ${metrics.get('largest_loss', 0):.2f}
"""


    @staticmethod
    def _generate_advanced_section(metrics: Dict[str, float]) -> str:
        """Generate advanced metrics section."""
        return f"""
--- ADVANCED METRICS ---
Information Ratio: {metrics.get('information_ratio', 0):.2f}
Beta: {metrics.get('beta', 0):.2f}
Skewness: {metrics.get('skewness', 0):.2f}
Kurtosis: {metrics.get('kurtosis', 0):.2f}
Recovery Factor: {metrics.get('recovery_factor', 0):.2f}
Market Exposure: {metrics.get('market_exposure', 0):.2%}
Max Drawdown Duration: {metrics.get('max_drawdown_duration', 0):.0f} days
"""


    @staticmethod
    def _generate_parameters_section(strategy: Dict[str, Any]) -> str:
        """Generate strategy parameters section."""
        parameters_text = "--- STRATEGY PARAMETERS ---\n"
        
        strategy_parameters = strategy.get('parameters', {})
        if strategy_parameters:
            for key, value in strategy_parameters.items():
                parameters_text += f"{key}: {value}\n"
        else:
            parameters_text += "No parameters configured\n"
        
        return parameters_text


    @staticmethod
    def _generate_evaluation_section(metrics: Dict[str, float]) -> str:
        """Generate evaluation section."""
        is_profitable = PerformanceAnalyzer.meets_profitability_criteria(metrics)
        
        evaluation_text = "--- STRATEGY EVALUATION ---\n"
        evaluation_text += f"Profitable Strategy: {'✅ YES' if is_profitable else '❌ NO'}\n"
        
        # Additional evaluation criteria
        if metrics.get('total_return', 0) > 0.2:
            evaluation_text += "Return Rating: ⭐⭐⭐ Excellent\n"
        elif metrics.get('total_return', 0) > 0.1:
            evaluation_text += "Return Rating: ⭐⭐ Good\n"
        elif metrics.get('total_return', 0) > 0:
            evaluation_text += "Return Rating: ⭐ Fair\n"
        else:
            evaluation_text += "Return Rating: ❌ Poor\n"
        
        if metrics.get('sharpe_ratio', 0) > 2.0:
            evaluation_text += "Risk-Adjusted Rating: ⭐⭐⭐ Excellent\n"
        elif metrics.get('sharpe_ratio', 0) > 1.0:
            evaluation_text += "Risk-Adjusted Rating: ⭐⭐ Good\n"
        elif metrics.get('sharpe_ratio', 0) > 0:
            evaluation_text += "Risk-Adjusted Rating: ⭐ Fair\n"
        else:
            evaluation_text += "Risk-Adjusted Rating: ❌ Poor\n"
        
        return evaluation_text


    @staticmethod
    def compare_strategies_detailed(
        strategy_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Perform detailed comparison analysis between multiple strategies.
        
        Args:
            strategy_results: List of strategy backtest results.
        
        Returns:
            Dictionary containing detailed comparison analysis.
        
        Raises:
            StrategyComparisonError: If comparison fails.
        """
        try:
            if len(strategy_results) < 2:
                raise StrategyComparisonError("At least 2 strategies required for comparison")
            
            # Rank strategies
            ranked_strategies = PerformanceAnalyzer.sort_strategies_by_performance(strategy_results)
            
            # Calculate comparison metrics
            comparison_data = {
                'total_strategies': len(strategy_results),
                'profitable_strategies': sum(
                    1 for result in strategy_results 
                    if PerformanceAnalyzer.meets_profitability_criteria(result['metrics'])
                ),
                'best_strategy': ranked_strategies[0],
                'worst_strategy': ranked_strategies[-1],
                'average_return': np.mean([r['metrics'].get('total_return', 0) for r in strategy_results]),
                'average_sharpe': np.mean([r['metrics'].get('sharpe_ratio', 0) for r in strategy_results]),
                'ranking': ranked_strategies
            }
            
            return comparison_data
            
        except Exception as e:
            raise StrategyComparisonError(f"Strategy comparison failed: {str(e)}") from e


    @staticmethod
    def calculate_portfolio_correlation(
        results1: Dict[str, Any], 
        results2: Dict[str, Any]
    ) -> float:
        """
        Calculate correlation between two strategy portfolios.
        
        Args:
            results1: First strategy results.
            results2: Second strategy results.
        
        Returns:
            Correlation coefficient between portfolio returns.
        
        Raises:
            MetricsCalculationError: If correlation calculation fails.
        """
        try:
            returns1 = results1['portfolio'].returns()
            returns2 = results2['portfolio'].returns()
            
            # Align returns by index
            aligned_returns = pd.concat([returns1, returns2], axis=1).dropna()
            
            if len(aligned_returns) < 2:
                return 0.0
            
            correlation = aligned_returns.iloc[:, 0].corr(aligned_returns.iloc[:, 1])
            return float(correlation) if not pd.isna(correlation) else 0.0
            
        except Exception as e:
            raise MetricsCalculationError(f"Correlation calculation failed: {str(e)}") from e


    @staticmethod
    def generate_comparison_report(
        strategy_results: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a comprehensive comparison report for multiple strategies.
        
        Args:
            strategy_results: List of strategy backtest results.
        
        Returns:
            Formatted comparison report string.
        
        Raises:
            ReportGenerationError: If report generation fails.
        """
        try:
            comparison_data = PerformanceAnalyzer.compare_strategies_detailed(strategy_results)
            
            report = f"""
=== STRATEGY COMPARISON REPORT ===

Total Strategies Analyzed: {comparison_data['total_strategies']}
Profitable Strategies: {comparison_data['profitable_strategies']}
Success Rate: {comparison_data['profitable_strategies'] / comparison_data['total_strategies']:.1%}

Average Performance:
- Return: {comparison_data['average_return']:.2%}
- Sharpe Ratio: {comparison_data['average_sharpe']:.2f}

--- TOP PERFORMING STRATEGY ---
Strategy: {comparison_data['best_strategy']['strategy']['name']}
Return: {comparison_data['best_strategy']['metrics']['total_return']:.2%}
Sharpe: {comparison_data['best_strategy']['metrics']['sharpe_ratio']:.2f}
Score: {comparison_data['best_strategy']['ranking_score']:.3f}

--- STRATEGY RANKINGS ---
"""
            
            for i, strategy in enumerate(comparison_data['ranking'][:5], 1):
                report += f"{i}. {strategy['strategy']['name']}: "
                report += f"Return={strategy['metrics']['total_return']:.2%}, "
                report += f"Sharpe={strategy['metrics']['sharpe_ratio']:.2f}, "
                report += f"Score={strategy['ranking_score']:.3f}\n"
            
            return report
            
        except Exception as e:
            raise ReportGenerationError(f"Comparison report generation failed: {str(e)}") from e


    @staticmethod
    def export_metrics_to_dict(
        results: Dict[str, Any],
        include_advanced: bool = True
    ) -> Dict[str, Any]:
        """
        Export comprehensive metrics to a structured dictionary format.
        
        Args:
            results: Backtest results dictionary.
            include_advanced: Whether to include advanced metrics.
        
        Returns:
            Structured dictionary with all metrics organized by category.
        
        Raises:
            DataValidationError: If results data is invalid.
        """
        try:
            PerformanceAnalyzer._validate_results_data(results)
            
            # Get metrics (with advanced if requested)
            if include_advanced:
                metrics = PerformanceAnalyzer.compute_extended_performance_stats(results)
            else:
                metrics = results['metrics']
            
            # Organize metrics by category
            organized_metrics = {
                'basic_performance': {
                    'total_return': metrics.get('total_return', 0.0),
                    'final_value': metrics.get('final_value', 0.0),
                    'alpha': metrics.get('alpha', 0.0),
                    'benchmark_return': metrics.get('benchmark_return', 0.0)
                },
                'risk_metrics': {
                    'sharpe_ratio': metrics.get('sharpe_ratio', 0.0),
                    'sortino_ratio': metrics.get('sortino_ratio', 0.0),
                    'calmar_ratio': metrics.get('calmar_ratio', 0.0),
                    'max_drawdown': metrics.get('max_drawdown', 0.0),
                    'volatility': metrics.get('volatility', 0.0),
                    'var_95': metrics.get('var_95', 0.0),
                    'skewness': metrics.get('skewness', 0.0),
                    'kurtosis': metrics.get('kurtosis', 0.0)
                },
                'trading_stats': {
                    'total_trades': metrics.get('total_trades', 0),
                    'win_rate': metrics.get('win_rate', 0.0),
                    'profit_factor': metrics.get('profit_factor', 0.0),
                    'avg_trade_duration': metrics.get('avg_trade_duration', 0.0),
                    'avg_win': metrics.get('avg_win', 0.0),
                    'avg_loss': metrics.get('avg_loss', 0.0),
                    'win_loss_ratio': metrics.get('win_loss_ratio', 0.0)
                },
                'portfolio_metrics': {
                    'market_exposure': metrics.get('market_exposure', 0.0),
                    'recovery_factor': metrics.get('recovery_factor', 0.0),
                    'max_drawdown_duration': metrics.get('max_drawdown_duration', 0.0)
                },
                'benchmark_comparison': {
                    'information_ratio': metrics.get('information_ratio', 0.0),
                    'beta': metrics.get('beta', 0.0)
                },
                'metadata': {
                    'strategy_name': results['strategy'].get('name', 'Unknown'),
                    'symbol': results.get('symbol', 'Unknown'),
                    'period_start': results['backtest_period']['start'],
                    'period_end': results['backtest_period']['end'],
                    'duration_days': results['backtest_period']['duration_days'],
                    'is_profitable': PerformanceAnalyzer.meets_profitability_criteria(metrics)
                }
            }
            
            return organized_metrics
            
        except Exception as e:
            raise DataValidationError(f"Failed to export metrics: {str(e)}") from e