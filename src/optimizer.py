import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransactionOptimizer:
    def __init__(self):
        self.blockchains = ['ETH', 'BNB', 'SOL']
        self.min_confirmations = {
            'ETH': 12,
            'BNB': 15,
            'SOL': 32
        }
        self.avg_block_times = {
            'ETH': 12,  # secondes
            'BNB': 3,
            'SOL': 0.4
        }

    def calculate_transaction_cost(self, amount: float, fee: float, blockchain: str) -> float:
        """Calcule le coût total d'une transaction incluant les frais"""
        base_costs = {
            'ETH': lambda x, f: (x * 0.001) + (f * 21000),  # 21000 gas pour transfer standard
            'BNB': lambda x, f: (x * 0.0005) + f,
            'SOL': lambda x, f: 0.000005 + f  # Frais fixe + frais variable
        }
        
        return base_costs[blockchain](amount, fee)

    def estimate_confirmation_time(self, blockchain: str, network_congestion: float) -> float:
        """Estime le temps de confirmation basé sur la congestion"""
        base_time = self.min_confirmations[blockchain] * self.avg_block_times[blockchain]
        congestion_factor = 1 + (network_congestion * 0.5)  # Augmente avec la congestion
        return base_time * congestion_factor

    def find_optimal_route(self, 
                         amount: float,
                         predictions: Dict[str, pd.Series],
                         congestion_data: Dict[str, float],
                         max_wait_time: int = 3600) -> Dict:
        """
        Trouve la meilleure route pour la transaction
        
        Args:
            amount: Montant à envoyer
            predictions: Prédictions de frais par blockchain
            congestion_data: Données de congestion actuelles
            max_wait_time: Temps d'attente maximum accepté (en secondes)
        """
        optimal_routes = []

        for blockchain in self.blockchains:
            fees = predictions[blockchain]
            
            # Analyse sur les prochaines 24h
            for timestamp, fee in fees.head(24).items():
                total_cost = self.calculate_transaction_cost(amount, fee, blockchain)
                est_confirmation_time = self.estimate_confirmation_time(
                    blockchain, 
                    congestion_data.get(blockchain, 0)
                )
                
                if est_confirmation_time <= max_wait_time:
                    optimal_routes.append({
                        'blockchain': blockchain,
                        'timestamp': timestamp,
                        'fee': fee,
                        'total_cost': total_cost,
                        'est_confirmation_time': est_confirmation_time
                    })

        # Trier par coût total
        optimal_routes.sort(key=lambda x: x['total_cost'])
        
        return {
            'best_routes': optimal_routes[:3],
            'analysis': {
                'avg_cost_by_chain': {
                    chain: np.mean([r['total_cost'] for r in optimal_routes 
                                  if r['blockchain'] == chain])
                    for chain in self.blockchains
                },
                'avg_confirmation_times': {
                    chain: np.mean([r['est_confirmation_time'] for r in optimal_routes 
                                  if r['blockchain'] == chain])
                    for chain in self.blockchains
                }
            }
        }

    def batch_optimize(self, 
                      transactions: List[Dict],
                      predictions: Dict[str, pd.Series],
                      congestion_data: Dict[str, float]) -> Dict:
        """Optimise un lot de transactions"""
        results = []
        total_cost_by_chain = {chain: 0 for chain in self.blockchains}
        
        for tx in transactions:
            amount = tx['amount']
            optimal_route = self.find_optimal_route(
                amount, 
                predictions, 
                congestion_data
            )
            
            best_route = optimal_route['best_routes'][0]
            total_cost_by_chain[best_route['blockchain']] += best_route['total_cost']
            
            results.append({
                'transaction_id': tx.get('id'),
                'amount': amount,
                'recommended_route': best_route,
                'alternatives': optimal_route['best_routes'][1:]
            })

        return {
            'optimized_transactions': results,
            'summary': {
                'total_cost_by_chain': total_cost_by_chain,
                'total_transactions': len(transactions),
                'average_cost_per_tx': sum(total_cost_by_chain.values()) / len(transactions)
            }
        }

    def generate_schedule(self, 
                         batch_results: Dict,
                         max_concurrent_tx: int = 50) -> Dict:
        """Génère un planning d'exécution optimal"""
        transactions = batch_results['optimized_transactions']
        schedule = {}
        
        # Grouper par blockchain et timestamp
        for tx in transactions:
            route = tx['recommended_route']
            key = f"{route['blockchain']}_{route['timestamp']}"
            if key not in schedule:
                schedule[key] = []
            schedule[key].append(tx)

        # Réorganiser si nécessaire pour respecter max_concurrent_tx
        final_schedule = {}
        for key, txs in schedule.items():
            if len(txs) > max_concurrent_tx:
                chunks = [txs[i:i + max_concurrent_tx] 
                         for i in range(0, len(txs), max_concurrent_tx)]
                for i, chunk in enumerate(chunks):
                    new_key = f"{key}_batch_{i}"
                    final_schedule[new_key] = chunk
            else:
                final_schedule[key] = txs

        return {
            'schedule': final_schedule,
            'metrics': {
                'total_batches': len(final_schedule),
                'max_batch_size': max(len(batch) for batch in final_schedule.values()),
                'min_batch_size': min(len(batch) for batch in final_schedule.values())
            }
        }