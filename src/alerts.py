import pandas as pd
from datetime import datetime, timedelta
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from typing import Dict, List, Optional
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertManager:
    def __init__(self, engine, config: Dict):
        self.engine = engine
        self.config = config
        self.thresholds = {
            'ETH': {
                'critical': 150,  # Gwei
                'warning': 100,   # Gwei
                'spike': 0.3      # 30% augmentation
            },
            'BNB': {
                'critical': 1,    # USD
                'warning': 0.5,   # USD
                'spike': 0.25     # 25% augmentation
            },
            'SOL': {
                'critical': 0.001, # SOL
                'warning': 0.0005, # SOL
                'spike': 0.2      # 20% augmentation
            }
        }

    def check_fee_alerts(self) -> List[Dict]:
        """Vérifie les conditions d'alerte pour les frais"""
        alerts = []
        
        for blockchain in ['ETH', 'BNB', 'SOL']:
            query = f"""
            SELECT 
                fee,
                transaction_volume,
                timestamp
            FROM transaction_fees
            WHERE symbol = '{blockchain}'
            AND timestamp >= NOW() - INTERVAL 1 HOUR
            ORDER BY timestamp DESC
            LIMIT 60
            """
            
            df = pd.read_sql(query, self.engine)
            
            if df.empty:
                continue
                
            current_fee = df['fee'].iloc[0]
            avg_fee = df['fee'].mean()
            
            # Vérification des seuils
            if current_fee > self.thresholds[blockchain]['critical']:
                alerts.append({
                    'blockchain': blockchain,
                    'type': 'CRITICAL',
                    'message': f'Frais critiques sur {blockchain}: {current_fee}',
                    'timestamp': datetime.now().isoformat(),
                    'data': {
                        'current_fee': float(current_fee),
                        'average_fee': float(avg_fee)
                    }
                })
            elif current_fee > self.thresholds[blockchain]['warning']:
                alerts.append({
                    'blockchain': blockchain,
                    'type': 'WARNING',
                    'message': f'Frais élevés sur {blockchain}: {current_fee}',
                    'timestamp': datetime.now().isoformat(),
                    'data': {
                        'current_fee': float(current_fee),
                        'average_fee': float(avg_fee)
                    }
                })
                
            # Vérification des pics
            fee_change = (current_fee - avg_fee) / avg_fee
            if fee_change > self.thresholds[blockchain]['spike']:
                alerts.append({
                    'blockchain': blockchain,
                    'type': 'SPIKE',
                    'message': f'Pic de frais détecté sur {blockchain}: {fee_change:.2%}',
                    'timestamp': datetime.now().isoformat(),
                    'data': {
                        'change_percentage': float(fee_change),
                        'current_fee': float(current_fee),
                        'average_fee': float(avg_fee)
                    }
                })
                
        return alerts

    def send_email_alert(self, alert: Dict):
        """Envoie une alerte par email"""
        try:
            smtp_config = self.config['smtp']
            
            msg = MIMEMultipart()
            msg['From'] = smtp_config['from']
            msg['To'] = smtp_config['to']
            msg['Subject'] = f"Alerte Blockchain - {alert['type']} - {alert['blockchain']}"
            
            body = f"""
            Type d'alerte: {alert['type']}
            Blockchain: {alert['blockchain']}
            Message: {alert['message']}
            Timestamp: {alert['timestamp']}
            
            Données détaillées:
            {json.dumps(alert['data'], indent=2)}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(smtp_config['host'], smtp_config['port']) as server:
                server.starttls()
                server.login(smtp_config['username'], smtp_config['password'])
                server.send_message(msg)
                
            logger.info(f"Email alert sent successfully: {alert['type']} - {alert['blockchain']}")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {str(e)}")

    def send_slack_alert(self, alert: Dict):
        """Envoie une alerte sur Slack"""
        try:
            slack_webhook = self.config['slack_webhook']
            
            message = {
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"🚨 Alerte {alert['type']} - {alert['blockchain']}"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Message:* {alert['message']}\n*Timestamp:* {alert['timestamp']}"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"```{json.dumps(alert['data'], indent=2)}```"
                        }
                    }
                ]
            }
            
            response = requests.post(slack_webhook, json=message)
            response.raise_for_status()
            
            logger.info(f"Slack alert sent successfully: {alert['type']} - {alert['blockchain']}")
            
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {str(e)}")

    def process_alerts(self):
        """Traite et envoie toutes les alertes nécessaires"""
        alerts = self.check_fee_alerts()
        
        for alert in alerts:
            if alert['type'] == 'CRITICAL':
                self.send_email_alert(alert)
                self.send_slack_alert(alert)
            elif alert['type'] in ['WARNING', 'SPIKE']:
                self.send_slack_alert(alert)
            
            self.save_alert(alert)

    def save_alert(self, alert: Dict):
        """Sauvegarde l'alerte dans la base de données"""
        try:
            query = """
            INSERT INTO alerts 
            (blockchain, type, message, timestamp, data)
            VALUES (%(blockchain)s, %(type)s, %(message)s, %(timestamp)s, %(data)s)
            """
            
            with self.engine.connect() as connection:
                connection.execute(query, {
                    'blockchain': alert['blockchain'],
                    'type': alert['type'],
                    'message': alert['message'],
                    'timestamp': alert['timestamp'],
                    'data': json.dumps(alert['data'])
                })
                
            logger.info(f"Alert saved successfully: {alert['type']} - {alert['blockchain']}")
            
        except Exception as e:
            logger.error(f"Failed to save alert: {str(e)}")

    def get_recent_alerts(self, hours: int = 24) -> List[Dict]:
        """Récupère les alertes récentes"""
        query = f"""
        SELECT *
        FROM alerts
        WHERE timestamp >= NOW() - INTERVAL {hours} HOUR
        ORDER BY timestamp DESC
        """
        
        df = pd.read_sql(query, self.engine)
        return df.to_dict('records')

    def update_thresholds(self, new_thresholds: Dict):
        """Met à jour les seuils d'alerte"""
        self.thresholds.update(new_thresholds)
        logger.info("Alert thresholds updated successfully")