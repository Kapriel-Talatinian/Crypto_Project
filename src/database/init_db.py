import mysql.connector
from config.config_loader import load_config

def init_database():
    config = load_config()
    
    try:
        connection = mysql.connector.connect(
            host=config['DB_HOST'],
            port=config['DB_PORT'],
            user=config['DB_USER'],
            password=config['DB_PASSWORD']
        )
        cursor = connection.cursor()
        
        # Créer la base de données avec le bon nom
        cursor.execute("CREATE DATABASE IF NOT EXISTS blockchain_fees")
        cursor.execute("USE blockchain_fees")
        
        # Créer la table transaction_fees
        create_table_query = """
        CREATE TABLE IF NOT EXISTS transaction_fees (
            id INT AUTO_INCREMENT PRIMARY KEY,
            symbol VARCHAR(10) NOT NULL,
            fee DECIMAL(18,8) NOT NULL,
            confirmation_time INT,
            transaction_volume DECIMAL(18,8),
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        print("Base de données initialisée avec succès")
        
    except mysql.connector.Error as err:
        print(f"Erreur lors de l'initialisation de la base de données: {err}")
        raise
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    init_database()