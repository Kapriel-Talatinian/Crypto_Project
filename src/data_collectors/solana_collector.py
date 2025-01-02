import requests

class SolanaCollector:
    def __init__(self):
        self.api_url = "https://api.binance.com/api/v3"

    def get_gas_prices(self):
        try:
            response = requests.get(f"{self.api_url}/ticker/price?symbol=SOLUSDT")
            if response.status_code == 200:
                sol_price = float(response.json()['price'])
                
                # Frais moyens Solana
                base_fee = 0.000005
                fee_in_usd = base_fee * sol_price

                return {
                    'blockchain': 'SOL',
                    'average_fee': fee_in_usd,
                    'confirmation_time': 1,
                    'transaction_volume': sol_price
                }
            return None
        except Exception as e:
            print(f"Erreur lors de la collecte Solana: {e}")
            return None