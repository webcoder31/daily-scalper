"""
Class for calculating and analyzing performance metrics.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np
from datetime import datetime


class PerformanceMetrics:
    """
    Class for analyzing and comparing strategy performances.
    """
    
    @staticmethod
    def calculate_advanced_metrics(results: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculates advanced metrics from backtest results.
        
        Args:
            results: Backtest results
            
        Returns:
            Dictionary of advanced metrics
        """
        portfolio = results['portfolio']
        metrics = results['metrics'].copy()
        
        try:
            # Additional calculations
            returns = portfolio.returns()
            
            # Annualized volatility
            volatility = returns.std() * np.sqrt(252)
            
            # Calmar ratio (annualized return / max drawdown)
            calmar_ratio = (metrics['total_return'] * 252 / len(returns)) / abs(metrics['max_drawdown']) if metrics['max_drawdown'] != 0 else 0
            
            # Sortino ratio
            downside_returns = returns[returns < 0]
            downside_deviation = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
            sortino_ratio = (metrics['total_return'] * 252 / len(returns)) / downside_deviation if downside_deviation != 0 else 0
            
            # VaR (Value at Risk) at 95%
            var_95 = np.percentile(returns, 5) if len(returns) > 0 else 0
            
            metrics.update({
                'volatility': float(volatility) if not pd.isna(volatility) else 0.0,
                'calmar_ratio': float(calmar_ratio) if not pd.isna(calmar_ratio) else 0.0,
                'sortino_ratio': float(sortino_ratio) if not pd.isna(sortino_ratio) else 0.0,
                'var_95': float(var_95) if not pd.isna(var_95) else 0.0,
            })
            
        except Exception as e:
            print(f"Error while calculating advanced metrics: {e}")
        
        return metrics
    
    @staticmethod
    def is_strategy_profitable(
            metrics: Dict[str, float], 
            min_return: float = 0.1,
            min_sharpe: float = 1.0,
            max_drawdown: float = 0.2
        ) -> bool:
        """
        Determines if a strategy is considered profitable.
        
        Args:
            metrics: Performance metrics
            min_return: Minimum required return
            min_sharpe: Minimum Sharpe ratio
            max_drawdown: Maximum acceptable drawdown
            
        Returns:
            True if the strategy is profitable, False otherwise
        """
        return (
            metrics.get('total_return', 0) >= min_return and
            metrics.get('sharpe_ratio', 0) >= min_sharpe and
            abs(metrics.get('max_drawdown', 1)) <= max_drawdown and
            metrics.get('total_trades', 0) >= 5  # Minimum trades for reliability
        )
    
    @staticmethod
    def rank_strategies(strategies_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ranks strategies by performance.
        
        Args:
            strategies_results: List of strategy results
            
        Returns:
            List sorted by performance (best first)
        """
        def calculate_score(metrics: Dict[str, float]) -> float:
            """Calculates a composite score for ranking."""
            return (
                metrics.get('total_return', 0) * 0.3 +
                metrics.get('sharpe_ratio', 0) * 0.3 +
                (1 - abs(metrics.get('max_drawdown', 1))) * 0.2 +
                metrics.get('win_rate', 0) * 0.2
            )
        
        # Add score to each strategy
        for result in strategies_results:
            result['score'] = calculate_score(result['metrics'])
        
        # Sort by descending score
        return sorted(strategies_results, key=lambda x: x['score'], reverse=True)
    
    @staticmethod
    def generate_performance_report(results: Dict[str, Any]) -> str:
        """
        Generates a textual performance report.
        
        Args:
            results: Backtest results
            
        Returns:
            Formatted text report
        """
        strategy = results['strategy']
        metrics = results['metrics']
        period = results['backtest_period']
        
        report = f"""
=== PERFORMANCE REPORT ===

Strategy: {strategy['name']}
Crypto Pair: results['symbol']
Description: {strategy['description']}
Period: {period['start']} to {period['end']} ({period['duration_days']} days)

--- FINANCIAL RESULTS ---
Initial capital: ${results['parameters']['initial_cash']:,.2f}
Final value: ${metrics['final_value']:,.2f}
Total return: {metrics['total_return']:.2%}
Alpha vs Buy & Hold: {metrics['alpha']:.2%}

--- RISK METRICS ---
Sharpe ratio: {metrics['sharpe_ratio']:.2f}
Maximum drawdown: {metrics['max_drawdown']:.2%}
Volatility: {metrics.get('volatility', 0):.2%}

--- TRADING STATISTICS ---
Total number of trades: {metrics['total_trades']}
Win rate: {metrics['win_rate']:.2%}
Average trade duration: {metrics['avg_trade_duration']:.1f} days
Profit factor: {metrics['profit_factor']:.2f}

--- PARAMETERS ---
"""
        
        for key, value in strategy['parameters'].items():
            report += f"{key}: {value}\n"
        
        # Performance evaluation
        is_profitable = PerformanceMetrics.is_strategy_profitable(metrics)
        report += f"\n--- EVALUATION ---\n"
        report += f"Profitable strategy: {'✅ YES' if is_profitable else '❌ NO'}\n"
        
        return report