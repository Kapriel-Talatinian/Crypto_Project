import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
from sklearn.preprocessing import MinMaxScaler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BlockchainAnalytics:
    def __init__(self, engine):
        self.engine = engine
        self.scaler = MinMaxScaler()
        
    def get_historical_stats(self, blockchain: str, days: int = 30) -> Dict:
        """Analyse les statistiques historiques pour une blockchain"""
        query = f"""
        SELECT 
            fee as average_fee,
            transaction_volume,
            timestamp
        FROM transaction_fees
        WHERE symbol = '{blockchain}'
        AND timestamp >= NOW() - INTERVAL {days} DAY
        ORDER BY timestamp
        """
        
        df = pd.read_sql(query, self.engine)
        
        # Calcul des statistiques de base
        stats = {
            'mean_fee': float(df['average_fee'].mean()),
            'median_fee': float(df['average_fee'].median()),
            'std_fee': float(df['average_fee'].std()),
            'min_fee': float(df['average_fee'].min()),
            'max_fee': float(df['average_fee'].max()),
            'volatility': float(df['average_fee'].std() / df['average_fee'].mean()),
            'fee_percentiles': {
                'p25': float(df['average_fee'].quantile(0.25)),
                'p50': float(df['average_fee'].quantile(0.50)),
                'p75': float(df['average_fee'].quantile(0.75)),
                'p90': float(df['average_fee'].quantile(0.90))
            }
        }
        
        return stats

    def analyze_cost_patterns(self, days: int = 30) -> Dict:
        """Analyse les patterns de coûts sur toutes les blockchains"""
        patterns = {}
        
        for blockchain in ['ETH', 'BNB', 'SOL']:
            query = f"""
            SELECT 
                DATE(timestamp) as date,
                HOUR(timestamp) as hour,
                DAYOFWEEK(timestamp) as day_of_week,
                AVG(fee) as avg_fee,
                AVG(transaction_volume) as avg_volume
            FROM transaction_fees
            WHERE symbol = '{blockchain}'
            AND timestamp >= NOW() - INTERVAL {days} DAY
            GROUP BY DATE(timestamp), HOUR(timestamp), DAYOFWEEK(timestamp)
            """
            
            df = pd.read_sql(query, self.engine)
            
            # Analyse horaire
            hourly_pattern = df.groupby('hour')['avg_fee'].agg([
                'mean', 'std', 'min', 'max'
            ]).round(4)
            
            # Analyse journalière
            daily_pattern = df.groupby('day_of_week')['avg_fee'].agg([
                'mean', 'std', 'min', 'max'
            ]).round(4)
            
            # Corrélation volume/frais
            volume_correlation = df['avg_fee'].corr(df['avg_volume'])
            
            patterns[blockchain] = {
                'hourly_pattern': hourly_pattern.to_dict(),
                'daily_pattern': daily_pattern.to_dict(),
                'volume_correlation': float(volume_correlation)
            }
            
        return patterns

    def detect_anomalies(self, window: int = 24) -> Dict:
        """Détecte les anomalies dans les frais de transaction"""
        anomalies = {}
        
        for blockchain in ['ETH', 'BNB', 'SOL']:
            query = f"""
            SELECT 
                fee as average_fee,
                timestamp
            FROM transaction_fees
            WHERE symbol = '{blockchain}'
            AND timestamp >= NOW() - INTERVAL {window} HOUR
            ORDER BY timestamp
            """
            
            df = pd.read_sql(query, self.engine)
            
            # Calcul des limites pour la détection d'anomalies
            rolling_mean = df['average_fee'].rolling(window=6).mean()
            rolling_std = df['average_fee'].rolling(window=6).std()
            
            upper_bound = rolling_mean + (2 * rolling_std)
            lower_bound = rolling_mean - (2 * rolling_std)
            
            # Détection des anomalies
            anomalies[blockchain] = {
                'high_fees': df[df['average_fee'] > upper_bound].to_dict('records'),
                'low_fees': df[df['average_fee'] < lower_bound].to_dict('records'),
                'thresholds': {
                    'upper': float(upper_bound.mean()),
                    'lower': float(lower_bound.mean())
                }
            }
        
        return anomalies

    def calculate_cost_savings(self, transactions: List[Dict], optimization_results: Dict) -> Dict:
        """Calcule les économies réalisées grâce à l'optimisation"""
        total_original_cost = 0
        total_optimized_cost = 0
        
        savings_by_chain = {
            'ETH': {'original': 0, 'optimized': 0},
            'BNB': {'original': 0, 'optimized': 0},
            'SOL': {'original': 0, 'optimized': 0}
        }
        
        for tx, opt_result in zip(transactions, optimization_results['optimized_transactions']):
            original_route = tx.get('original_chain', 'ETH')  # Default to ETH if not specified
            optimized_route = opt_result['recommended_route']['blockchain']
            
            original_cost = self.get_average_cost(original_route, tx['amount'])
            optimized_cost = opt_result['recommended_route']['total_cost']
            
            total_original_cost += original_cost
            total_optimized_cost += optimized_cost
            
            savings_by_chain[original_route]['original'] += original_cost
            savings_by_chain[optimized_route]['optimized'] += optimized_cost
        
        return {
            'total_savings': total_original_cost - total_optimized_cost,
            'savings_percentage': ((total_original_cost - total_optimized_cost) / total_original_cost) * 100,
            'savings_by_chain': savings_by_chain,
            'summary': {
                'total_transactions': len(transactions),
                'average_saving_per_tx': (total_original_cost - total_optimized_cost) / len(transactions)
            }
        }

    def get_average_cost(self, blockchain: str, amount: float) -> float:
        """Obtient le coût moyen pour une transaction sur une blockchain donnée"""
        query = f"""
        SELECT AVG(fee) as avg_fee
        FROM transaction_fees
        WHERE symbol = '{blockchain}'
        AND timestamp >= NOW() - INTERVAL 1 HOUR
        """
        
        df = pd.read_sql(query, self.engine)
        avg_fee = float(df['avg_fee'].iloc[0])
        
        # Calcul simplifié du coût total
        if blockchain == 'ETH':
            return (amount * 0.001) + (avg_fee * 21000)
        elif blockchain == 'BNB':
            return (amount * 0.0005) + avg_fee
        else:  # SOL
            return 0.000005 + avg_fee

    def generate_report(self, days: int = 30) -> Dict:
        """Génère un rapport complet d'analyse"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'period': f'{days} days',
            'historical_stats': {},
            'cost_patterns': self.analyze_cost_patterns(days),
            'recent_anomalies': self.detect_anomalies(),
            'recommendations': {}
        }
        
        # Ajouter les stats historiques pour chaque blockchain
        for blockchain in ['ETH', 'BNB', 'SOL']:
            report['historical_stats'][blockchain] = self.get_historical_stats(blockchain, days)
        
        # Générer des recommandations basées sur l'analyse
        for blockchain in ['ETH', 'BNB', 'SOL']:
            stats = report['historical_stats'][blockchain]
            patterns = report['cost_patterns'][blockchain]
            
            best_hours = sorted(
                patterns['hourly_pattern']['mean'].items(),
                key=lambda x: x[1]
            )[:3]
            
            report['recommendations'][blockchain] = {
                'best_hours': [int(hour) for hour, _ in best_hours],
                'fee_threshold': stats['fee_percentiles']['p75'],
                'volatility_level': 'high' if stats['volatility'] > 0.2 else 'moderate'
            }
        
        return report