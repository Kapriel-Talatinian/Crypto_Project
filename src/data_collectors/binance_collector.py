import requests

class BinanceCollector:
    def __init__(self):
        self.api_url = "https://api.binance.com/api/v3"

    def get_gas_prices(self):
        try:
            response = requests.get(f"{self.api_url}/ticker/price?symbol=BNBUSDT")
            if response.status_code == 200:
                bnb_price = float(response.json()['price'])
                
                # Frais moyens BSC
                base_fee = 0.0003
                fee_in_usd = base_fee * bnb_price

                return {
                    'blockchain': 'BNB',
                    'average_fee': fee_in_usd,
                    'confirmation_time': 3,
                    'transaction_volume': bnb_price
                }
            return None
        except Exception as e:
            print(f"Erreur lors de la collecte Binance: {e}")
            return None