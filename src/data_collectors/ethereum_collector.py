from web3 import Web3
import time
import statistics

class EthereumCollector:
    def __init__(self, node_url):
        self.web3 = Web3(Web3.HTTPProvider(node_url))
    
    def get_gas_prices(self):
        try:
            latest_block = self.web3.eth.block_number
            blocks = []
            for i in range(latest_block - 5, latest_block):  # Réduit à 5 blocs pour plus de rapidité
                block = self.web3.eth.get_block(i, full_transactions=True)
                blocks.append(block)
            
            gas_prices = []
            total_volume = 0
            for block in blocks:
                for tx in block['transactions']:
                    gas_prices.append(tx['gasPrice'])
                    total_volume += float(self.web3.from_wei(tx.get('value', 0), 'ether'))
            
            if gas_prices:
                avg_gas_price = statistics.mean(gas_prices)
                return {
                    'blockchain': 'ETH',
                    'average_fee': float(self.web3.from_wei(avg_gas_price, 'gwei')),
                    'confirmation_time': 15,
                    'transaction_volume': float(total_volume)
                }
            return None
            
        except Exception as e:
            print(f"Erreur lors de la collecte Ethereum: {e}")
            return None