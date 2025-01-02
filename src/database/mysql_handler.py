import mysql.connector
from datetime import datetime

class DatabaseHandler:
    def __init__(self, host, user, password, database, port=8889):
        try:
            self.connection = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database
            )
            self.cursor = self.connection.cursor()
            print("Connexion à la base de données réussie")
        except mysql.connector.Error as err:
            print(f"Erreur de connexion à la base de données: {err}")
            raise
    
    def insert_fee_data(self, data):
        try:
            query = """
            INSERT INTO transaction_fees 
            (symbol, fee, confirmation_time, transaction_volume, timestamp)
            VALUES (%s, %s, %s, %s, NOW())
            """
            values = (
                data['blockchain'],
                data['average_fee'],
                data['confirmation_time'],
                data['transaction_volume']
            )
            
            self.cursor.execute(query, values)
            self.connection.commit()
            print(f"Données {data['blockchain']} insérées avec succès")
        except Exception as e:
            print(f"Erreur lors de l'insertion des données: {e}")
            self.connection.rollback()