import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import TimeSeriesSplit
import joblib
from datetime import datetime, timedelta

class BlockchainFeePredictor:
    def __init__(self, blockchain):
        self.blockchain = blockchain
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=4
        )
        self.scaler = MinMaxScaler()
        self.feature_columns = [
            'hour_sin',
            'hour_cos',
            'day_sin',
            'day_cos',
            'transaction_volume_normalized',
            'moving_avg_1h',
            'moving_avg_24h'
        ]

    def _create_cyclical_features(self, df):
        """Crée des features cycliques pour le temps"""
        df['hour_sin'] = np.sin(2 * np.pi * df['timestamp'].dt.hour/24)
        df['hour_cos'] = np.cos(2 * np.pi * df['timestamp'].dt.hour/24)
        df['day_sin'] = np.sin(2 * np.pi * df['timestamp'].dt.dayofweek/7)
        df['day_cos'] = np.cos(2 * np.pi * df['timestamp'].dt.dayofweek/7)
        return df

    def _create_volume_features(self, df):
        """Crée des features basées sur le volume"""
        df['transaction_volume_normalized'] = self.scaler.fit_transform(
            df[['transaction_volume']]
        )
        df['moving_avg_1h'] = df['average_fee'].rolling(window=6).mean()
        df['moving_avg_24h'] = df['average_fee'].rolling(window=144).mean()
        df = df.fillna(method='bfill')
        return df

    def prepare_data(self, df):
        """Prépare les données pour l'entraînement"""
        df = df.copy()
        df = self._create_cyclical_features(df)
        df = self._create_volume_features(df)
        return df

    def train(self, df):
        """Entraîne le modèle"""
        prepared_data = self.prepare_data(df)
        X = prepared_data[self.feature_columns]
        y = prepared_data['average_fee']

        # Utilisation de TimeSeriesSplit pour la validation
        tscv = TimeSeriesSplit(n_splits=5)
        for train_index, val_index in tscv.split(X):
            X_train, X_val = X.iloc[train_index], X.iloc[val_index]
            y_train, y_val = y.iloc[train_index], y.iloc[val_index]
            self.model.fit(X_train, y_train)

        return self.model.score(X_val, y_val)

    def predict_next_week(self, current_data):
        """Prédit les frais pour la semaine suivante"""
        last_timestamp = current_data['timestamp'].max()
        future_dates = pd.date_range(
            start=last_timestamp,
            periods=24*7,  # 7 jours
            freq='H'
        )

        # Création du DataFrame pour les prédictions
        future_df = pd.DataFrame({'timestamp': future_dates})
        future_df['transaction_volume'] = current_data['transaction_volume'].mean()
        
        # Préparation des données futures
        prepared_future = self.prepare_data(future_df)
        predictions = self.model.predict(prepared_future[self.feature_columns])

        return pd.Series(predictions, index=future_dates)

    def find_optimal_times(self, predictions, n_best=5):
        """Trouve les meilleurs moments pour les transactions"""
        best_times = predictions.nsmallest(n_best)
        return {
            'timestamps': best_times.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
            'fees': best_times.values.tolist()
        }

    def analyze_patterns(self, df):
        """Analyse les patterns de frais"""
        prepared_data = self.prepare_data(df)
        
        # Analyse par heure
        hourly_analysis = df.groupby(df['timestamp'].dt.hour)['average_fee'].agg([
            'mean', 'std', 'min', 'max'
        ]).round(4)

        # Analyse par jour de la semaine
        daily_analysis = df.groupby(df['timestamp'].dt.dayofweek)['average_fee'].agg([
            'mean', 'std', 'min', 'max'
        ]).round(4)

        # Détection des périodes de congestion
        congestion_threshold = df['average_fee'].quantile(0.75)
        high_congestion_periods = df[df['average_fee'] > congestion_threshold]

        return {
            'hourly_patterns': hourly_analysis.to_dict(),
            'daily_patterns': daily_analysis.to_dict(),
            'congestion_periods': {
                'threshold': float(congestion_threshold),
                'high_congestion_hours': high_congestion_periods['timestamp'].dt.hour.value_counts().to_dict()
            }
        }

    def save_model(self, path):
        """Sauvegarde le modèle"""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler
        }, path)

    def load_model(self, path):
        """Charge le modèle"""
        saved_model = joblib.load(path)
        self.model = saved_model['model']
        self.scaler = saved_model['scaler']