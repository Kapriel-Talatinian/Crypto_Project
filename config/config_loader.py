import os
from dotenv import load_dotenv

def load_config():
    # Charge les variables d'environnement depuis config.env
    load_dotenv('config/config.env')
    
    return {
        'DB_HOST': os.getenv('DB_HOST', 'localhost'),
        'DB_PORT': int(os.getenv('DB_PORT', 8889)),
        'DB_USER': os.getenv('DB_USER', 'root'),
        'DB_PASSWORD': os.getenv('DB_PASSWORD', 'root'),
        'DB_NAME': os.getenv('DB_NAME', 'blockchain_analyzer')
    }