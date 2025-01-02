import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from sqlalchemy import create_engine

class VisualizationGenerator:
    def __init__(self, db_handler):
        self.db_handler = db_handler
        self.engine = create_engine(f'mysql+mysqlconnector://root:root@localhost:8889/blockchain_fees')
        plt.style.use('dark_background')
        self.colors = {
            'ETH': '#627EEA',
            'BNB': '#F3BA2F',
            'SOL': '#00FFA3'
        }
    
    def get_data(self):
        query = """
        SELECT 
            symbol as blockchain,
            fee as average_fee,
            confirmation_time,
            transaction_volume,
            timestamp
        FROM transaction_fees
        WHERE timestamp >= NOW() - INTERVAL 10 MINUTE
        ORDER BY timestamp, blockchain
        """
        try:
            df = pd.read_sql(query, self.engine)
            return df
        except Exception as e:
            print(f"Erreur lors de la récupération des données: {e}")
            return pd.DataFrame()

    def generate_fee_comparison(self):
        df = self.get_data()
        if df.empty:
            return

        # Configuration du style
        plt.style.use('dark_background')
        
        # Création de la figure avec un ratio spécifique
        fig, ax = plt.subplots(figsize=(15, 8))
        
        # Tracer une ligne pour chaque blockchain
        for blockchain in df['blockchain'].unique():
            data = df[df['blockchain'] == blockchain]
            line = ax.plot(data['timestamp'], 
                          data['average_fee'],
                          label=blockchain,
                          color=self.colors.get(blockchain, '#333333'),
                          linewidth=2,
                          marker='o',
                          markersize=6)
            
            # Ajouter la dernière valeur à côté de la ligne
            if not data.empty:
                last_value = data['average_fee'].iloc[-1]
                ax.text(data['timestamp'].iloc[-1], last_value,
                    f'  ${last_value:.6f}',
                    verticalalignment='center',
                    fontsize=10,
                    color=self.colors.get(blockchain, '#333333'),
                    fontweight='bold')

        # Personnalisation du graphique
        ax.set_title('Comparaison des Frais de Transaction en Temps Réel',
                    fontsize=16, pad=20, fontweight='bold')
        ax.set_xlabel('Temps', fontsize=12, labelpad=10)
        ax.set_ylabel('Frais en USD', fontsize=12, labelpad=10)

        # Amélioration de la grille
        ax.grid(True, linestyle='--', alpha=0.2)
        ax.set_axisbelow(True)

        # Format des dates sur l'axe X
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.xticks(rotation=45)

        # Légende améliorée avec les temps de confirmation
        legend_elements = []
        for blockchain in df['blockchain'].unique():
            conf_time = df[df['blockchain'] == blockchain]['confirmation_time'].iloc[-1]
            legend_elements.append(
                f"{blockchain} (Confirmation: {conf_time}s)"
            )
        ax.legend(legend_elements, 
                 loc='upper left',
                 bbox_to_anchor=(1.05, 1),
                 borderaxespad=0.,
                 fontsize=10,
                 facecolor='black',
                 edgecolor='white')

        # Ajout d'informations statistiques
        stats_box = []
        for blockchain in df['blockchain'].unique():
            blockchain_data = df[df['blockchain'] == blockchain]
            stats_box.append(f"{blockchain}:")
            stats_box.append(f"  Min: ${blockchain_data['average_fee'].min():.6f}")
            stats_box.append(f"  Max: ${blockchain_data['average_fee'].max():.6f}")
            stats_box.append(f"  Avg: ${blockchain_data['average_fee'].mean():.6f}")
            stats_box.append("")

        plt.text(1.05, 0.5, '\n'.join(stats_box),
                 transform=ax.transAxes,
                 verticalalignment='center',
                 fontsize=10,
                 fontfamily='monospace',
                 bbox=dict(facecolor='black', edgecolor='white', alpha=0.8))

        # Ajustement de la mise en page
        plt.tight_layout()
        
        # Sauvegarde avec une haute résolution
        plt.savefig('blockchain_fees_comparison.png', 
                    dpi=300, 
                    bbox_inches='tight',
                    facecolor='black',
                    edgecolor='none')
        plt.close('all')

    def generate_eth_gas_history(self):
        df = self.get_eth_historical_data()
        if df.empty:
            return

        plt.figure(figsize=(12, 8))
        fig, ax = plt.subplots(figsize=(12, 8))

        ax.plot(df['timestamp'], df['gas_price'], 
                color=self.colors['ETH'], 
                linewidth=2, 
                label='Gas Price')

        df['rolling_avg'] = df['gas_price'].rolling(window=10).mean()
        ax.plot(df['timestamp'], df['rolling_avg'], 
                '--', color='#FF9B71', 
                linewidth=1.5, 
                label='Moving Average (10 points)')

        ax.set_title('Historique des Gas Fees Ethereum', 
                    pad=20, fontsize=16, fontweight='bold')
        ax.set_xlabel('Temps', fontsize=12)
        ax.set_ylabel('Gas Price (Gwei)', fontsize=12)

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.xticks(rotation=45)

        stats_text = (f"Min: ${df['gas_price'].min():.6f}\n"
                     f"Max: ${df['gas_price'].max():.6f}\n"
                     f"Avg: ${df['gas_price'].mean():.6f}")
        plt.text(0.02, 0.98, stats_text,
                transform=ax.transAxes,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()
        plt.tight_layout()

        plt.savefig('eth_gas_history.png', dpi=300, bbox_inches='tight')
        plt.close('all')

    def get_eth_historical_data(self):
        query = """
        SELECT 
            fee as gas_price,
            timestamp
        FROM transaction_fees
        WHERE symbol = 'ETH'
        AND timestamp >= NOW() - INTERVAL 1 HOUR
        ORDER BY timestamp
        """
        try:
            return pd.read_sql(query, self.engine)
        except Exception as e:
            print(f"Erreur lors de la récupération des données ETH: {e}")
            return pd.DataFrame()