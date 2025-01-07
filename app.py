from flask import Flask, render_template, jsonify, request
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine
import numpy as np
import json

app = Flask(__name__)
engine = create_engine('mysql+pymysql://root:root@localhost:8889/blockchain_fees')

def get_time_range_query(time_range):
    ranges = {
        "24h": "INTERVAL 24 HOUR",
        "7d": "INTERVAL 7 DAY",
        "30d": "INTERVAL 30 DAY",
        "1y": "INTERVAL 1 YEAR"
    }
    return ranges.get(time_range, "INTERVAL 24 HOUR")

def get_stats(df):
    try:
        return {
            "eth_gas": round(df[df['blockchain'] == 'ETH']['average_fee'].mean(), 2),
            "eth_gas_trend": round(((df[df['blockchain'] == 'ETH']['average_fee'].iloc[-1] / 
                                   df[df['blockchain'] == 'ETH']['average_fee'].iloc[0]) - 1) * 100, 2),
            "bnb_price": round(df[df['blockchain'] == 'BNB']['average_fee'].mean(), 2),
            "sol_tps": round(df[df['blockchain'] == 'SOL']['transaction_volume'].mean() / 3600, 2),
            "total_tps": round(df['transaction_volume'].mean() / 3600, 2)
        }
    except Exception as e:
        print(f"Error calculating stats: {str(e)}")
        return {
            "eth_gas": 0,
            "eth_gas_trend": 0,
            "bnb_price": 0,
            "sol_tps": 0,
            "total_tps": 0
        }

def generate_mock_data():
    current_time = datetime.now()
    times = [current_time - timedelta(hours=x) for x in range(24)]
    simulated_data = []
    for t in times:
        # Simulate lower fees during weekends
        weekend_factor = 0.7 if t.weekday() >= 5 else 1.0
        # Simulate lower fees during night hours (0-6)
        hour_factor = 0.8 if 0 <= t.hour <= 6 else 1.0
        
        simulated_data.extend([
            {'blockchain': 'ETH', 
             'average_fee': np.random.uniform(30, 100) * weekend_factor * hour_factor, 
             'transaction_volume': np.random.uniform(1000, 5000), 
             'timestamp': t},
            {'blockchain': 'BNB', 
             'average_fee': np.random.uniform(0.1, 1) * weekend_factor * hour_factor, 
             'transaction_volume': np.random.uniform(2000, 6000), 
             'timestamp': t},
            {'blockchain': 'SOL', 
             'average_fee': np.random.uniform(0.001, 0.01) * weekend_factor * hour_factor, 
             'transaction_volume': np.random.uniform(3000, 7000), 
             'timestamp': t}
        ])
    return pd.DataFrame(simulated_data)

def analyze_fee_patterns(df):
    predictions = {}
    comparisons = {}
    
    day_names = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    
    for blockchain in df['blockchain'].unique():
        blockchain_data = df[df['blockchain'] == blockchain]
        
        # Analyse par jour de la semaine
        daily_avg = blockchain_data.groupby(blockchain_data['timestamp'].dt.dayofweek)['average_fee'].mean()
        best_days = daily_avg.nsmallest(3)
        
        # Analyse par heure
        hourly_avg = blockchain_data.groupby(blockchain_data['timestamp'].dt.hour)['average_fee'].mean()
        best_hours = hourly_avg.nsmallest(3)
        
        # Calcul des économies potentielles
        avg_fee = float(blockchain_data['average_fee'].mean())
        best_time_fee = float(best_days.iloc[0])
        potential_savings = float(((avg_fee - best_time_fee) / avg_fee) * 100)
        
        predictions[blockchain] = {
            'best_days': int(best_days.index[0]),  # Convertir en int standard
            'best_hours': [int(h) for h in best_hours.index.tolist()],  # Convertir la liste en int standard
            'average_fee': float(avg_fee),  # Convertir en float standard
            'lowest_fee': float(best_time_fee),  # Convertir en float standard
            'potential_savings': float(potential_savings),  # Convertir en float standard
            'best_day_name': day_names[int(best_days.index[0])],
            'best_time_description': f"Le meilleur moment est {day_names[int(best_days.index[0])]} à {int(best_hours.index[0])}h"
        }
    
    # Comparaison entre blockchains
    avg_fees = {blockchain: float(data['average_fee']) for blockchain, data in predictions.items()}
    cheapest_chain = min(avg_fees.items(), key=lambda x: x[1])[0]
    highest_chain = max(avg_fees.items(), key=lambda x: x[1])[0]
    
    fee_comparison = {}
    for blockchain, fee in avg_fees.items():
        comparison = {
            'relative_cost': float(fee / avg_fees[cheapest_chain]),
            'is_cheapest': blockchain == cheapest_chain,
            'savings_vs_highest': float(((avg_fees[highest_chain] - fee) / avg_fees[highest_chain]) * 100) if blockchain != highest_chain else 0,
            'recommendation': "Recommandé" if blockchain == cheapest_chain else "Plus coûteux"
        }
        fee_comparison[blockchain] = comparison
    
    return {
        'predictions': predictions,
        'blockchain_comparison': {
            'cheapest_chain': cheapest_chain,
            'highest_chain': highest_chain,
            'comparisons': fee_comparison
        }
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send')
def send():
    return render_template('send.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/documentation')
def documentation():
    return render_template('documentation.html')

@app.route('/FAQ')
def faq():
    return render_template('faq.html')

@app.route('/guide')
def guide():
    return render_template('guide.html')

@app.route('/api')
def api():
    return render_template('api.html')

@app.route('/get_data')
def get_data():
    try:
        time_range = request.args.get('timeRange', '24h')
        time_query = get_time_range_query(time_range)
        
        query = f"""
        SELECT 
            symbol as blockchain,
            fee as average_fee,
            transaction_volume,
            timestamp
        FROM transaction_fees
        WHERE timestamp >= NOW() - {time_query}
        ORDER BY timestamp
        """
        
        try:
            df = pd.read_sql(query, engine)
            if df.empty:
                df = generate_mock_data()
        except Exception as e:
            print(f"Database error: {str(e)}")
            df = generate_mock_data()

        # Configuration des couleurs et analyse des patterns
        colors = {'ETH': '#627EEA', 'BNB': '#F3BA2F', 'SOL': '#00FFA3'}
        fee_analysis = analyze_fee_patterns(df)

        # Création du dashboard
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Frais en Temps Réel',
                'Volume des Transactions',
                'Distribution des Frais',
                'Analyse Horaire',
                'Tendances des Prix',
                'Corrélation Volume/Prix'
            ),
            specs=[
                [{"type": "scatter"}, {"type": "bar"}],
                [{"type": "histogram"}, {"type": "scatter"}],
                [{"type": "scatter"}, {"type": "scatter"}]
            ],
            vertical_spacing=0.12,
            horizontal_spacing=0.1
        )

  # 1. Frais en temps réel
        for blockchain in df['blockchain'].unique():
            data = df[df['blockchain'] == blockchain]
            fig.add_trace(
                go.Scatter(
                    x=data['timestamp'],
                    y=data['average_fee'],
                    name=f"{blockchain} Fees",
                    line=dict(color=colors[blockchain])
                ),
                row=1, col=1
            )

        # 2. Volume des transactions
        for blockchain in df['blockchain'].unique():
            data = df[df['blockchain'] == blockchain]
            fig.add_trace(
                go.Bar(
                    x=data['timestamp'],
                    y=data['transaction_volume'],
                    name=f"{blockchain} Volume",
                    marker_color=colors[blockchain],
                    opacity=0.7
                ),
                row=1, col=2
            )

        # 3. Distribution des frais
        for blockchain in df['blockchain'].unique():
            data = df[df['blockchain'] == blockchain]
            fig.add_trace(
                go.Histogram(
                    x=data['average_fee'],
                    name=f"{blockchain} Distribution",
                    marker_color=colors[blockchain],
                    opacity=0.7,
                    nbinsx=30
                ),
                row=2, col=1
            )

        # 4. Analyse horaire des frais moyens
        for blockchain in df['blockchain'].unique():
            data = df[df['blockchain'] == blockchain]
            hourly_avg = data.groupby(data['timestamp'].dt.hour)['average_fee'].mean()
            fig.add_trace(
                go.Scatter(
                    x=list(hourly_avg.index),
                    y=hourly_avg.values,
                    name=f"{blockchain} Hourly Avg",
                    line=dict(color=colors[blockchain])
                ),
                row=2, col=2
            )

        # 5. Tendances des prix (moyenne mobile)
        for blockchain in df['blockchain'].unique():
            data = df[df['blockchain'] == blockchain]
            rolling_mean = data['average_fee'].rolling(window=6).mean()
            fig.add_trace(
                go.Scatter(
                    x=data['timestamp'],
                    y=rolling_mean,
                    name=f"{blockchain} Trend",
                    line=dict(color=colors[blockchain])
                ),
                row=3, col=1
            )

        # 6. Corrélation Volume/Prix
        for blockchain in df['blockchain'].unique():
            data = df[df['blockchain'] == blockchain]
            fig.add_trace(
                go.Scatter(
                    x=data['transaction_volume'],
                    y=data['average_fee'],
                    mode='markers',
                    name=f"{blockchain} Correlation",
                    marker=dict(
                        color=colors[blockchain],
                        size=8,
                        opacity=0.6
                    )
                ),
                row=3, col=2
            )

        # Mise à jour des layouts pour chaque subplot
        fig.update_xaxes(title_text="Temps", row=1, col=1)
        fig.update_xaxes(title_text="Temps", row=1, col=2)
        fig.update_xaxes(title_text="Frais", row=2, col=1)
        fig.update_xaxes(title_text="Heure", row=2, col=2)
        fig.update_xaxes(title_text="Temps", row=3, col=1)
        fig.update_xaxes(title_text="Volume", row=3, col=2)

        fig.update_yaxes(title_text="Frais (USD)", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=1, col=2)
        fig.update_yaxes(title_text="Fréquence", row=2, col=1)
        fig.update_yaxes(title_text="Frais moyens", row=2, col=2)
        fig.update_yaxes(title_text="Tendance des frais", row=3, col=1)
        fig.update_yaxes(title_text="Frais", row=3, col=2)

        fig.update_layout(
            height=1200,
            title_text="Analyse des Frais Blockchain",
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
        stats = get_stats(df)

        return jsonify({
            'dashboard': fig.to_json(),
            'stats': stats,
            'predictions': fee_analysis
        })

    except Exception as e:
        print(f"Error in get_data: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)