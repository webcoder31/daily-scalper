"""
Charting module for cryptocurrency trading strategy backtests.

This module provides comprehensive charting capabilities for backtest results
using Plotly. It includes interactive charts for price data, portfolio performance,
technical indicators, and performance metrics with robust error handling and
customization options.

Classes:
    ChartBuilder: Main class for creating interactive charts.
    ChartError: Custom exception for chart errors
    ChartConfigurationError: Custom exception for chart configuration errors
    ChartDataError: Custom exception for chart data errors

Example:
    >>> from charting.chart_builder import ChartBuilder
    >>> chart_builder = ChartBuilder()
    >>> chart = chart_builder.create_backtest_charts(backtest_results)
    >>> chart.show()
"""

from typing import Dict, Any, Optional, List
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px # Not used for now, but can be useful for future enhancements 
import numpy as np

# Configure logging - use absolute import to avoid local logging module conflict
from logger.logging_manager import get_logger
logger = get_logger(__name__)


class ChartError(Exception):
    """Exception raised when chart operations fail."""
    

    def __init__(self, message: str, chart_type: Optional[str] = None, cause: Optional[Exception] = None) -> None:
        """
        Initialize ChartError.
        
        Args:
            message: Error message describing the issue.
            chart_type: The type of chart that caused the error (optional).
            cause: The underlying exception that caused this error (optional).
        """
        self.chart_type = chart_type
        self.cause = cause
        super().__init__(message)


class ChartConfigurationError(Exception):
    """Exception raised when chart configuration is invalid."""
    

    def __init__(self, message: str, config_key: Optional[str] = None, cause: Optional[Exception] = None) -> None:
        """
        Initialize ChartConfigurationError.
        
        Args:
            message: Error message describing the configuration issue.
            config_key: The configuration key that caused the error (optional).
            cause: The underlying exception that caused this error (optional).
        """
        self.config_key = config_key
        self.cause = cause
        super().__init__(message)


class ChartDataError(Exception):
    """Exception raised when data preparation for chart creation fails."""
    

    def __init__(self, message: str, data_type: Optional[str] = None, cause: Optional[Exception] = None) -> None:
        """
        Initialize ChartDataError.
        
        Args:
            message: Error message describing the data issue.
            data_type: The type of data that caused the error (optional).
            cause: The underlying exception that caused this error (optional).
        """
        self.data_type = data_type
        self.cause = cause
        super().__init__(message)


class ChartBuilder:
    """
    Class for creating interactive charts of cryptocurrency trading backtest results.
    
    This class provides comprehensive charting capabilities including candlestick charts,
    portfolio performance tracking, technical indicators, performance metrics, and drawdown
    analysis. All charts are interactive and built using Plotly with professional styling
    and robust error handling.
    
    Attributes:
        DEFAULT_COLORS: Default color scheme for charts.
        CHART_HEIGHT: Default height for charts.
        SUBPLOT_SPACING: Default spacing between subplots.
        
    Example:
        >>> chart_builder = ChartBuilder()
        >>> main_chart = chart_builder.create_backtest_charts(results)
        >>> metrics_chart = chart_builder.create_performance_metrics_chart(results)
        >>> drawdown_chart = chart_builder.create_drawdown_chart(results)
    """
    
    # Default color scheme for consistent chart styling
    DEFAULT_COLORS: Dict[str, str] = {
        'bullish': '#2ca02c',      # Green for bullish/positive
        'bearish': '#d62728',      # Red for bearish/negative
        'primary': '#1f77b4',      # Blue for primary elements
        'secondary': '#ff7f0e',    # Orange for secondary elements
        'neutral': '#7f7f7f',      # Gray for neutral elements
        'background': '#ffffff',   # White background
        'grid': '#e0e0e0',        # Light gray for grid lines
        'volume': '#aec7e8',      # Light blue for volume
        'highlight': '#ff1493'     # Pink for highlights
    }
    
    # Chart configuration constants
    CHART_HEIGHT: int = 800
    SUBPLOT_SPACING: float = 0.05
    CANDLESTICK_OPACITY: float = 0.8
    SIGNAL_MARKER_SIZE: int = 12
    LINE_WIDTH: int = 2
    

    @staticmethod
    def create_backtest_charts(
        results: Dict[str, Any],
        show_signals: bool = True,
        show_indicators: bool = True
    ) -> go.Figure:
        """
        Create an interactive chart of backtest results.
        
        Args:
            results: Dictionary containing backtest results.
            show_signals: Whether to show buy/sell signals.
            show_indicators: Whether to show technical indicators.
            
        Returns:
            Interactive Plotly figure.
            
        Raises:
            ChartError: If chart creation fails.
            ChartDataError: If required data is missing.
        """
        try:
            # Validate required data
            required_fields = ['data', 'portfolio', 'buy_signals', 'sell_signals', 'strategy']
            missing_fields = [field for field in required_fields if field not in results]
            
            if missing_fields:
                raise ChartDataError(
                    f"Missing required fields: {missing_fields}",
                    data_type="backtest_results"
                )
            
            data = results['data']
            portfolio = results['portfolio']
            buy_signals = results['buy_signals']
            sell_signals = results['sell_signals']
            strategy = results['strategy']
            
            # Validate data types
            if not isinstance(data, pd.DataFrame) or data.empty:
                raise ChartDataError(
                    "Data must be a non-empty pandas DataFrame",
                    data_type="price_data"
                )
            
            # Create subplots
            chart = make_subplots(
                rows=3, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                subplot_titles=('Price and Signals', 'Portfolio Value', 'Volume'),
                row_heights=[0.5, 0.3, 0.2]
            )
            
            # Add candlestick chart
            chart.add_trace(
                go.Candlestick(
                    x=data.index,
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    name='Price',
                    increasing_line_color='#2ca02c',
                    decreasing_line_color='#d62728'
                ),
                row=1, col=1
            )
            
            # Add technical indicators if available and requested
            if show_indicators and hasattr(results.get('strategy_instance'), 'get_indicators'):
                try:
                    indicators = results['strategy_instance'].get_indicators()
                    for name, indicator in indicators.items():
                        if isinstance(indicator, (pd.Series, np.ndarray)) and len(indicator) == len(data):
                            chart.add_trace(
                                go.Scatter(
                                    x=data.index,
                                    y=indicator,
                                    name=name.upper(),
                                    line=dict(width=2)
                                ),
                                row=1, col=1
                            )
                except Exception as e:
                    logger.warning(f"Failed to add indicators: {e}")
            
            # Add buy and sell signals if requested
            if show_signals:
                # Buy signals
                if isinstance(buy_signals, pd.Series) and buy_signals.any():
                    buy_points = data[buy_signals]
                    if not buy_points.empty:
                        chart.add_trace(
                            go.Scatter(
                                x=buy_points.index,
                                y=buy_points['Close'],
                                mode='markers',
                                marker=dict(
                                    symbol='triangle-up',
                                    size=12,
                                    color='#2ca02c',
                                    line=dict(color='#1f5f1f', width=2)
                                ),
                                name='Buy',
                                hovertemplate='Buy: %{y:.2f}<br>Date: %{x}<extra></extra>'
                            ),
                            row=1, col=1
                        )
                
                # Sell signals
                if isinstance(sell_signals, pd.Series) and sell_signals.any():
                    sell_points = data[sell_signals]
                    if not sell_points.empty:
                        chart.add_trace(
                            go.Scatter(
                                x=sell_points.index,
                                y=sell_points['Close'],
                                mode='markers',
                                marker=dict(
                                    symbol='triangle-down',
                                    size=12,
                                    color='#d62728',
                                    line=dict(color='#8b1a1a', width=2)
                                ),
                                name='Sell',
                                hovertemplate='Sell: %{y:.2f}<br>Date: %{x}<extra></extra>'
                            ),
                            row=1, col=1
                        )
            
            # Add portfolio value
            try:
                portfolio_value = portfolio.value()
                chart.add_trace(
                    go.Scatter(
                        x=portfolio_value.index,
                        y=portfolio_value.values,
                        name='Portfolio Value',
                        line=dict(color='#1f77b4', width=2),
                        hovertemplate='Value: $%{y:,.2f}<br>Date: %{x}<extra></extra>'
                    ),
                    row=2, col=1
                )
                
                # Add initial capital reference line
                initial_cash = results.get('parameters', {}).get('initial_cash', 10000)
                chart.add_hline(
                    y=initial_cash,
                    line_dash="dash",
                    line_color="#7f7f7f",
                    annotation_text="Initial Capital",
                    row=2, col=1
                )
            except Exception as e:
                logger.error(f"Failed to add portfolio chart: {e}")
                raise ChartError(
                    f"Failed to create portfolio chart: {str(e)}",
                    chart_type="portfolio",
                    cause=e
                ) from e
            
            # Add volume chart
            if 'Volume' in data.columns:
                chart.add_trace(
                    go.Bar(
                        x=data.index,
                        y=data['Volume'],
                        name='Volume',
                        marker_color='#aec7e8',
                        opacity=0.7
                    ),
                    row=3, col=1
                )
            
            # Configure layout
            total_return = results.get('metrics', {}).get('total_return', 0)
            strategy_name = strategy.get('name', 'Unknown Strategy')
            
            chart.update_layout(
                title=f"Backtest: {strategy_name} - Return: {total_return:.2%}",
                height=800,
                showlegend=True,
                hovermode='x unified',
                template='plotly_white'
            )
            
            # Update axes
            chart.update_yaxes(title_text="Price ($)", row=1, col=1)
            chart.update_yaxes(title_text="Value ($)", row=2, col=1)
            chart.update_yaxes(title_text="Volume", row=3, col=1)
            
            # Remove range selector for candlestick
            chart.update_layout(xaxis_rangeslider_visible=False)
            
            logger.info(f"Backtest chart created successfully for {strategy_name}")
            return chart
            
        except (ChartError, ChartDataError):
            raise
        except Exception as e:
            raise ChartError(
                f"Unexpected error creating backtest chart: {str(e)}",
                chart_type="backtest_results",
                cause=e
            ) from e
    

    @staticmethod
    def create_performance_metrics_chart(results: Dict[str, Any]) -> go.Figure:
        """
        Create a radar chart of performance metrics.
        
        Args:
            results: Dictionary containing backtest results with metrics.
            
        Returns:
            Interactive Plotly figure with performance metrics.
            
        Raises:
            ChartError: If metrics chart creation fails.
            ChartDataError: If metrics data is invalid.
        """
        try:
            if 'metrics' not in results:
                raise ChartDataError(
                    "Results must contain 'metrics' field",
                    data_type="performance_metrics"
                )
            
            metrics = results['metrics']
            
            # Prepare data for radar chart with normalization
            categories = [
                'Total Return',
                'Sharpe Ratio',
                'Win Rate',
                'Profit Factor',
                'Alpha vs B&H'
            ]
            
            # Normalize values to 0-100 scale for better display
            values = [
                min(max(metrics.get('total_return', 0) * 100, -100), 100) + 100,  # Scale to 0-200
                min(max(metrics.get('sharpe_ratio', 0) * 20, -100), 100) + 100,   # Scale and shift
                metrics.get('win_rate', 0) * 100,                                 # Already 0-1
                min(metrics.get('profit_factor', 0) * 20, 100),                   # Scale down
                min(max((metrics.get('alpha', 0) + 0.5) * 100, 0), 100)           # Shift and scale
            ]
            
            # Create radar chart
            chart = go.Figure()
            
            chart.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='Performance',
                line_color='#1f77b4',
                fillcolor='rgba(31, 119, 180, 0.2)'
            ))
            
            chart.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 200],  # Adjusted for normalized values
                        ticksuffix='%'
                    )
                ),
                showlegend=False,
                title="Performance Metrics (Normalized)",
                template='plotly_white'
            )
            
            logger.info("Performance metrics radar chart created successfully")
            return chart
            
        except (ChartError, ChartDataError):
            raise
        except Exception as e:
            raise ChartError(
                f"Unexpected error creating performance metrics chart: {str(e)}",
                chart_type="performance_metrics",
                cause=e
            ) from e
    

    @staticmethod
    def create_drawdown_chart(results: Dict[str, Any]) -> go.Figure:
        """
        Create a drawdown chart showing portfolio drawdown over time.
        
        Args:
            results: Dictionary containing backtest results with portfolio.
            
        Returns:
            Interactive Plotly figure showing drawdown evolution.
            
        Raises:
            ChartError: If drawdown chart creation fails.
            ChartDataError: If portfolio data is invalid.
        """
        try:
            if 'portfolio' not in results:
                raise ChartDataError(
                    "Results must contain 'portfolio' field",
                    data_type="portfolio"
                )
            
            portfolio = results['portfolio']
            
            try:
                # Calculate drawdown
                drawdown = portfolio.drawdown()
                
                if drawdown.empty:
                    raise ChartDataError(
                        "Portfolio drawdown data is empty",
                        data_type="drawdown"
                    )
                
                # Create drawdown chart
                chart = go.Figure()
                
                chart.add_trace(go.Scatter(
                    x=drawdown.index,
                    y=drawdown.values * 100,  # Convert to percentage
                    fill='tonexty',
                    fillcolor='rgba(214, 39, 40, 0.3)',
                    line_color='#d62728',
                    name='Drawdown',
                    hovertemplate='Drawdown: %{y:.2f}%<br>Date: %{x}<extra></extra>'
                ))
                
                chart.update_layout(
                    title="Portfolio Drawdown Evolution",
                    xaxis_title="Date",
                    yaxis_title="Drawdown (%)",
                    hovermode='x',
                    template='plotly_white'
                )
                
                # Add reference line at 0
                chart.add_hline(y=0, line_dash="dash", line_color="#7f7f7f")
                
                # Calculate max drawdown for annotation
                max_drawdown = drawdown.min() * 100
                chart.add_annotation(
                    text=f"Max Drawdown: {max_drawdown:.2f}%",
                    xref="paper", yref="paper",
                    x=0.02, y=0.98,
                    showarrow=False,
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="#d62728",
                    borderwidth=1
                )
                
                logger.info("Drawdown chart created successfully")
                return chart
                
            except AttributeError:
                # Portfolio doesn't have drawdown method
                raise ChartDataError(
                    "Portfolio object must have a 'drawdown' method",
                    data_type="portfolio_methods"
                )
            except Exception as e:
                raise ChartError(
                    f"Failed to calculate or plot drawdown: {str(e)}",
                    chart_type="drawdown",
                    cause=e
                ) from e
                
        except (ChartError, ChartDataError):
            raise
        except Exception as e:
            raise ChartError(
                f"Unexpected error creating drawdown chart: {str(e)}",
                chart_type="drawdown",
                cause=e
            ) from e
    

    @staticmethod
    def display_charts(results: Dict[str, Any]) -> None:
        """
        Display all performance charts in sequence.
        
        Args:
            results: Dictionary containing complete backtest results.
            
        Raises:
            ChartError: If any chart creation fails.
            
        Example:
            >>> ChartBuilder.display_charts(backtest_results)
        """
        try:
            logger.info("Displaying all performance charts")
            
            # Main backtest chart
            try:
                main_chart = ChartBuilder.create_backtest_charts(results)
                main_chart.show()
                logger.debug("Main backtest chart displayed")
            except Exception as e:
                logger.error(f"Failed to display main chart: {e}")
                raise

            # Performance metrics chart
            try:
                metrics_chart = ChartBuilder.create_performance_metrics_chart(results)
                metrics_chart.show()
                logger.debug("Performance metrics chart displayed")
            except Exception as e:
                logger.warning(f"Failed to display metrics chart: {e}")
                # Don't raise - this is optional

            # Drawdown chart
            try:
                drawdown_chart = ChartBuilder.create_drawdown_chart(results)
                drawdown_chart.show()
                logger.debug("Drawdown chart displayed")
            except Exception as e:
                logger.warning(f"Failed to display drawdown chart: {e}")
                # Don't raise - this is optional
            
            logger.info("All charts displayed successfully")
            
        except Exception as e:
            raise ChartError(
                f"Failed to display all charts: {str(e)}",
                chart_type="all_plots",
                cause=e
            ) from e
    

    @staticmethod
    def create_comparison_chart(
        results_list: List[Dict[str, Any]],
        metric: str = 'portfolio_value',
        title: Optional[str] = None
    ) -> go.Figure:
        """
        Create a comparison chart for multiple strategy results.
        
        Args:
            results_list: List of backtest results to compare.
            metric: Metric to compare ('portfolio_value', 'drawdown', etc.).
            title: Custom chart title (optional).
            
        Returns:
            Interactive Plotly figure comparing multiple strategies.
            
        Raises:
            ChartError: If comparison chart creation fails.
            ValueError: If invalid parameters are provided.
            
        Example:
            >>> comparison_fig = Visualizer.create_comparison_chart(
            ...     [results1, results2], metric='portfolio_value'
            ... )
            >>> comparison_chart.show()
        """
        try:
            if not isinstance(results_list, list) or len(results_list) < 2:
                raise ValueError("results_list must be a list with at least 2 results")
            
            if metric not in ['portfolio_value', 'drawdown']:
                raise ValueError("metric must be 'portfolio_value' or 'drawdown'")
            
            chart = go.Figure()
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
            
            for i, results in enumerate(results_list):
                try:
                    strategy_name = results.get('strategy', {}).get('name', f'Strategy {i+1}')
                    color = colors[i % len(colors)]
                    
                    if metric == 'portfolio_value':
                        portfolio_value = results['portfolio'].value()
                        chart.add_trace(go.Scatter(
                            x=portfolio_value.index,
                            y=portfolio_value.values,
                            name=strategy_name,
                            line=dict(color=color, width=2),
                            hovertemplate=f'{strategy_name}<br>Value: $%{{y:,.2f}}<br>Date: %{{x}}<extra></extra>'
                        ))
                    
                    elif metric == 'drawdown':
                        drawdown = results['portfolio'].drawdown() * 100
                        chart.add_trace(go.Scatter(
                            x=drawdown.index,
                            y=drawdown.values,
                            name=strategy_name,
                            line=dict(color=color, width=2),
                            hovertemplate=f'{strategy_name}<br>Drawdown: %{{y:.2f}}%<br>Date: %{{x}}<extra></extra>'
                        ))
                
                except Exception as e:
                    logger.warning(f"Failed to add strategy {i+1} to comparison: {e}")
                    continue
            
            # Configure layout
            chart_title = title or f"Strategy Comparison - {metric.replace('_', ' ').title()}"
            y_title = "Portfolio Value ($)" if metric == 'portfolio_value' else "Drawdown (%)"
            
            chart.update_layout(
                title=chart_title,
                xaxis_title="Date",
                yaxis_title=y_title,
                hovermode='x unified',
                template='plotly_white',
                height=600
            )
            
            if metric == 'drawdown':
                chart.add_hline(y=0, line_dash="dash", line_color="#7f7f7f")
            
            logger.info(f"Comparison chart created for {len(results_list)} strategies")
            return chart
            
        except (ValueError, ChartError):
            raise
        except Exception as e:
            raise ChartError(
                f"Unexpected error creating comparison chart: {str(e)}",
                chart_type="comparison",
                cause=e
            ) from e
    
    
    @staticmethod
    def save_chart_to_html_file(
        chart: go.Figure,
        filename: str,
        format: str = 'html',
        width: Optional[int] = None,
        height: Optional[int] = None
    ) -> str:
        """
        Save a Plotly figure to file.
        
        Args:
            chart: Plotly figure to save.
            filename: Output filename (without extension).
            format: Output format ('html', 'png', 'pdf', 'svg').
            width: Image width for static formats (optional).
            height: Image height for static formats (optional).
            
        Returns:
            Path to the saved file.
            
        Raises:
            ChartError: If saving fails.
            ValueError: If invalid parameters are provided.
            
        Example:
            >>> chart = chart_builder.create_backtest_charts(results)
            >>> saved_path = ChartBuilder.save_chart_to_html_file(chart, "backtest_chart", "html")
        """
        try:
            if not isinstance(filename, str) or not filename.strip():
                raise ValueError("filename must be a non-empty string")
            
            if format not in ['html', 'png', 'pdf', 'svg']:
                raise ValueError("format must be one of: html, png, pdf, svg")
            
            # Add appropriate extension
            full_filename = f"{filename.strip()}.{format}"
            
            if format == 'html':
                chart.write_html(full_filename)
            else:
                # For static formats, use write_image (requires kaleido)
                try:
                    chart.write_image(
                        full_filename,
                        width=width,
                        height=height,
                        format=format
                    )
                except Exception as e:
                    raise ChartError(
                        f"Failed to save static image. Make sure 'kaleido' is installed: {str(e)}",
                        chart_type="static_export",
                        cause=e
                    ) from e
            
            logger.info(f"Chart saved successfully: {full_filename}")
            return full_filename
            
        except (ValueError, ChartError):
            raise
        except Exception as e:
            raise ChartError(
                f"Unexpected error saving chart: {str(e)}",
                chart_type="save_operation",
                cause=e
            ) from e