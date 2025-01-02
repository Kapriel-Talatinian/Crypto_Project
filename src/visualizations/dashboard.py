import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

class BlockchainDashboard:
    def __init__(self, engine):
        self.engine = engine

    def create_fee_comparison_chart(self, timeframe='24h'):
        # Récupération des données
        query = f"""
        SELECT 
            symbol as blockchain,
            fee as average_fee,
            transaction_volume,
            timestamp
        FROM transaction_fees
        WHERE timestamp >= NOW() - INTERVAL {timeframe}
        ORDER BY timestamp
        """
        df = pd.read_sql(query, self.engine)

        # Création du graphique comparatif
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Comparaison des Frais', 'Volume des Transactions'),
            vertical_spacing=0.15
        )

        colors = {'ETH': '#627EEA', 'BNB': '#F3BA2F', 'SOL': '#00FFA3'}

        # Graphique des frais
        for blockchain in df['blockchain'].unique():
            blockchain_data = df[df['blockchain'] == blockchain]
            
            fig.add_trace(
                go.Scatter(
                    x=blockchain_data['timestamp'],
                    y=blockchain_data['average_fee'],
                    name=f"{blockchain} Fees",
                    line=dict(color=colors[blockchain]),
                    hovertemplate="<b>%{y:.8f}</b> USD<br>%{x}<extra></extra>"
                ),
                row=1, col=1
            )

            # Ajout du volume
            fig.add_trace(
                go.Bar(
                    x=blockchain_data['timestamp'],
                    y=blockchain_data['transaction_volume'],
                    name=f"{blockchain} Volume",
                    marker_color=colors[blockchain],
                    opacity=0.7
                ),
                row=2, col=1
            )

        # Mise en page
        fig.update_layout(
            height=800,
            title_text="Analyse des Frais et Volumes de Transaction",
            template='plotly_dark',
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ),
            hovermode='x unified'
        )

        return fig

    def create_prediction_chart(self, predictions_dict):
        fig = make_subplots(rows=1, cols=1)
        colors = {'ETH': '#627EEA', 'BNB': '#F3BA2F', 'SOL': '#00FFA3'}

        for blockchain, predictions in predictions_dict.items():
            fig.add_trace(
                go.Scatter(
                    x=predictions.index,
                    y=predictions.values,
                    name=f"{blockchain} Predicted",
                    line=dict(
                        color=colors[blockchain],
                        dash='dash'
                    ),
                    hovertemplate="<b>%{y:.8f}</b> USD<br>%{x}<extra></extra>"
                )
            )

        fig.update_layout(
            title="Prédiction des Frais sur 7 Jours",
            xaxis_title="Date",
            yaxis_title="Frais Estimés (USD)",
            template='plotly_dark',
            height=500,
            showlegend=True,
            hovermode='x unified'
        )

        return fig

    def create_optimization_chart(self, optimization_results):
        # Création d'un graphique pour visualiser les économies potentielles
        savings_data = optimization_results['savings_by_chain']
        
        fig = go.Figure()
        
        blockchains = list(savings_data.keys())
        original_costs = [data['original'] for data in savings_data.values()]
        optimized_costs = [data['optimized'] for data in savings_data.values()]

        fig.add_trace(go.Bar(
            name='Coûts Originaux',
            x=blockchains,
            y=original_costs,
            marker_color='#FF6B6B'
        ))

        fig.add_trace(go.Bar(
            name='Coûts Optimisés',
            x=blockchains,
            y=optimized_costs,
            marker_color='#4ECB71'
        ))

        fig.update_layout(
            title="Comparaison des Coûts: Original vs Optimisé",
            barmode='group',
            template='plotly_dark',
            height=400
        )

        return fig

    def create_analysis_dashboard(self, timeframe='24h'):
        # Création d'un dashboard complet
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Frais en Temps Réel',
                'Prédictions',
                'Volume des Transactions',
                'Analyse des Économies',
                'Distribution des Frais',
                'Congestion du Réseau'
            ),
            vertical_spacing=0.12,
            horizontal_spacing=0.1,
            specs=[
                [{"type": "scatter"}, {"type": "scatter"}],
                [{"type": "bar"}, {"type": "bar"}],
                [{"type": "histogram"}, {"type": "heatmap"}]
            ]
        )

        # Ajout des sous-graphiques...
        # [Le code pour ajouter chaque sous-graphique]

        fig.update_layout(
            height=1200,
            title_text="Dashboard d'Analyse des Frais Blockchain",
            template='plotly_dark',
            showlegend=True
        )

        return fig