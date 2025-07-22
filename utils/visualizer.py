"""
Module de visualisation des résultats de backtest.
"""

from typing import Dict, Any, Optional
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px


class Visualizer:
    """
    Classe pour créer des visualisations interactives des résultats de backtest.
    """
    
    @staticmethod
    def plot_backtest_results(results: Dict[str, Any], 
                            show_signals: bool = True,
                            show_indicators: bool = True,
                            save_path: Optional[str] = None) -> go.Figure:
        """
        Crée un graphique interactif des résultats de backtest.
        
        Args:
            results: Résultats du backtest
            show_signals: Afficher les signaux d'achat/vente
            show_indicators: Afficher les indicateurs techniques
            save_path: Chemin pour sauvegarder le graphique (optionnel)
            
        Returns:
            Figure plotly
        """
        data = results['data']
        portfolio = results['portfolio']
        buy_signals = results['buy_signals']
        sell_signals = results['sell_signals']
        strategy = results['strategy']
        
        # Création des sous-graphiques
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('Prix et Signaux', 'Valeur du Portfeuille', 'Volume'),
            row_heights=[0.5, 0.3, 0.2]
        )
        
        # 1. Graphique des prix avec chandelier
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='Prix',
                increasing_line_color='#2ca02c',  # Green
                decreasing_line_color='#d62728'   # Red
            ),
            row=1, col=1
        )
        
        # Indicateurs techniques (si disponibles)
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
        
        # Signaux d'achat et de vente
        if show_signals:
            
            # Signaux d'achat
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
                        name='Achat',
                        hovertemplate='Achat: %{y:.2f}<br>Date: %{x}<extra></extra>'
                    ),
                    row=1, col=1
                )
            
            # Signaux de vente
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
                        name='Vente',
                        hovertemplate='Vente: %{y:.2f}<br>Date: %{x}<extra></extra>'
                    ),
                    row=1, col=1
                )
        
        # 2. Valeur du portfolio
        portfolio_value = portfolio.value()
        fig.add_trace(
            go.Scatter(
                x=portfolio_value.index,
                y=portfolio_value.values,
                name='Valeur Portfolio',
                line=dict(color='#1f77b4', width=2),  # Blue
                hovertemplate='Valeur: $%{y:,.2f}<br>Date: %{x}<extra></extra>'
            ),
            row=2, col=1
        )
        
        # Ligne de référence (capital initial)
        fig.add_hline(
            y=results['parameters']['initial_cash'],
            line_dash="dash",
            line_color="#7f7f7f",  # Gray
            annotation_text="Capital initial",
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
        
        # Mise en forme
        fig.update_layout(
            title=f"Backtest: {strategy['name']} - Rendement: {results['metrics']['total_return']:.2%}",
            # xaxis_title="Date",
            height=800,
            showlegend=True,
            hovermode='x unified'
        )
        
        # Axes Y
        fig.update_yaxes(title_text="Prix ($)", row=1, col=1)
        fig.update_yaxes(title_text="Valeur ($)", row=2, col=1)
        fig.update_yaxes(title_text="Volume", row=3, col=1)
        
        # Suppression du sélecteur de plage pour le chandelier
        fig.update_layout(xaxis_rangeslider_visible=False)
        
        # Sauvegarde si demandée
        if save_path:
            fig.write_html(save_path)
            print(f"Graphique sauvegardé: {save_path}")
        
        return fig
    
    @staticmethod
    def plot_performance_metrics(results: Dict[str, Any]) -> go.Figure:
        """
        Crée un graphique des métriques de performance.
        
        Args:
            results: Résultats du backtest
            
        Returns:
            Figure plotly avec les métriques
        """
        metrics = results['metrics']
        
        # Préparation des données pour le graphique radar
        categories = [
            'Rendement Total',
            'Ratio Sharpe',
            'Taux de Réussite',
            'Facteur de Profit',
            'Alpha vs B&H'
        ]
        
        values = [
            min(metrics['total_return'] * 100, 100),  # Normalisation
            min(metrics['sharpe_ratio'] * 20, 100),   # Normalisation
            metrics['win_rate'] * 100,
            min(metrics['profit_factor'] * 20, 100),  # Normalisation
            min((metrics['alpha'] + 0.5) * 100, 100) # Normalisation
        ]
        
        # Graphique radar
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
            title="Métriques de Performance (Normalisées)"
        )
        
        return fig
    
    @staticmethod
    def plot_drawdown(results: Dict[str, Any]) -> go.Figure:
        """
        Crée un graphique du drawdown.
        
        Args:
            results: Résultats du backtest
            
        Returns:
            Figure plotly du drawdown
        """
        portfolio = results['portfolio']
        
        try:
            drawdown = portfolio.drawdown()
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=drawdown.index,
                y=drawdown.values * 100,  # Conversion en pourcentage
                fill='tonexty',
                fillcolor='rgba(214, 39, 40, 0.3)',  # Light red
                line_color='#d62728',  # Red
                name='Drawdown',
                hovertemplate='Drawdown: %{y:.2f}%<br>Date: %{x}<extra></extra>'
            ))
            
            fig.update_layout(
                title="Évolution du Drawdown",
                xaxis_title="Date",
                yaxis_title="Drawdown (%)",
                hovermode='x'
            )
            
            # Ligne de référence à 0
            fig.add_hline(y=0, line_dash="dash", line_color="#7f7f7f")  # Gray
            
            return fig
            
        except Exception as e:
            print(f"Erreur lors de la création du graphique drawdown: {e}")
            return go.Figure().add_annotation(text="Erreur: impossible de calculer le drawdown")
    
    @staticmethod
    def show_all_plots(results: Dict[str, Any]) -> None:
        """
        Affiche tous les graphiques de performance.
        
        Args:
            results: Résultats du backtest
        """
        # Graphique principal
        main_fig = Visualizer.plot_backtest_results(results)
        main_fig.show()
        
        # Métriques de performance
        metrics_fig = Visualizer.plot_performance_metrics(results)
        metrics_fig.show()
        
        # Drawdown
        drawdown_fig = Visualizer.plot_drawdown(results)
        drawdown_fig.show()