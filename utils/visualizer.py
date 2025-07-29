"""
Module for visualizing backtest results.
"""

from typing import Dict, Any, Optional
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px


class Visualizer:
    """
    Class for creating interactive visualizations of backtest results.
    """
    
    @staticmethod
    def plot_backtest_results(
            results: Dict[str, Any], 
            show_signals: bool = True,
            show_indicators: bool = True,
        ) -> go.Figure:
        """
        Creates an interactive chart of backtest results.
        
        Args:
            results: Backtest results
            show_signals: Show buy/sell signals
            show_indicators: Show technical indicators
            save_path: Path to save the chart (optional)
            
        Returns:
            Plotly figure
        """
        data = results['data']
        portfolio = results['portfolio']
        buy_signals = results['buy_signals']
        sell_signals = results['sell_signals']
        strategy = results['strategy']
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('Price and Signals', 'Portfolio Value', 'Volume'),
            row_heights=[0.5, 0.3, 0.2]
        )
        
        # 1. Price chart with candlestick
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='Price',
                increasing_line_color='#2ca02c',  # Green
                decreasing_line_color='#d62728'   # Red
            ),
            row=1, col=1
        )
        
        # Technical indicators (if available)
        if show_indicators and hasattr(results.get('strategy_instance'), 'get_indicators'):
            try:
                indicators = results['strategy_instance'].get_indicators()
                for name, indicator in indicators.items():
                    fig.add_trace(
                        go.Scatter(
                            x=data.index,
                            y=indicator,
                            name=name.upper(),
                            line=dict(width=2)
                        ),
                        row=1, col=1
                    )
            except:
                pass
        
        # Buy and sell signals
        if show_signals:
            
            # Buy signals
            buy_points = data[buy_signals]
            if not buy_points.empty:
                fig.add_trace(
                    go.Scatter(
                        x=buy_points.index,
                        y=buy_points['Close'],
                        mode='markers',
                        marker=dict(
                            symbol='triangle-up',
                            size=12,
                            color='#2ca02c',  # Green
                            line=dict(color='#1f5f1f', width=2)  # Dark green
                        ),
                        name='Buy',
                        hovertemplate='Buy: %{y:.2f}<br>Date: %{x}<extra></extra>'
                    ),
                    row=1, col=1
                )
            
            # Sell signals
            sell_points = data[sell_signals]
            if not sell_points.empty:
                fig.add_trace(
                    go.Scatter(
                        x=sell_points.index,
                        y=sell_points['Close'],
                        mode='markers',
                        marker=dict(
                            symbol='triangle-down',
                            size=12,
                            color='#d62728',  # Red
                            line=dict(color='#8b1a1a', width=2)  # Dark red
                        ),
                        name='Sell',
                        hovertemplate='Sell: %{y:.2f}<br>Date: %{x}<extra></extra>'
                    ),
                    row=1, col=1
                )
        
        # 2. Portfolio value
        portfolio_value = portfolio.value()
        fig.add_trace(
            go.Scatter(
                x=portfolio_value.index,
                y=portfolio_value.values,
                name='Portfolio Value',
                line=dict(color='#1f77b4', width=2),  # Blue
                hovertemplate='Value: $%{y:,.2f}<br>Date: %{x}<extra></extra>'
            ),
            row=2, col=1
        )
        
        # Reference line (initial capital)
        fig.add_hline(
            y=results['parameters']['initial_cash'],
            line_dash="dash",
            line_color="#7f7f7f",  # Gray
            annotation_text="Initial capital",
            row=2, col=1
        )
        
        # 3. Volume
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['Volume'],
                name='Volume',
                marker_color='#aec7e8',  # Light blue
                opacity=0.7
            ),
            row=3, col=1
        )
        
        # Formatting
        fig.update_layout(
            title=f"Backtest: {strategy['name']} - Return: {results['metrics']['total_return']:.2%}",
            # xaxis_title="Date",
            height=800,
            showlegend=True,
            hovermode='x unified'
        )
        
        # Y axes
        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        fig.update_yaxes(title_text="Value ($)", row=2, col=1)
        fig.update_yaxes(title_text="Volume", row=3, col=1)
        
        # Remove range selector for candlestick
        fig.update_layout(xaxis_rangeslider_visible=False)
        
        return fig
    
    @staticmethod
    def plot_performance_metrics(results: Dict[str, Any]) -> go.Figure:
        """
        Creates a chart of performance metrics.
        
        Args:
            results: Backtest results
            
        Returns:
            Plotly figure with metrics
        """
        metrics = results['metrics']
        
        # Prepare data for radar chart
        categories = [
            'Total Return',
            'Sharpe Ratio',
            'Win Rate',
            'Profit Factor',
            'Alpha vs B&H'
        ]
        
        values = [
            min(metrics['total_return'] * 100, 100),  # Normalization
            min(metrics['sharpe_ratio'] * 20, 100),   # Normalization
            metrics['win_rate'] * 100,
            min(metrics['profit_factor'] * 20, 100),  # Normalization
            min((metrics['alpha'] + 0.5) * 100, 100) # Normalization
        ]
        
        # Radar chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Performance',
            line_color='#1f77b4'  # Blue
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=False,
            title="Performance Metrics (Normalized)"
        )
        
        return fig
    
    @staticmethod
    def plot_drawdown(results: Dict[str, Any]) -> go.Figure:
        """
        Creates a drawdown chart.
        
        Args:
            results: Backtest results
            
        Returns:
            Plotly figure of drawdown
        """
        portfolio = results['portfolio']
        
        try:
            drawdown = portfolio.drawdown()
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=drawdown.index,
                y=drawdown.values * 100,  # Convert to percentage
                fill='tonexty',
                fillcolor='rgba(214, 39, 40, 0.3)',  # Light red
                line_color='#d62728',  # Red
                name='Drawdown',
                hovertemplate='Drawdown: %{y:.2f}%<br>Date: %{x}<extra></extra>'
            ))
            
            fig.update_layout(
                title="Drawdown Evolution",
                xaxis_title="Date",
                yaxis_title="Drawdown (%)",
                hovermode='x'
            )
            
            # Reference line at 0
            fig.add_hline(y=0, line_dash="dash", line_color="#7f7f7f")  # Gray
            
            return fig
            
        except Exception as e:
            print(f"Error creating drawdown chart: {e}")
            return go.Figure().add_annotation(text="Error: unable to calculate drawdown")
    
    @staticmethod
    def show_all_plots(results: Dict[str, Any]) -> None:
        """
        Displays all performance charts.
        
        Args:
            results: Backtest results
        """
        # Main chart
        main_fig = Visualizer.plot_backtest_results(results)
        main_fig.show()
        
        # Performance metrics
        metrics_fig = Visualizer.plot_performance_metrics(results)
        metrics_fig.show()
        
        # Drawdown
        drawdown_fig = Visualizer.plot_drawdown(results)
        drawdown_fig.show()